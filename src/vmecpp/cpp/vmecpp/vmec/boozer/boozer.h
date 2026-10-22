// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT
#ifndef VMECPP_VMEC_BOOZER_BOOZER_H_
#define VMECPP_VMEC_BOOZER_BOOZER_H_

#include <Eigen/Dense>
#include <vector>

#include "absl/status/statusor.h"
#include "vmecpp/common/util/util.h"

namespace vmecpp {

// The stellarator-symmetric wout spectra that the Boozer transform consumes,
// in the layout of the Python VmecWOut, with one row per Fourier mode and one
// column per radial surface. rmnc and zmns live on the full radial grid,
// lmns, bmnc, bsubumnc, bsubvmnc and iotas on the half grid, whose column 0 is
// the unused axis entry. The same struct carries tangents and cotangents.
struct BoozerInputSpectra {
  RowMatrixXd rmnc;       // [mnmax x ns]
  RowMatrixXd zmns;       // [mnmax x ns]
  RowMatrixXd lmns;       // [mnmax x ns]
  RowMatrixXd bmnc;       // [mnmax_nyq x ns]
  RowMatrixXd bsubumnc;   // [mnmax_nyq x ns]
  RowMatrixXd bsubvmnc;   // [mnmax_nyq x ns]
  Eigen::VectorXd iotas;  // [ns]
};

// Boozer spectra on the selected half-grid surfaces, one column per surface
// and one row per Boozer mode (xm_b, xn_b), together with iota, G = B_zeta
// and I = B_theta on those surfaces. The same struct carries tangents and
// cotangents.
struct BoozerOutputSpectra {
  RowMatrixXd bmnc_b;        // [mnboz x n_surfaces]
  RowMatrixXd rmnc_b;        // [mnboz x n_surfaces]
  RowMatrixXd zmns_b;        // [mnboz x n_surfaces]
  RowMatrixXd numns_b;       // [mnboz x n_surfaces]
  RowMatrixXd gmnc_b;        // [mnboz x n_surfaces]
  Eigen::VectorXd iota_b;    // [n_surfaces]
  Eigen::VectorXd boozer_g;  // [n_surfaces]
  Eigen::VectorXd boozer_i;  // [n_surfaces]
};

// The transformation to Boozer coordinates of booz_xform
// (https://github.com/hiddenSymmetries/booz_xform), restricted to
// stellarator symmetry, together with its exact tangent and adjoint.
//
// On every surface the VMEC angles are mapped to the Boozer angles
// theta_B = theta + lambda + iota nu and zeta_B = zeta + nu with
// nu = (w - I lambda) / (G + iota I), where w is the periodic part of the
// magnetic scalar potential assembled from bsubumnc (m != 0) and bsubvmnc
// (m = 0). Every Boozer spectrum is a quadrature over the VMEC angle grid that
// carries the Jacobian of this angle map, so the map is never inverted. The
// grid, the mode table and the half-grid interpolation of R and Z are those of
// booz_xform, so that the primal agrees with booz_xform to roundoff.
//
// The tangent and the adjoint differentiate exactly this discrete map, which
// is smooth as long as the Jacobian of the angle map does not vanish. They are
// hand-written: the map is a linear synthesis on the VMEC grid, a pointwise
// nonlinearity and a projection on the Boozer harmonics, whose adjoint is the
// transposed sum.
class BoozerTransform {
 public:
  // `surfaces` are 0-based indices into the half grid without the axis, as in
  // booz_xform's compute_surfs: surface j lies at s = (j + 1/2) / (ns - 1) and
  // reads column j + 1 of the half-grid wout arrays.
  static absl::StatusOr<BoozerTransform> Create(
      int nfp, int ns, const std::vector<int>& xm, const std::vector<int>& xn,
      const std::vector<int>& xm_nyq, const std::vector<int>& xn_nyq,
      const std::vector<int>& surfaces, int mboz, int nboz);

  absl::StatusOr<BoozerOutputSpectra> Forward(
      const BoozerInputSpectra& input) const;

  // Tangent of Forward at `input` in the direction `tangent`.
  absl::StatusOr<BoozerOutputSpectra> Jvp(
      const BoozerInputSpectra& input, const BoozerInputSpectra& tangent) const;

  // Cotangent of the inputs that the cotangent of the outputs pulls back to.
  absl::StatusOr<BoozerInputSpectra> Vjp(
      const BoozerInputSpectra& input,
      const BoozerOutputSpectra& cotangent) const;

  const std::vector<int>& xm_b() const { return xm_b_; }
  const std::vector<int>& xn_b() const { return xn_b_; }
  const std::vector<int>& surfaces() const { return surfaces_; }
  // Normalized toroidal flux of the selected surfaces.
  Eigen::VectorXd s_b() const;
  int ntheta() const { return ntheta_; }
  int nzeta() const { return nzeta_; }

 private:
  struct Surface;
  struct SurfaceTangent;
  struct GridArrays;

  BoozerTransform() = default;

  absl::Status CheckInput(const BoozerInputSpectra& input) const;
  absl::Status CheckOutput(const BoozerOutputSpectra& output) const;

  // R and Z of half-grid surface j from the full-grid coefficients: the mean
  // of the neighbours for even m, the mean of X / sqrt(s) times sqrt(s) for
  // odd m, extrapolated to the axis for m = 1 on the first surface.
  struct Stencil {
    int full_index;
    double weight;
  };
  std::vector<Stencil> RadialStencil(int mode, int j) const;
  Eigen::VectorXd HalfGridGeometry(const RowMatrixXd& full, int j) const;
  void AccumulateHalfGridGeometryAdjoint(const Eigen::VectorXd& half_bar, int j,
                                         RowMatrixXd& full_bar) const;

  GridArrays Synthesize(const BoozerInputSpectra& input, int j) const;
  Surface Solve(const BoozerInputSpectra& input, int j) const;

  // Boozer harmonics cos/sin(m theta_B - n zeta_B) on the VMEC grid.
  void BoozerHarmonics(const Eigen::VectorXd& theta_b,
                       const Eigen::VectorXd& zeta_b, RowMatrixXd& cos_b,
                       RowMatrixXd& sin_b) const;

  int nfp_ = 1;
  int ns_ = 0;
  int mboz_ = 0;
  int nboz_ = 0;
  int ntheta_ = 0;
  int nzeta_ = 0;
  int nu2_b_ = 0;
  int n_grid_ = 0;
  double fourier_factor_ = 0.0;

  std::vector<int> xm_, xn_, xm_nyq_, xn_nyq_;
  std::vector<int> xm_b_, xn_b_;
  std::vector<int> surfaces_;

  // Quadrature weight per grid point: 1/2 on theta = 0 and theta = pi.
  Eigen::VectorXd weight_;
  Eigen::VectorXd theta_;
  Eigen::VectorXd zeta_;

  // cos/sin(m theta - n zeta) on the VMEC grid, [n_grid x mnmax(_nyq)].
  RowMatrixXd cos_grid_, sin_grid_;
  RowMatrixXd cos_grid_nyq_, sin_grid_nyq_;

  // Mode numbers as doubles, and the Fourier normalization per Boozer mode.
  Eigen::VectorXd m_, n_, m_nyq_, n_nyq_, m_b_, n_b_, normalization_b_;
};

}  // namespace vmecpp

#endif  // VMECPP_VMEC_BOOZER_BOOZER_H_
