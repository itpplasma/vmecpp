// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT
#include "vmecpp/vmec/boozer/boozer.h"

#include <cmath>
#include <cstdlib>
#include <string>
#include <utility>
#include <vector>

#include "absl/status/status.h"
#include "absl/strings/str_format.h"

namespace vmecpp {

namespace {

using Eigen::ArrayXd;
using Eigen::VectorXd;

Eigen::VectorXd ToDouble(const std::vector<int>& v) {
  Eigen::VectorXd out(v.size());
  for (std::size_t i = 0; i < v.size(); ++i) {
    out[i] = v[i];
  }
  return out;
}

// cos/sin(m theta - n zeta) for the modes (xm, xn) on the points (theta, zeta).
void Harmonics(const VectorXd& theta, const VectorXd& zeta,
               const std::vector<int>& xm, const std::vector<int>& xn,
               RowMatrixXd& cos_mn, RowMatrixXd& sin_mn) {
  const int n_points = static_cast<int>(theta.size());
  const int n_modes = static_cast<int>(xm.size());
  cos_mn.resize(n_points, n_modes);
  sin_mn.resize(n_points, n_modes);
  for (int j = 0; j < n_points; ++j) {
    for (int k = 0; k < n_modes; ++k) {
      const double angle = xm[k] * theta[j] - xn[k] * zeta[j];
      cos_mn(j, k) = std::cos(angle);
      sin_mn(j, k) = std::sin(angle);
    }
  }
}

}  // namespace

// Synthesized fields of one surface on the VMEC grid.
struct BoozerTransform::GridArrays {
  VectorXd r, z, lambda, lambda_t, lambda_z;
  VectorXd w, w_t, w_z, b;
  double boozer_i = 0.0;
  double boozer_g = 0.0;
  double iota = 0.0;
};

// The primal state of one surface, kept for the tangent and the adjoint.
struct BoozerTransform::Surface {
  GridArrays grid;
  double d = 0.0;  // G + iota I
  VectorXd nu, nu_t, nu_z;
  VectorXd theta_b, zeta_b;
  VectorXd jacobian;         // d(theta_B, zeta_B) / d(theta, zeta)
  VectorXd boozer_jacobian;  // (G + iota I) / B^2
  VectorXd weighted;         // quadrature weight times jacobian
  RowMatrixXd cos_b, sin_b;  // [n_grid x mnboz]
};

absl::StatusOr<BoozerTransform> BoozerTransform::Create(
    int nfp, int ns, const std::vector<int>& xm, const std::vector<int>& xn,
    const std::vector<int>& xm_nyq, const std::vector<int>& xn_nyq,
    const std::vector<int>& surfaces, int mboz, int nboz) {
  if (nfp < 1) {
    return absl::InvalidArgumentError("nfp must be at least 1");
  }
  if (ns < 3) {
    return absl::InvalidArgumentError(
        "the Boozer transform needs at least 3 radial surfaces");
  }
  if (mboz < 2 || nboz < 0) {
    return absl::InvalidArgumentError("need mboz >= 2 and nboz >= 0");
  }
  if (xm.size() != xn.size() || xm_nyq.size() != xn_nyq.size() || xm.empty() ||
      xm_nyq.empty()) {
    return absl::InvalidArgumentError("inconsistent mode tables");
  }
  for (const int j : surfaces) {
    if (j < 0 || j >= ns - 1) {
      return absl::InvalidArgumentError(absl::StrFormat(
          "surface index %d is outside the half grid [0, %d)", j, ns - 1));
    }
  }
  const auto count_origin = [](const std::vector<int>& m,
                               const std::vector<int>& n) {
    int count = 0;
    for (std::size_t k = 0; k < m.size(); ++k) {
      count += (m[k] == 0 && n[k] == 0) ? 1 : 0;
    }
    return count;
  };
  if (count_origin(xm_nyq, xn_nyq) != 1) {
    return absl::InvalidArgumentError(
        "the Nyquist mode table must contain (m, n) = (0, 0) exactly once");
  }

  BoozerTransform t;
  t.nfp_ = nfp;
  t.ns_ = ns;
  t.mboz_ = mboz;
  t.nboz_ = nboz;
  t.xm_ = xm;
  t.xn_ = xn;
  t.xm_nyq_ = xm_nyq;
  t.xn_nyq_ = xn_nyq;
  t.surfaces_ = surfaces;

  // Grid and mode table of booz_xform's init().
  t.ntheta_ = 2 * (2 * mboz + 1);
  t.nzeta_ = nboz == 0 ? 1 : 2 * (2 * nboz + 1);
  t.nu2_b_ = t.ntheta_ / 2 + 1;
  t.n_grid_ = t.nu2_b_ * t.nzeta_;
  for (int m = 0; m <= mboz - 1; ++m) {
    for (int n = (m == 0 ? 0 : -nboz); n <= nboz; ++n) {
      t.xm_b_.push_back(m);
      t.xn_b_.push_back(n * nfp);
    }
  }

  const double d_theta = 2.0 * M_PI / t.ntheta_;
  const double d_zeta = 2.0 * M_PI / (nfp * t.nzeta_);
  t.theta_.resize(t.n_grid_);
  t.zeta_.resize(t.n_grid_);
  t.weight_.setOnes(t.n_grid_);
  for (int i = 0; i < t.nu2_b_; ++i) {
    for (int k = 0; k < t.nzeta_; ++k) {
      const int index = i * t.nzeta_ + k;
      t.theta_[index] = i * d_theta;
      t.zeta_[index] = k * d_zeta;
      if (i == 0 || i == t.nu2_b_ - 1) {
        t.weight_[index] = 0.5;
      }
    }
  }

  Harmonics(t.theta_, t.zeta_, xm, xn, t.cos_grid_, t.sin_grid_);
  Harmonics(t.theta_, t.zeta_, xm_nyq, xn_nyq, t.cos_grid_nyq_,
            t.sin_grid_nyq_);

  t.m_ = ToDouble(xm);
  t.n_ = ToDouble(xn);
  t.m_nyq_ = ToDouble(xm_nyq);
  t.n_nyq_ = ToDouble(xn_nyq);
  t.m_b_ = ToDouble(t.xm_b_);
  t.n_b_ = ToDouble(t.xn_b_);

  t.fourier_factor_ = 2.0 / ((t.nu2_b_ - 1) * t.nzeta_);
  t.normalization_b_.setConstant(t.xm_b_.size(), t.fourier_factor_);
  t.normalization_b_[0] *= 0.5;
  return t;
}

Eigen::VectorXd BoozerTransform::s_b() const {
  VectorXd s(surfaces_.size());
  for (std::size_t i = 0; i < surfaces_.size(); ++i) {
    s[i] = (surfaces_[i] + 0.5) / (ns_ - 1.0);
  }
  return s;
}

absl::Status BoozerTransform::CheckInput(
    const BoozerInputSpectra& input) const {
  const auto check = [&](const RowMatrixXd& a, std::size_t rows,
                         const char* name) -> absl::Status {
    if (a.rows() != static_cast<Eigen::Index>(rows) || a.cols() != ns_) {
      return absl::InvalidArgumentError(
          absl::StrFormat("%s has shape (%d, %d), expected (%d, %d)", name,
                          a.rows(), a.cols(), rows, ns_));
    }
    return absl::OkStatus();
  };
  for (const auto& status :
       {check(input.rmnc, xm_.size(), "rmnc"),
        check(input.zmns, xm_.size(), "zmns"),
        check(input.lmns, xm_.size(), "lmns"),
        check(input.bmnc, xm_nyq_.size(), "bmnc"),
        check(input.bsubumnc, xm_nyq_.size(), "bsubumnc"),
        check(input.bsubvmnc, xm_nyq_.size(), "bsubvmnc")}) {
    if (!status.ok()) {
      return status;
    }
  }
  if (input.iotas.size() != ns_) {
    return absl::InvalidArgumentError("iotas must have ns entries");
  }
  return absl::OkStatus();
}

absl::Status BoozerTransform::CheckOutput(
    const BoozerOutputSpectra& output) const {
  const Eigen::Index n_modes = static_cast<Eigen::Index>(xm_b_.size());
  const Eigen::Index n_surfaces = static_cast<Eigen::Index>(surfaces_.size());
  for (const RowMatrixXd* a : {&output.bmnc_b, &output.rmnc_b, &output.zmns_b,
                               &output.numns_b, &output.gmnc_b}) {
    if (a->rows() != n_modes || a->cols() != n_surfaces) {
      return absl::InvalidArgumentError(absl::StrFormat(
          "Boozer spectra must have shape (%d, %d)", n_modes, n_surfaces));
    }
  }
  for (const VectorXd* v :
       {&output.iota_b, &output.boozer_g, &output.boozer_i}) {
    if (v->size() != n_surfaces) {
      return absl::InvalidArgumentError(
          "iota_b, boozer_g and boozer_i must have one entry per surface");
    }
  }
  return absl::OkStatus();
}

std::vector<BoozerTransform::Stencil> BoozerTransform::RadialStencil(
    int mode, int j) const {
  const int m = xm_[mode];
  if (m % 2 == 0) {
    return {{j, 0.5}, {j + 1, 0.5}};
  }
  const double hs = 1.0 / (ns_ - 1.0);
  const auto sqrt_s_full = [&](int k) {
    return k == 0 ? 1.0 : std::sqrt(hs * k);
  };
  const double sqrt_s_half = std::sqrt(hs * (j + 0.5));
  if (m == 1 && j == 0) {
    return {{1, 1.5 * sqrt_s_half / sqrt_s_full(1)},
            {2, -0.5 * sqrt_s_half / sqrt_s_full(2)}};
  }
  return {{j, 0.5 * sqrt_s_half / sqrt_s_full(j)},
          {j + 1, 0.5 * sqrt_s_half / sqrt_s_full(j + 1)}};
}

Eigen::VectorXd BoozerTransform::HalfGridGeometry(const RowMatrixXd& full,
                                                  int j) const {
  VectorXd half(xm_.size());
  for (int mode = 0; mode < static_cast<int>(xm_.size()); ++mode) {
    double value = 0.0;
    for (const Stencil& s : RadialStencil(mode, j)) {
      value += s.weight * full(mode, s.full_index);
    }
    half[mode] = value;
  }
  return half;
}

void BoozerTransform::AccumulateHalfGridGeometryAdjoint(
    const Eigen::VectorXd& half_bar, int j, RowMatrixXd& full_bar) const {
  for (int mode = 0; mode < static_cast<int>(xm_.size()); ++mode) {
    for (const Stencil& s : RadialStencil(mode, j)) {
      full_bar(mode, s.full_index) += s.weight * half_bar[mode];
    }
  }
}

// Linear in `input`, so it also maps a tangent to the tangent grid arrays.
BoozerTransform::GridArrays BoozerTransform::Synthesize(
    const BoozerInputSpectra& input, int j) const {
  const int column = j + 1;  // half-grid column of surface j
  GridArrays g;
  const VectorXd r_half = HalfGridGeometry(input.rmnc, j);
  const VectorXd z_half = HalfGridGeometry(input.zmns, j);
  const VectorXd lambda = input.lmns.col(column);
  g.r = cos_grid_ * r_half;
  g.z = sin_grid_ * z_half;
  g.lambda = sin_grid_ * lambda;
  g.lambda_t = cos_grid_ * m_.cwiseProduct(lambda);
  g.lambda_z = -(cos_grid_ * n_.cwiseProduct(lambda));

  // Periodic part of the scalar potential, booz_xform's transpmn.
  VectorXd wmns = VectorXd::Zero(xm_nyq_.size());
  for (int k = 0; k < static_cast<int>(xm_nyq_.size()); ++k) {
    if (xm_nyq_[k] != 0) {
      wmns[k] = input.bsubumnc(k, column) / xm_nyq_[k];
    } else if (xn_nyq_[k] != 0) {
      wmns[k] = -input.bsubvmnc(k, column) / xn_nyq_[k];
    } else {
      g.boozer_i = input.bsubumnc(k, column);
      g.boozer_g = input.bsubvmnc(k, column);
    }
  }
  g.w = sin_grid_nyq_ * wmns;
  g.w_t = cos_grid_nyq_ * m_nyq_.cwiseProduct(wmns);
  g.w_z = -(cos_grid_nyq_ * n_nyq_.cwiseProduct(wmns));
  g.b = cos_grid_nyq_ * input.bmnc.col(column);
  g.iota = input.iotas[column];
  return g;
}

void BoozerTransform::BoozerHarmonics(const VectorXd& theta_b,
                                      const VectorXd& zeta_b,
                                      RowMatrixXd& cos_b,
                                      RowMatrixXd& sin_b) const {
  // Angle-addition recursion as in booz_xform's init_trig.
  const int n_m = mboz_ + 1;
  const int n_n = nboz_ + 1;
  RowMatrixXd cos_m(n_grid_, n_m), sin_m(n_grid_, n_m);
  RowMatrixXd cos_n(n_grid_, n_n), sin_n(n_grid_, n_n);
  for (int j = 0; j < n_grid_; ++j) {
    cos_m(j, 0) = 1.0;
    sin_m(j, 0) = 0.0;
    cos_m(j, 1) = std::cos(theta_b[j]);
    sin_m(j, 1) = std::sin(theta_b[j]);
    for (int m = 2; m < n_m; ++m) {
      cos_m(j, m) =
          cos_m(j, m - 1) * cos_m(j, 1) - sin_m(j, m - 1) * sin_m(j, 1);
      sin_m(j, m) =
          sin_m(j, m - 1) * cos_m(j, 1) + cos_m(j, m - 1) * sin_m(j, 1);
    }
    cos_n(j, 0) = 1.0;
    sin_n(j, 0) = 0.0;
    if (n_n > 1) {
      cos_n(j, 1) = std::cos(nfp_ * zeta_b[j]);
      sin_n(j, 1) = std::sin(nfp_ * zeta_b[j]);
    }
    for (int n = 2; n < n_n; ++n) {
      cos_n(j, n) =
          cos_n(j, n - 1) * cos_n(j, 1) - sin_n(j, n - 1) * sin_n(j, 1);
      sin_n(j, n) =
          sin_n(j, n - 1) * cos_n(j, 1) + cos_n(j, n - 1) * sin_n(j, 1);
    }
  }
  const int mnboz = static_cast<int>(xm_b_.size());
  cos_b.resize(n_grid_, mnboz);
  sin_b.resize(n_grid_, mnboz);
  for (int k = 0; k < mnboz; ++k) {
    const int m = xm_b_[k];
    const int abs_n = std::abs(xn_b_[k] / nfp_);
    const double sign = xn_b_[k] < 0 ? -1.0 : 1.0;
    for (int j = 0; j < n_grid_; ++j) {
      cos_b(j, k) =
          cos_m(j, m) * cos_n(j, abs_n) + sign * sin_m(j, m) * sin_n(j, abs_n);
      sin_b(j, k) =
          sin_m(j, m) * cos_n(j, abs_n) - sign * cos_m(j, m) * sin_n(j, abs_n);
    }
  }
}

BoozerTransform::Surface BoozerTransform::Solve(const BoozerInputSpectra& input,
                                                int j) const {
  Surface s;
  s.grid = Synthesize(input, j);
  const GridArrays& g = s.grid;
  s.d = g.boozer_g + g.iota * g.boozer_i;
  s.nu = (g.w - g.boozer_i * g.lambda) / s.d;
  s.nu_t = (g.w_t - g.boozer_i * g.lambda_t) / s.d;
  s.nu_z = (g.w_z - g.boozer_i * g.lambda_z) / s.d;
  s.theta_b = theta_ + g.lambda + g.iota * s.nu;
  s.zeta_b = zeta_ + s.nu;
  s.jacobian = ((1.0 + g.lambda_t.array()) * (1.0 + s.nu_z.array()) +
                (g.iota - g.lambda_z.array()) * s.nu_t.array())
                   .matrix();
  s.boozer_jacobian = (s.d / g.b.array().square()).matrix();
  s.weighted = weight_.cwiseProduct(s.jacobian);
  BoozerHarmonics(s.theta_b, s.zeta_b, s.cos_b, s.sin_b);
  return s;
}

absl::StatusOr<BoozerOutputSpectra> BoozerTransform::Forward(
    const BoozerInputSpectra& input) const {
  if (absl::Status status = CheckInput(input); !status.ok()) {
    return status;
  }
  const int mnboz = static_cast<int>(xm_b_.size());
  const int n_surfaces = static_cast<int>(surfaces_.size());
  BoozerOutputSpectra out;
  for (RowMatrixXd* a :
       {&out.bmnc_b, &out.rmnc_b, &out.zmns_b, &out.numns_b, &out.gmnc_b}) {
    a->setZero(mnboz, n_surfaces);
  }
  out.iota_b.setZero(n_surfaces);
  out.boozer_g.setZero(n_surfaces);
  out.boozer_i.setZero(n_surfaces);

#pragma omp parallel for schedule(dynamic)
  for (int i = 0; i < n_surfaces; ++i) {
    const Surface s = Solve(input, surfaces_[i]);
    const auto project = [&](const RowMatrixXd& basis, const VectorXd& q) {
      return normalization_b_.cwiseProduct(basis.transpose() *
                                           s.weighted.cwiseProduct(q));
    };
    out.bmnc_b.col(i) = project(s.cos_b, s.grid.b);
    out.rmnc_b.col(i) = project(s.cos_b, s.grid.r);
    out.zmns_b.col(i) = project(s.sin_b, s.grid.z);
    out.numns_b.col(i) = project(s.sin_b, s.nu);
    out.gmnc_b.col(i) = project(s.cos_b, s.boozer_jacobian);
    out.iota_b[i] = s.grid.iota;
    out.boozer_g[i] = s.grid.boozer_g;
    out.boozer_i[i] = s.grid.boozer_i;
  }
  return out;
}

absl::StatusOr<BoozerOutputSpectra> BoozerTransform::Jvp(
    const BoozerInputSpectra& input, const BoozerInputSpectra& tangent) const {
  if (absl::Status status = CheckInput(input); !status.ok()) {
    return status;
  }
  if (absl::Status status = CheckInput(tangent); !status.ok()) {
    return status;
  }
  const int mnboz = static_cast<int>(xm_b_.size());
  const int n_surfaces = static_cast<int>(surfaces_.size());
  BoozerOutputSpectra out;
  for (RowMatrixXd* a :
       {&out.bmnc_b, &out.rmnc_b, &out.zmns_b, &out.numns_b, &out.gmnc_b}) {
    a->setZero(mnboz, n_surfaces);
  }
  out.iota_b.setZero(n_surfaces);
  out.boozer_g.setZero(n_surfaces);
  out.boozer_i.setZero(n_surfaces);

#pragma omp parallel for schedule(dynamic)
  for (int i = 0; i < n_surfaces; ++i) {
    const int j = surfaces_[i];
    const Surface s = Solve(input, j);
    const GridArrays& g = s.grid;
    const GridArrays dg = Synthesize(tangent, j);

    const double d_d =
        dg.boozer_g + dg.iota * g.boozer_i + g.iota * dg.boozer_i;
    const ArrayXd d_nu = (dg.w.array() - dg.boozer_i * g.lambda.array() -
                          g.boozer_i * dg.lambda.array() - s.nu.array() * d_d) /
                         s.d;
    const ArrayXd d_nu_t =
        (dg.w_t.array() - dg.boozer_i * g.lambda_t.array() -
         g.boozer_i * dg.lambda_t.array() - s.nu_t.array() * d_d) /
        s.d;
    const ArrayXd d_nu_z =
        (dg.w_z.array() - dg.boozer_i * g.lambda_z.array() -
         g.boozer_i * dg.lambda_z.array() - s.nu_z.array() * d_d) /
        s.d;
    const ArrayXd d_theta_b =
        dg.lambda.array() + dg.iota * s.nu.array() + g.iota * d_nu;
    const ArrayXd& d_zeta_b = d_nu;
    const ArrayXd d_jacobian =
        dg.lambda_t.array() * (1.0 + s.nu_z.array()) +
        (1.0 + g.lambda_t.array()) * d_nu_z +
        (dg.iota - dg.lambda_z.array()) * s.nu_t.array() +
        (g.iota - g.lambda_z.array()) * d_nu_t;
    const ArrayXd b = g.b.array();
    const ArrayXd d_boozer_jacobian =
        d_d / b.square() - 2.0 * s.d * dg.b.array() / (b.square() * b);
    const ArrayXd d_weighted = weight_.array() * d_jacobian;
    const ArrayXd a = s.weighted.array();

    // Tangent of normalization * sum_j a_j q_j basis_k(theta_B, zeta_B).
    const auto tangent_of = [&](const VectorXd& q, const ArrayXd& d_q,
                                bool cosine) -> VectorXd {
      const ArrayXd aq = a * q.array();
      const VectorXd amplitude = (d_weighted * q.array() + a * d_q).matrix();
      const VectorXd shift_theta = (aq * d_theta_b).matrix();
      const VectorXd shift_zeta = (aq * d_zeta_b).matrix();
      VectorXd result;
      if (cosine) {
        result = s.cos_b.transpose() * amplitude -
                 m_b_.cwiseProduct(s.sin_b.transpose() * shift_theta) +
                 n_b_.cwiseProduct(s.sin_b.transpose() * shift_zeta);
      } else {
        result = s.sin_b.transpose() * amplitude +
                 m_b_.cwiseProduct(s.cos_b.transpose() * shift_theta) -
                 n_b_.cwiseProduct(s.cos_b.transpose() * shift_zeta);
      }
      return normalization_b_.cwiseProduct(result);
    };
    out.bmnc_b.col(i) = tangent_of(g.b, dg.b.array(), true);
    out.rmnc_b.col(i) = tangent_of(g.r, dg.r.array(), true);
    out.zmns_b.col(i) = tangent_of(g.z, dg.z.array(), false);
    out.numns_b.col(i) = tangent_of(s.nu, d_nu, false);
    out.gmnc_b.col(i) = tangent_of(s.boozer_jacobian, d_boozer_jacobian, true);
    out.iota_b[i] = dg.iota;
    out.boozer_g[i] = dg.boozer_g;
    out.boozer_i[i] = dg.boozer_i;
  }
  return out;
}

absl::StatusOr<BoozerInputSpectra> BoozerTransform::Vjp(
    const BoozerInputSpectra& input,
    const BoozerOutputSpectra& cotangent) const {
  if (absl::Status status = CheckInput(input); !status.ok()) {
    return status;
  }
  if (absl::Status status = CheckOutput(cotangent); !status.ok()) {
    return status;
  }
  const int n_surfaces = static_cast<int>(surfaces_.size());
  const int mnmax = static_cast<int>(xm_.size());
  const int mnmax_nyq = static_cast<int>(xm_nyq_.size());

  // Per-surface cotangents of the half-grid coefficients; they are folded
  // into the shared result after the parallel loop.
  struct SurfaceCotangent {
    VectorXd r_half, z_half, lambda, bmnc, bsubumnc, bsubvmnc;
    double iota = 0.0;
  };
  std::vector<SurfaceCotangent> per_surface(n_surfaces);

#pragma omp parallel for schedule(dynamic)
  for (int i = 0; i < n_surfaces; ++i) {
    const Surface s = Solve(input, surfaces_[i]);
    const GridArrays& g = s.grid;
    const ArrayXd a = s.weighted.array();

    ArrayXd a_bar = ArrayXd::Zero(n_grid_);
    ArrayXd theta_b_bar = ArrayXd::Zero(n_grid_);
    ArrayXd zeta_b_bar = ArrayXd::Zero(n_grid_);

    // Adjoint of normalization * sum_j a_j q_j basis_k(theta_B, zeta_B):
    // returns the cotangent of q and accumulates those of a and the angles.
    const auto pull_back = [&](const VectorXd& q, const RowMatrixXd& out_bar,
                               bool cosine) -> ArrayXd {
      const VectorXd u = normalization_b_.cwiseProduct(out_bar.col(i));
      const ArrayXd aq = a * q.array();
      ArrayXd p_bar;
      if (cosine) {
        p_bar = (s.cos_b * u).array();
        theta_b_bar -= aq * (s.sin_b * m_b_.cwiseProduct(u)).array();
        zeta_b_bar += aq * (s.sin_b * n_b_.cwiseProduct(u)).array();
      } else {
        p_bar = (s.sin_b * u).array();
        theta_b_bar += aq * (s.cos_b * m_b_.cwiseProduct(u)).array();
        zeta_b_bar -= aq * (s.cos_b * n_b_.cwiseProduct(u)).array();
      }
      a_bar += p_bar * q.array();
      return p_bar * a;
    };
    ArrayXd b_bar = pull_back(g.b, cotangent.bmnc_b, true);
    const ArrayXd r_bar = pull_back(g.r, cotangent.rmnc_b, true);
    const ArrayXd z_bar = pull_back(g.z, cotangent.zmns_b, false);
    ArrayXd nu_bar = pull_back(s.nu, cotangent.numns_b, false);
    const ArrayXd boozer_jacobian_bar =
        pull_back(s.boozer_jacobian, cotangent.gmnc_b, true);

    double iota_bar = cotangent.iota_b[i];
    double boozer_g_bar = cotangent.boozer_g[i];
    double boozer_i_bar = cotangent.boozer_i[i];
    double d_bar = 0.0;

    // boozer_jacobian = d / b^2
    const ArrayXd b = g.b.array();
    d_bar += (boozer_jacobian_bar / b.square()).sum();
    b_bar -= 2.0 * s.d * boozer_jacobian_bar / (b.square() * b);

    // weighted = weight * jacobian, jacobian = (1 + lambda_t)(1 + nu_z)
    //                                        + (iota - lambda_z) nu_t
    const ArrayXd jacobian_bar = weight_.array() * a_bar;
    ArrayXd lambda_t_bar = jacobian_bar * (1.0 + s.nu_z.array());
    ArrayXd nu_z_bar = jacobian_bar * (1.0 + g.lambda_t.array());
    iota_bar += (jacobian_bar * s.nu_t.array()).sum();
    ArrayXd lambda_z_bar = -jacobian_bar * s.nu_t.array();
    const ArrayXd nu_t_bar = jacobian_bar * (g.iota - g.lambda_z.array());

    // theta_B = theta + lambda + iota nu, zeta_B = zeta + nu
    ArrayXd lambda_bar = theta_b_bar;
    iota_bar += (theta_b_bar * s.nu.array()).sum();
    nu_bar += g.iota * theta_b_bar + zeta_b_bar;

    // nu = (w - I lambda) / d, and likewise for the theta and zeta derivatives.
    const auto pull_back_nu = [&](const ArrayXd& nu_x_bar, const VectorXd& nu_x,
                                  const VectorXd& lambda_x,
                                  ArrayXd& lambda_x_bar) -> ArrayXd {
      boozer_i_bar -= (nu_x_bar * lambda_x.array()).sum() / s.d;
      lambda_x_bar -= g.boozer_i * nu_x_bar / s.d;
      d_bar -= (nu_x_bar * nu_x.array()).sum() / s.d;
      return nu_x_bar / s.d;
    };
    const ArrayXd w_bar = pull_back_nu(nu_bar, s.nu, g.lambda, lambda_bar);
    const ArrayXd w_t_bar =
        pull_back_nu(nu_t_bar, s.nu_t, g.lambda_t, lambda_t_bar);
    const ArrayXd w_z_bar =
        pull_back_nu(nu_z_bar, s.nu_z, g.lambda_z, lambda_z_bar);

    // d = G + iota I
    boozer_g_bar += d_bar;
    iota_bar += d_bar * g.boozer_i;
    boozer_i_bar += d_bar * g.iota;

    // Transposed synthesis.
    SurfaceCotangent& c = per_surface[i];
    c.r_half = cos_grid_.transpose() * r_bar.matrix();
    c.z_half = sin_grid_.transpose() * z_bar.matrix();
    c.lambda = sin_grid_.transpose() * lambda_bar.matrix() +
               m_.cwiseProduct(cos_grid_.transpose() * lambda_t_bar.matrix()) -
               n_.cwiseProduct(cos_grid_.transpose() * lambda_z_bar.matrix());
    const VectorXd wmns_bar =
        sin_grid_nyq_.transpose() * w_bar.matrix() +
        m_nyq_.cwiseProduct(cos_grid_nyq_.transpose() * w_t_bar.matrix()) -
        n_nyq_.cwiseProduct(cos_grid_nyq_.transpose() * w_z_bar.matrix());
    c.bmnc = cos_grid_nyq_.transpose() * b_bar.matrix();
    c.bsubumnc.setZero(mnmax_nyq);
    c.bsubvmnc.setZero(mnmax_nyq);
    for (int k = 0; k < mnmax_nyq; ++k) {
      if (xm_nyq_[k] != 0) {
        c.bsubumnc[k] = wmns_bar[k] / xm_nyq_[k];
      } else if (xn_nyq_[k] != 0) {
        c.bsubvmnc[k] = -wmns_bar[k] / xn_nyq_[k];
      } else {
        c.bsubumnc[k] = boozer_i_bar;
        c.bsubvmnc[k] = boozer_g_bar;
      }
    }
    c.iota = iota_bar;
  }

  BoozerInputSpectra bar;
  bar.rmnc.setZero(mnmax, ns_);
  bar.zmns.setZero(mnmax, ns_);
  bar.lmns.setZero(mnmax, ns_);
  bar.bmnc.setZero(mnmax_nyq, ns_);
  bar.bsubumnc.setZero(mnmax_nyq, ns_);
  bar.bsubvmnc.setZero(mnmax_nyq, ns_);
  bar.iotas.setZero(ns_);
  for (int i = 0; i < n_surfaces; ++i) {
    const int j = surfaces_[i];
    const int column = j + 1;
    const SurfaceCotangent& c = per_surface[i];
    AccumulateHalfGridGeometryAdjoint(c.r_half, j, bar.rmnc);
    AccumulateHalfGridGeometryAdjoint(c.z_half, j, bar.zmns);
    bar.lmns.col(column) += c.lambda;
    bar.bmnc.col(column) += c.bmnc;
    bar.bsubumnc.col(column) += c.bsubumnc;
    bar.bsubvmnc.col(column) += c.bsubvmnc;
    bar.iotas[column] += c.iota;
  }
  return bar;
}

}  // namespace vmecpp
