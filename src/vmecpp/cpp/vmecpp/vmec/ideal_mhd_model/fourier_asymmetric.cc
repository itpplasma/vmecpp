// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT
#include "vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.h"

#include <cmath>

#include "absl/algorithm/container.h"
#include "vmecpp/common/util/util.h"

namespace vmecpp {

// Implementation of totzspa: Fourier transform for anti-symmetric contributions
// This transforms the asymmetric Fourier coefficients (rmnsc, zmncc, lmncc,
// rmncs, zmnss, lmnss) to real space
void FourierToReal3DAsymmFastPoloidal(const FourierGeometry& physical_x,
                                      const std::vector<double>& xmpq,
                                      const RadialPartitioning& r,
                                      const Sizes& s, const RadialProfiles& rp,
                                      const FourierBasisFastPoloidal& fb,
                                      RealSpaceGeometryAsym& m_geometry_asym) {
  // Clear all arrays first
  absl::c_fill(m_geometry_asym.r1_a, 0);
  absl::c_fill(m_geometry_asym.ru_a, 0);
  absl::c_fill(m_geometry_asym.rv_a, 0);
  absl::c_fill(m_geometry_asym.z1_a, 0);
  absl::c_fill(m_geometry_asym.zu_a, 0);
  absl::c_fill(m_geometry_asym.zv_a, 0);
  absl::c_fill(m_geometry_asym.lu_a, 0);
  absl::c_fill(m_geometry_asym.lv_a, 0);

#pragma omp parallel for
  for (int jF = r.nsMinF1; jF < r.nsMaxF1; ++jF) {
    const double sqrtSF = rp.sqrtSF[jF - r.nsMinF1];
    const double xmpqF = xmpq[jF - r.nsMinF1];

    for (int m = 0; m < s.mpol; ++m) {
      // Apply mode scaling with sqrt(s) for odd-m modes
      // This implements Equation (8c) from Hirshman, Schwenn & Nührenberg
      // (1990)
      double modeScale = 1.0;
      if (m % 2 == 1) {  // odd-m modes
        // Prevent division by zero at axis using minimum value from next point
        const double sqrtS_min = (jF == r.nsMinF1 && r.nsMaxF1 - r.nsMinF1 > 1)
                                     ? rp.sqrtSF[1]
                                     : sqrtSF;
        modeScale = 1.0 / sqrtS_min;
      }

      // Poloidal loop
      for (int l = 0; l < s.nThetaReduced; ++l) {
        int idx_ml = m * s.nThetaReduced + l;

        // Toroidal loop
        for (int k = 0; k < s.nZeta; ++k) {
          int idx_kl = k * s.nThetaReduced + l;
          int idx_kl1 = (jF - r.nsMinF1) * s.nZnT + idx_kl;

          for (int n = 0; n < s.ntor + 1; ++n) {
            int idx_fc = ((jF - r.nsMinF1) * s.mpol + m) * (s.ntor + 1) + n;
            int idx_kn = k * (s.nnyq2 + 1) + n;

            // For asymmetric contributions, we use different basis
            // combinations: R: sin(m*theta)*cos(n*zeta) and
            // cos(m*theta)*sin(n*zeta) Z: cos(m*theta)*cos(n*zeta) and
            // sin(m*theta)*sin(n*zeta) lambda: similar to Z

            // rmnsc contribution: R ~ sin(m*theta)*cos(n*zeta)
            double rsc_term = physical_x.rmnsc[idx_fc] * fb.sinmu[idx_ml] *
                              fb.cosnv[idx_kn] * modeScale;

            // NOTE: Asymmetric contribution will be added to both even and odd
            // components

            m_geometry_asym.r1_a[idx_kl1] += rsc_term;
            m_geometry_asym.ru_a[idx_kl1] +=
                rsc_term * m * xmpqF;  // derivative w.r.t. theta
            m_geometry_asym.rv_a[idx_kl1] +=
                rsc_term * (-n);  // derivative w.r.t. zeta

            // zmncc contribution: Z ~ cos(m*theta)*cos(n*zeta)
            double zcc_term = physical_x.zmncc[idx_fc] * fb.cosmu[idx_ml] *
                              fb.cosnv[idx_kn] * modeScale;
            m_geometry_asym.z1_a[idx_kl1] += zcc_term;
            m_geometry_asym.zu_a[idx_kl1] +=
                zcc_term * (-m) * xmpqF;  // derivative w.r.t. theta
            m_geometry_asym.zv_a[idx_kl1] +=
                zcc_term * (-n);  // derivative w.r.t. zeta

            // lmncc contribution: lambda ~ cos(m*theta)*cos(n*zeta)
            double lcc_term = physical_x.lmncc[idx_fc] * fb.cosmu[idx_ml] *
                              fb.cosnv[idx_kn] * modeScale;
            m_geometry_asym.lu_a[idx_kl1] +=
                lcc_term * (-m) * xmpqF;  // derivative w.r.t. theta
            m_geometry_asym.lv_a[idx_kl1] +=
                lcc_term * (-n);  // derivative w.r.t. zeta

            if (s.lthreed && n > 0) {
              // rmncs contribution: R ~ cos(m*theta)*sin(n*zeta)
              double rcs_term = physical_x.rmncs[idx_fc] * fb.cosmu[idx_ml] *
                                fb.sinnv[idx_kn] * modeScale;
              m_geometry_asym.r1_a[idx_kl1] += rcs_term;
              m_geometry_asym.ru_a[idx_kl1] +=
                  rcs_term * (-m) * xmpqF;  // derivative w.r.t. theta
              m_geometry_asym.rv_a[idx_kl1] +=
                  rcs_term * n;  // derivative w.r.t. zeta

              // zmnss contribution: Z ~ sin(m*theta)*sin(n*zeta)
              double zss_term = physical_x.zmnss[idx_fc] * fb.sinmu[idx_ml] *
                                fb.sinnv[idx_kn] * modeScale;
              m_geometry_asym.z1_a[idx_kl1] += zss_term;
              m_geometry_asym.zu_a[idx_kl1] +=
                  zss_term * m * xmpqF;  // derivative w.r.t. theta
              m_geometry_asym.zv_a[idx_kl1] +=
                  zss_term * n;  // derivative w.r.t. zeta

              // lmnss contribution: lambda ~ sin(m*theta)*sin(n*zeta)
              double lss_term = physical_x.lmnss[idx_fc] * fb.sinmu[idx_ml] *
                                fb.sinnv[idx_kn] * modeScale;
              m_geometry_asym.lu_a[idx_kl1] +=
                  lss_term * m * xmpqF;  // derivative w.r.t. theta
              m_geometry_asym.lv_a[idx_kl1] +=
                  lss_term * n;  // derivative w.r.t. zeta
            }
          }  // n
        }  // k
      }  // l
    }  // m
  }  // jF
}

void FourierToReal2DAsymmFastPoloidal(const FourierGeometry& physical_x,
                                      const std::vector<double>& xmpq,
                                      const RadialPartitioning& r,
                                      const Sizes& s, const RadialProfiles& rp,
                                      const FourierBasisFastPoloidal& fb,
                                      RealSpaceGeometryAsym& m_geometry_asym) {
  // Clear all arrays first
  // For 2D case: use nThetaReduced for consistency with force arrays
  const int num_realsp = (r.nsMaxF1 - r.nsMinF1) * s.nThetaReduced;
  for (auto* v :
       {&m_geometry_asym.r1_a, &m_geometry_asym.ru_a, &m_geometry_asym.z1_a,
        &m_geometry_asym.zu_a, &m_geometry_asym.lu_a}) {
    absl::c_fill_n(*v, num_realsp, 0);
  }

  // For 2D case, only poloidal variation
  for (int jF = r.nsMinF1; jF < r.nsMaxF1; ++jF) {
    const double sqrtSF = rp.sqrtSF[jF - r.nsMinF1];
    const double xmpqF = xmpq[jF - r.nsMinF1];

    for (int m = 0; m < s.mpol; ++m) {
      // Apply mode scaling with sqrt(s) for odd-m modes
      double modeScale = 1.0;
      if (m % 2 == 1) {  // odd-m modes
        // Prevent division by zero at axis using minimum value from next point
        const double sqrtS_min = (jF == r.nsMinF1 && r.nsMaxF1 - r.nsMinF1 > 1)
                                     ? rp.sqrtSF[1]
                                     : sqrtSF;
        modeScale = 1.0 / sqrtS_min;
      }

      // Process asymmetric modes

      for (int l = 0; l < s.nThetaReduced; ++l) {
        int idx_ml = m * s.nThetaReduced + l;
        int idx_l1 = (jF - r.nsMinF1) * s.nThetaReduced + l;
        int idx_fc = ((jF - r.nsMinF1) * s.mpol + m) * (s.ntor + 1) + 0;

        // For 2D asymmetric case (n=0 only)
        // rmnsc contribution: R ~ sin(m*theta)
        double rsc_term =
            physical_x.rmnsc[idx_fc] * fb.sinmu[idx_ml] * modeScale;
        m_geometry_asym.r1_a[idx_l1] += rsc_term;
        m_geometry_asym.ru_a[idx_l1] +=
            rsc_term * m * xmpqF;  // derivative w.r.t. theta

        // zmncc contribution: Z ~ cos(m*theta)
        double zcc_term =
            physical_x.zmncc[idx_fc] * fb.cosmu[idx_ml] * modeScale;
        m_geometry_asym.z1_a[idx_l1] += zcc_term;
        m_geometry_asym.zu_a[idx_l1] +=
            zcc_term * (-m) * xmpqF;  // derivative w.r.t. theta

        // lmncc contribution: lambda ~ cos(m*theta)
        double lcc_term =
            physical_x.lmncc[idx_fc] * fb.cosmu[idx_ml] * modeScale;
        m_geometry_asym.lu_a[idx_l1] +=
            lcc_term * (-m) * xmpqF;  // derivative w.r.t. theta
      }  // l
    }  // m
  }  // jF
}

// Implementation of symrzl: Extend geometry from [0,pi] to [0,2pi]
// Uses reflection operations to combine symmetric and antisymmetric pieces
void SymmetrizeRealSpaceGeometry(const Sizes& s, const RadialPartitioning& r,
                                 RealSpaceGeometry& m_geometry,
                                 RealSpaceGeometryAsym& m_geometry_asym) {
  // For stellarator-symmetric case (lasym=false), the full theta grid is
  // obtained by mirroring the [0,pi] data to [pi,2pi] For non-stellarator
  // symmetric case (lasym=true), we need to combine symmetric and antisymmetric
  // contributions

  // This function extends the geometry arrays from the reduced theta interval
  // [0,pi] to the full interval [0,2pi] The extension depends on the parity of
  // the quantity:
  // - Even parity in theta: f(2pi-theta) = f(theta)
  // - Odd parity in theta: f(2pi-theta) = -f(theta)

#pragma omp parallel for
  for (int jF = r.nsMinF1; jF < r.nsMaxF1; ++jF) {
    // Loop over toroidal angle
    for (int k = 0; k < s.nZeta; ++k) {
      // Loop over the extended poloidal range [pi, 2pi]
      for (int l = s.nThetaReduced; l < s.nThetaEven; ++l) {
        int l_mirror = s.nThetaEven - l;  // Mirror index in [0,pi]

        int idx_kl = k * s.nThetaEven + l;
        int idx_kl_mirror = k * s.nThetaEven + l_mirror;
        int idx_full = (jF - r.nsMinF1) * s.nZnT + idx_kl;
        int idx_mirror = (jF - r.nsMinF1) * s.nZnT + idx_kl_mirror;

        // For symmetric quantities (even in theta):
        // R, Z are even in theta
        m_geometry.r1_e[idx_full] = m_geometry.r1_e[idx_mirror];
        m_geometry.r1_o[idx_full] = m_geometry.r1_o[idx_mirror];
        m_geometry.z1_e[idx_full] = m_geometry.z1_e[idx_mirror];
        m_geometry.z1_o[idx_full] = m_geometry.z1_o[idx_mirror];

        // dR/dtheta, dZ/dtheta are odd in theta (sign flip)
        m_geometry.ru_e[idx_full] = -m_geometry.ru_e[idx_mirror];
        m_geometry.ru_o[idx_full] = -m_geometry.ru_o[idx_mirror];
        m_geometry.zu_e[idx_full] = -m_geometry.zu_e[idx_mirror];
        m_geometry.zu_o[idx_full] = -m_geometry.zu_o[idx_mirror];

        // dR/dzeta, dZ/dzeta are even in theta
        m_geometry.rv_e[idx_full] = m_geometry.rv_e[idx_mirror];
        m_geometry.rv_o[idx_full] = m_geometry.rv_o[idx_mirror];
        m_geometry.zv_e[idx_full] = m_geometry.zv_e[idx_mirror];
        m_geometry.zv_o[idx_full] = m_geometry.zv_o[idx_mirror];

        // dlambda/dtheta is odd, dlambda/dzeta is even
        m_geometry.lu_e[idx_full] = -m_geometry.lu_e[idx_mirror];
        m_geometry.lu_o[idx_full] = -m_geometry.lu_o[idx_mirror];
        m_geometry.lv_e[idx_full] = m_geometry.lv_e[idx_mirror];
        m_geometry.lv_o[idx_full] = m_geometry.lv_o[idx_mirror];

        // For asymmetric quantities (when lasym=true):
        // The asymmetric parts have opposite parity
        if (s.lasym && !m_geometry_asym.r1_a.empty()) {
          // R_asym, Z_asym are odd in theta (sign flip)
          m_geometry_asym.r1_a[idx_full] = -m_geometry_asym.r1_a[idx_mirror];
          m_geometry_asym.z1_a[idx_full] = -m_geometry_asym.z1_a[idx_mirror];

          // dR_asym/dtheta, dZ_asym/dtheta are even in theta
          m_geometry_asym.ru_a[idx_full] = m_geometry_asym.ru_a[idx_mirror];
          m_geometry_asym.zu_a[idx_full] = m_geometry_asym.zu_a[idx_mirror];

          // dR_asym/dzeta, dZ_asym/dzeta are odd in theta
          m_geometry_asym.rv_a[idx_full] = -m_geometry_asym.rv_a[idx_mirror];
          m_geometry_asym.zv_a[idx_full] = -m_geometry_asym.zv_a[idx_mirror];

          // dlambda_asym/dtheta is even, dlambda_asym/dzeta is odd
          m_geometry_asym.lu_a[idx_full] = m_geometry_asym.lu_a[idx_mirror];
          m_geometry_asym.lv_a[idx_full] = -m_geometry_asym.lv_a[idx_mirror];
        }
      }  // l
    }  // k
  }  // jF

  // Now combine symmetric and antisymmetric parts if lasym=true
  // Following jVMEC's symrzl approach for proper asymmetric combination
  if (s.lasym && !m_geometry_asym.r1_a.empty()) {
#pragma omp parallel for
    for (int jF = r.nsMinF1; jF < r.nsMaxF1; ++jF) {
      // For the primary interval θ ∈ [0, π]: direct addition
      for (int k = 0; k < s.nZeta; ++k) {
        for (int l = 0; l < s.nThetaReduced; ++l) {
          int idx_kl = k * s.nThetaEven + l;
          int idx = (jF - r.nsMinF1) * s.nZnT + idx_kl;

          // Direct addition for primary interval (jVMEC approach)
          m_geometry.r1_e[idx] += m_geometry_asym.r1_a[idx];
          m_geometry.ru_e[idx] += m_geometry_asym.ru_a[idx];
          m_geometry.rv_e[idx] += m_geometry_asym.rv_a[idx];

          m_geometry.z1_e[idx] += m_geometry_asym.z1_a[idx];
          m_geometry.zu_e[idx] += m_geometry_asym.zu_a[idx];
          m_geometry.zv_e[idx] += m_geometry_asym.zv_a[idx];

          m_geometry.lu_e[idx] += m_geometry_asym.lu_a[idx];
          m_geometry.lv_e[idx] += m_geometry_asym.lv_a[idx];

          // Don't add to odd components - this was causing the doubling issue
          // The asymmetric contribution should only be added once, not twice
        }
      }

      // For the extended interval θ ∈ [π, 2π]: reflection with asymmetric
      // combination
      for (int k = 0; k < s.nZeta; ++k) {
        for (int l = s.nThetaReduced; l < s.nThetaEven; ++l) {
          int l_mirror = s.nThetaEven - l;         // Mirror index in [0,π]
          int k_mirror = (s.nZeta - k) % s.nZeta;  // Mirror index for zeta

          int idx_kl = k * s.nThetaEven + l;
          int idx_mirror = k_mirror * s.nThetaEven + l_mirror;
          int idx_full = (jF - r.nsMinF1) * s.nZnT + idx_kl;
          int idx_reflected = (jF - r.nsMinF1) * s.nZnT + idx_mirror;

          // jVMEC's symrzl approach: R and Z have different sign patterns
          // Apply reflection only to even components to avoid doubling
          // R: R[extended] = R[reflected] - R_asym[reflected]
          m_geometry.r1_e[idx_full] = m_geometry.r1_e[idx_reflected] -
                                      m_geometry_asym.r1_a[idx_reflected];

          // dR/dtheta has opposite sign: dR/dtheta[extended] =
          // -dR/dtheta[reflected] + dR_asym/dtheta[reflected]
          m_geometry.ru_e[idx_full] = -m_geometry.ru_e[idx_reflected] +
                                      m_geometry_asym.ru_a[idx_reflected];

          // dR/dzeta: dR/dzeta[extended] = -dR/dzeta[reflected] +
          // dR_asym/dzeta[reflected]
          m_geometry.rv_e[idx_full] = -m_geometry.rv_e[idx_reflected] +
                                      m_geometry_asym.rv_a[idx_reflected];

          // Z: Z[extended] = -Z[reflected] + Z_asym[reflected]
          m_geometry.z1_e[idx_full] = -m_geometry.z1_e[idx_reflected] +
                                      m_geometry_asym.z1_a[idx_reflected];

          // dZ/dtheta: dZ/dtheta[extended] = dZ/dtheta[reflected] -
          // dZ_asym/dtheta[reflected]
          m_geometry.zu_e[idx_full] = m_geometry.zu_e[idx_reflected] -
                                      m_geometry_asym.zu_a[idx_reflected];

          // dZ/dzeta: dZ/dzeta[extended] = dZ/dzeta[reflected] -
          // dZ_asym/dzeta[reflected]
          m_geometry.zv_e[idx_full] = m_geometry.zv_e[idx_reflected] -
                                      m_geometry_asym.zv_a[idx_reflected];

          // Lambda derivatives follow Z pattern
          m_geometry.lu_e[idx_full] = m_geometry.lu_e[idx_reflected] -
                                      m_geometry_asym.lu_a[idx_reflected];
          m_geometry.lv_e[idx_full] = m_geometry.lv_e[idx_reflected] -
                                      m_geometry_asym.lv_a[idx_reflected];

          // For odd components, use simple reflection without asymmetric terms
          m_geometry.r1_o[idx_full] = m_geometry.r1_o[idx_reflected];
          m_geometry.ru_o[idx_full] = -m_geometry.ru_o[idx_reflected];
          m_geometry.rv_o[idx_full] = -m_geometry.rv_o[idx_reflected];
          m_geometry.z1_o[idx_full] = -m_geometry.z1_o[idx_reflected];
          m_geometry.zu_o[idx_full] = m_geometry.zu_o[idx_reflected];
          m_geometry.zv_o[idx_full] = m_geometry.zv_o[idx_reflected];
          m_geometry.lu_o[idx_full] = m_geometry.lu_o[idx_reflected];
          m_geometry.lv_o[idx_full] = m_geometry.lv_o[idx_reflected];
        }
      }
    }
  }
}

// Implementation of tomnspa: Fourier transform antisymmetric forces back to
// spectral space
void ForcesToFourier3DAsymmFastPoloidal(const RealSpaceForcesAsym& d_asym,
                                        const std::vector<double>& /* xmpq */,
                                        const RadialPartitioning& rp,
                                        const Sizes& s,
                                        const FourierBasisFastPoloidal& fb,
                                        FourierForces& m_physical_forces) {
  // Transform antisymmetric real-space forces to Fourier coefficients
  // This complements the symmetric version for lasym=true configurations

  const int jMinL = 1;  // axis lambda stays zero

  for (int jF = rp.nsMinF; jF < rp.nsMaxF; ++jF) {
    const int mmax = jF == 0 ? 1 : s.mpol;
    for (int m = 0; m < mmax; ++m) {
      for (int k = 0; k < s.nZeta; ++k) {
        double rmksc = 0.0;
        double rmksc_n = 0.0;
        double rmkcs = 0.0;
        double rmkcs_n = 0.0;
        double zmkcc = 0.0;
        double zmkcc_n = 0.0;
        double zmkss = 0.0;
        double zmkss_n = 0.0;
        double lmkcc = 0.0;
        double lmkcc_n = 0.0;
        double lmkss = 0.0;
        double lmkss_n = 0.0;

        const int idx_kl_base = ((jF - rp.nsMinF) * s.nZeta + k) * s.nThetaEff;
        const int idx_ml_base = m * s.nThetaReduced;

        for (int l = 0; l < s.nThetaReduced; ++l) {
          const int idx_kl = idx_kl_base + l;
          const int idx_ml = idx_ml_base + l;

          const double cosmui = fb.cosmui[idx_ml];
          const double sinmui = fb.sinmui[idx_ml];
          const double cosmumi = fb.cosmumi[idx_ml];
          const double sinmumi = fb.sinmumi[idx_ml];

          // Lambda force components for asymmetric modes
          lmkcc += d_asym.blmn_a[idx_kl] * cosmumi;   // --> flcc
          lmkss += d_asym.blmn_a[idx_kl] * sinmumi;   // --> flss
          lmkss_n -= d_asym.clmn_a[idx_kl] * cosmui;  // --> flss
          lmkcc_n -= d_asym.clmn_a[idx_kl] * sinmui;  // --> flcc

          rmkcs_n -= d_asym.crmn_a[idx_kl] * cosmui;  // --> frcs
          zmkss_n -= d_asym.czmn_a[idx_kl] * cosmui;  // --> fzss

          rmksc_n -= d_asym.crmn_a[idx_kl] * sinmui;  // --> frsc
          zmkcc_n -= d_asym.czmn_a[idx_kl] * sinmui;  // --> fzcc

          // Assemble effective R and Z forces from asymmetric MHD contributions
          const double tempR = d_asym.armn_a[idx_kl];
          const double tempZ = d_asym.azmn_a[idx_kl];

          // For asymmetric modes, we use different basis combinations:
          // R: sin(m*theta)*cos(n*zeta) and cos(m*theta)*sin(n*zeta)
          // Z: cos(m*theta)*cos(n*zeta) and sin(m*theta)*sin(n*zeta)
          rmksc +=
              tempR * sinmui + d_asym.brmn_a[idx_kl] * cosmumi;  // --> frsc
          rmkcs +=
              tempR * cosmui + d_asym.brmn_a[idx_kl] * sinmumi;  // --> frcs
          zmkcc +=
              tempZ * cosmui + d_asym.bzmn_a[idx_kl] * sinmumi;  // --> fzcc
          zmkss +=
              tempZ * sinmui + d_asym.bzmn_a[idx_kl] * cosmumi;  // --> fzss
        }  // l

        for (int n = 0; n < s.ntor + 1; ++n) {
          const int idx_mn = ((jF - rp.nsMinF) * s.mpol + m) * (s.ntor + 1) + n;
          const int idx_kn = k * (s.nnyq2 + 1) + n;

          const double cosnv = fb.cosnv[idx_kn];
          const double sinnv = fb.sinnv[idx_kn];
          const double cosnvn = fb.cosnvn[idx_kn];
          const double sinnvn = fb.sinnvn[idx_kn];

          // Accumulate asymmetric force contributions
          m_physical_forces.frsc[idx_mn] += rmksc * cosnv + rmksc_n * sinnvn;
          m_physical_forces.frcs[idx_mn] += rmkcs * sinnv + rmkcs_n * cosnvn;
          m_physical_forces.fzcc[idx_mn] += zmkcc * cosnv + zmkcc_n * sinnvn;
          m_physical_forces.fzss[idx_mn] += zmkss * sinnv + zmkss_n * cosnvn;

          if (jMinL <= jF) {
            m_physical_forces.flcc[idx_mn] += lmkcc * cosnv + lmkcc_n * sinnvn;
            m_physical_forces.flss[idx_mn] += lmkss * sinnv + lmkss_n * cosnvn;
          }
        }  // n
      }  // k
    }  // m
  }  // jF
}

void ForcesToFourier2DAsymmFastPoloidal(const RealSpaceForcesAsym& d_asym,
                                        const std::vector<double>& /* xmpq */,
                                        const RadialPartitioning& rp,
                                        const Sizes& s,
                                        const FourierBasisFastPoloidal& fb,
                                        FourierForces& m_physical_forces) {
  // Transform antisymmetric real-space forces to Fourier coefficients for 2D
  // case This is the 2D version without toroidal dependence (ntor=0, n=0 only)

  const int jMinL = 1;  // axis lambda stays zero

  for (int jF = rp.nsMinF; jF < rp.nsMaxF; ++jF) {
    const int mmax = jF == 0 ? 1 : s.mpol;
    for (int m = 0; m < mmax; ++m) {
      // For 2D case, only n=0 (no toroidal variation)
      const int n = 0;

      // Only the components needed for 2D asymmetric (n=0 only)
      double rmksc = 0.0;  // R sin(m*theta)*cos(0*zeta)
      double zmkcc = 0.0;  // Z cos(m*theta)*cos(0*zeta)
      double lmkcc = 0.0;  // lambda cos(m*theta)*cos(0*zeta)

      // For 2D case: simplified indexing without toroidal complexity
      // Force arrays are sized as (nsMaxF - nsMinF) * nThetaReduced
      const int idx_kl_base = (jF - rp.nsMinF) * s.nThetaReduced;
      const int idx_ml_base = m * s.nThetaReduced;

      for (int l = 0; l < s.nThetaReduced; ++l) {
        const int idx_kl = idx_kl_base + l;
        const int idx_ml = idx_ml_base + l;

        const double cosmui = fb.cosmui[idx_ml];
        const double sinmui = fb.sinmui[idx_ml];

        // Assemble effective R and Z forces from asymmetric MHD contributions
        // Add bounds checking to debug the segfault
        if (idx_kl >= static_cast<int>(d_asym.armn_a.size()) ||
            idx_kl >= static_cast<int>(d_asym.azmn_a.size()) || idx_kl < 0) {
          continue;  // Skip if out of bounds
        }
        const double tempR = d_asym.armn_a[idx_kl];
        const double tempZ = d_asym.azmn_a[idx_kl];

        // For 2D asymmetric: only process sin(m*theta) for R and cos(m*theta)
        // for Z Based on jVMEC pattern for 2D asymmetric cases
        rmksc += tempR * sinmui;  // R sin(m*theta) component
        zmkcc += tempZ * cosmui;  // Z cos(m*theta) component

        // Lambda force: access blmn_a if it exists and has valid data
        if (!d_asym.blmn_a.empty() &&
            idx_kl < static_cast<int>(d_asym.blmn_a.size())) {
          const double tempL = d_asym.blmn_a[idx_kl];
          lmkcc += tempL * cosmui;  // lambda cos(m*theta) component
        }
      }  // l

      // For 2D case, only n=0 contribution
      const int idx_mn = ((jF - rp.nsMinF) * s.mpol + m) * (s.ntor + 1) + n;

      // For 2D (n=0), only assign to components that don't involve sin(n*zeta)
      // Based on jVMEC: 2D asymmetric only processes frsc and fzcc components
      m_physical_forces.frsc[idx_mn] +=
          rmksc;  // frsc: R sin(m*theta)*cos(0*zeta) = R sin(m*theta)
      m_physical_forces.fzcc[idx_mn] +=
          zmkcc;  // fzcc: Z cos(m*theta)*cos(0*zeta) = Z cos(m*theta)

      // Skip frcs and fzss as they involve sin(n*zeta) which is zero for n=0
      // rmkcs and zmkss are not used in 2D asymmetric case

      // Lambda components only for jF >= jMinL
      // For 2D, only flcc is used (cos(m*theta)*cos(0*zeta))
      if (jMinL <= jF) {
        m_physical_forces.flcc[idx_mn] += lmkcc;
      }
    }  // m
  }  // jF
}

// Implementation of symforce: Symmetrize forces in (theta,zeta) space
// Separates forces into symmetric and antisymmetric components
void SymmetrizeForces(const Sizes& s, const RadialPartitioning& r,
                      RealSpaceForces& m_forces,
                      RealSpaceForcesAsym& m_forces_asym) {
  // Force symmetrization based on stellarator symmetry decomposition
  // Following jVMEC implementation: decompose forces into symmetric and
  // antisymmetric parts f_sym = 0.5 * (f(k,l) + f(k_rev,l_rev)) f_asym = 0.5 *
  // (f(k,l) - f(k_rev,l_rev)) where (k_rev,l_rev) represents the stellarator
  // symmetric point (-zeta,-theta)

  if (!s.lasym) {
    return;  // No symmetrization needed for stellarator-symmetric case
  }

  // Grid sizes for symmetrization
  const int nZeta = s.nZeta;
  const int nThetaEff = s.nThetaEff;
  const int nZnT = s.nZnT;
  const int ntheta1 = s.nThetaEven;
  const int ntheta2 = s.nThetaReduced;

  // Apply stellarator symmetry decomposition following jVMEC approach
  for (int jF = r.nsMinF; jF < r.nsMaxF; ++jF) {
    const int jOffset = (jF - r.nsMinF) * nZnT;

    // Create temporary arrays for both symmetric and asymmetric forces
    std::vector<double> armn_sym_e(nZnT), armn_sym_o(nZnT);
    std::vector<double> azmn_sym_e(nZnT), azmn_sym_o(nZnT);
    std::vector<double> brmn_sym_e(nZnT), brmn_sym_o(nZnT);
    std::vector<double> bzmn_sym_e(nZnT), bzmn_sym_o(nZnT);
    std::vector<double> blmn_sym_e(nZnT), blmn_sym_o(nZnT);
    std::vector<double> clmn_sym_e(nZnT), clmn_sym_o(nZnT);
    std::vector<double> crmn_sym_e(nZnT), crmn_sym_o(nZnT);
    std::vector<double> czmn_sym_e(nZnT), czmn_sym_o(nZnT);

    std::vector<double> armn_asym_e(nZnT), armn_asym_o(nZnT);
    std::vector<double> azmn_asym_e(nZnT), azmn_asym_o(nZnT);
    std::vector<double> brmn_asym_e(nZnT), brmn_asym_o(nZnT);
    std::vector<double> bzmn_asym_e(nZnT), bzmn_asym_o(nZnT);
    std::vector<double> blmn_asym_e(nZnT), blmn_asym_o(nZnT);
    std::vector<double> clmn_asym_e(nZnT), clmn_asym_o(nZnT);
    std::vector<double> crmn_asym_e(nZnT), crmn_asym_o(nZnT);
    std::vector<double> czmn_asym_e(nZnT), czmn_asym_o(nZnT);

    for (int l = 0; l < ntheta2; ++l) {
      const int lReversed = (ntheta1 - l) % ntheta1;

      for (int k = 0; k < nZeta; ++k) {
        const int kReversed = (nZeta - k) % nZeta;

        const int idx_kl = k * nThetaEff + l;
        // Ensure lReversed is within the valid range for nThetaEff
        const int lRev_safe = std::min(lReversed, nThetaEff - 1);
        const int idx_rev = kReversed * nThetaEff + lRev_safe;

        // Bounds checking
        if (idx_kl >= nZnT || idx_rev >= nZnT || idx_kl < 0 || idx_rev < 0) {
          continue;  // Skip invalid indices
        }

        // Additional bounds checking for force array access
        // Standard arrays (armn, azmn, brmn, bzmn, crmn, czmn)
        if (jOffset + idx_kl >= static_cast<int>(m_forces.armn_e.size()) ||
            jOffset + idx_rev >= static_cast<int>(m_forces.armn_e.size())) {
          continue;  // Skip if array access would be out of bounds
        }

        // Lambda arrays (blmn, clmn) may have different size - check separately
        const bool lambda_arrays_valid =
            (jOffset + idx_kl < static_cast<int>(m_forces.blmn_e.size())) &&
            (jOffset + idx_rev < static_cast<int>(m_forces.blmn_e.size()));

        // Apply jVMEC stellarator symmetry decomposition
        // Following the exact pattern from jVMEC:

        // armn: symmetric part retained, antisymmetric part goes to asym
        armn_sym_e[idx_kl] = 0.5 * (m_forces.armn_e[jOffset + idx_kl] +
                                    m_forces.armn_e[jOffset + idx_rev]);
        armn_sym_o[idx_kl] = 0.5 * (m_forces.armn_o[jOffset + idx_kl] +
                                    m_forces.armn_o[jOffset + idx_rev]);
        armn_asym_e[idx_kl] = 0.5 * (m_forces.armn_e[jOffset + idx_kl] -
                                     m_forces.armn_e[jOffset + idx_rev]);
        armn_asym_o[idx_kl] = 0.5 * (m_forces.armn_o[jOffset + idx_kl] -
                                     m_forces.armn_o[jOffset + idx_rev]);

        // brmn: antisymmetric part goes to symmetric, symmetric part goes to
        // asym
        brmn_sym_e[idx_kl] = 0.5 * (m_forces.brmn_e[jOffset + idx_kl] -
                                    m_forces.brmn_e[jOffset + idx_rev]);
        brmn_sym_o[idx_kl] = 0.5 * (m_forces.brmn_o[jOffset + idx_kl] -
                                    m_forces.brmn_o[jOffset + idx_rev]);
        brmn_asym_e[idx_kl] = 0.5 * (m_forces.brmn_e[jOffset + idx_kl] +
                                     m_forces.brmn_e[jOffset + idx_rev]);
        brmn_asym_o[idx_kl] = 0.5 * (m_forces.brmn_o[jOffset + idx_kl] +
                                     m_forces.brmn_o[jOffset + idx_rev]);

        // azmn: antisymmetric part goes to symmetric, symmetric part goes to
        // asym
        azmn_sym_e[idx_kl] = 0.5 * (m_forces.azmn_e[jOffset + idx_kl] -
                                    m_forces.azmn_e[jOffset + idx_rev]);
        azmn_sym_o[idx_kl] = 0.5 * (m_forces.azmn_o[jOffset + idx_kl] -
                                    m_forces.azmn_o[jOffset + idx_rev]);
        azmn_asym_e[idx_kl] = 0.5 * (m_forces.azmn_e[jOffset + idx_kl] +
                                     m_forces.azmn_e[jOffset + idx_rev]);
        azmn_asym_o[idx_kl] = 0.5 * (m_forces.azmn_o[jOffset + idx_kl] +
                                     m_forces.azmn_o[jOffset + idx_rev]);

        // bzmn: symmetric part retained, antisymmetric part goes to asym
        bzmn_sym_e[idx_kl] = 0.5 * (m_forces.bzmn_e[jOffset + idx_kl] +
                                    m_forces.bzmn_e[jOffset + idx_rev]);
        bzmn_sym_o[idx_kl] = 0.5 * (m_forces.bzmn_o[jOffset + idx_kl] +
                                    m_forces.bzmn_o[jOffset + idx_rev]);
        bzmn_asym_e[idx_kl] = 0.5 * (m_forces.bzmn_e[jOffset + idx_kl] -
                                     m_forces.bzmn_e[jOffset + idx_rev]);
        bzmn_asym_o[idx_kl] = 0.5 * (m_forces.bzmn_o[jOffset + idx_kl] -
                                     m_forces.bzmn_o[jOffset + idx_rev]);

        // blmn: antisymmetric part goes to symmetric, symmetric part goes to
        // asym
        if (lambda_arrays_valid) {
          blmn_sym_e[idx_kl] = 0.5 * (m_forces.blmn_e[jOffset + idx_kl] -
                                      m_forces.blmn_e[jOffset + idx_rev]);
          blmn_sym_o[idx_kl] = 0.5 * (m_forces.blmn_o[jOffset + idx_kl] -
                                      m_forces.blmn_o[jOffset + idx_rev]);
          blmn_asym_e[idx_kl] = 0.5 * (m_forces.blmn_e[jOffset + idx_kl] +
                                       m_forces.blmn_e[jOffset + idx_rev]);
          blmn_asym_o[idx_kl] = 0.5 * (m_forces.blmn_o[jOffset + idx_kl] +
                                       m_forces.blmn_o[jOffset + idx_rev]);
        } else {
          blmn_sym_e[idx_kl] = 0.0;
          blmn_sym_o[idx_kl] = 0.0;
          blmn_asym_e[idx_kl] = 0.0;
          blmn_asym_o[idx_kl] = 0.0;
        }

        // clmn: symmetric part retained, antisymmetric part goes to asym
        if (lambda_arrays_valid) {
          clmn_sym_e[idx_kl] = 0.5 * (m_forces.clmn_e[jOffset + idx_kl] +
                                      m_forces.clmn_e[jOffset + idx_rev]);
          clmn_sym_o[idx_kl] = 0.5 * (m_forces.clmn_o[jOffset + idx_kl] +
                                      m_forces.clmn_o[jOffset + idx_rev]);
          clmn_asym_e[idx_kl] = 0.5 * (m_forces.clmn_e[jOffset + idx_kl] -
                                       m_forces.clmn_e[jOffset + idx_rev]);
          clmn_asym_o[idx_kl] = 0.5 * (m_forces.clmn_o[jOffset + idx_kl] -
                                       m_forces.clmn_o[jOffset + idx_rev]);
        } else {
          clmn_sym_e[idx_kl] = 0.0;
          clmn_sym_o[idx_kl] = 0.0;
          clmn_asym_e[idx_kl] = 0.0;
          clmn_asym_o[idx_kl] = 0.0;
        }

        // crmn: antisymmetric part goes to symmetric, symmetric part goes to
        // asym
        crmn_sym_e[idx_kl] = 0.5 * (m_forces.crmn_e[jOffset + idx_kl] -
                                    m_forces.crmn_e[jOffset + idx_rev]);
        crmn_sym_o[idx_kl] = 0.5 * (m_forces.crmn_o[jOffset + idx_kl] -
                                    m_forces.crmn_o[jOffset + idx_rev]);
        crmn_asym_e[idx_kl] = 0.5 * (m_forces.crmn_e[jOffset + idx_kl] +
                                     m_forces.crmn_e[jOffset + idx_rev]);
        crmn_asym_o[idx_kl] = 0.5 * (m_forces.crmn_o[jOffset + idx_kl] +
                                     m_forces.crmn_o[jOffset + idx_rev]);

        // czmn: symmetric part retained, antisymmetric part goes to asym
        czmn_sym_e[idx_kl] = 0.5 * (m_forces.czmn_e[jOffset + idx_kl] +
                                    m_forces.czmn_e[jOffset + idx_rev]);
        czmn_sym_o[idx_kl] = 0.5 * (m_forces.czmn_o[jOffset + idx_kl] +
                                    m_forces.czmn_o[jOffset + idx_rev]);
        czmn_asym_e[idx_kl] = 0.5 * (m_forces.czmn_e[jOffset + idx_kl] -
                                     m_forces.czmn_e[jOffset + idx_rev]);
        czmn_asym_o[idx_kl] = 0.5 * (m_forces.czmn_o[jOffset + idx_kl] -
                                     m_forces.czmn_o[jOffset + idx_rev]);
      }
    }

    // Copy symmetrized forces back to original arrays
    for (int kl = 0; kl < nZnT; ++kl) {
      const_cast<double*>(m_forces.armn_e.data())[jOffset + kl] =
          armn_sym_e[kl];
      const_cast<double*>(m_forces.armn_o.data())[jOffset + kl] =
          armn_sym_o[kl];
      const_cast<double*>(m_forces.azmn_e.data())[jOffset + kl] =
          azmn_sym_e[kl];
      const_cast<double*>(m_forces.azmn_o.data())[jOffset + kl] =
          azmn_sym_o[kl];
      const_cast<double*>(m_forces.brmn_e.data())[jOffset + kl] =
          brmn_sym_e[kl];
      const_cast<double*>(m_forces.brmn_o.data())[jOffset + kl] =
          brmn_sym_o[kl];
      const_cast<double*>(m_forces.bzmn_e.data())[jOffset + kl] =
          bzmn_sym_e[kl];
      const_cast<double*>(m_forces.bzmn_o.data())[jOffset + kl] =
          bzmn_sym_o[kl];
      // Lambda arrays may have different size, check bounds
      if (jOffset + kl < static_cast<int>(m_forces.blmn_e.size())) {
        const_cast<double*>(m_forces.blmn_e.data())[jOffset + kl] =
            blmn_sym_e[kl];
        const_cast<double*>(m_forces.blmn_o.data())[jOffset + kl] =
            blmn_sym_o[kl];
        const_cast<double*>(m_forces.clmn_e.data())[jOffset + kl] =
            clmn_sym_e[kl];
        const_cast<double*>(m_forces.clmn_o.data())[jOffset + kl] =
            clmn_sym_o[kl];
      }
      const_cast<double*>(m_forces.crmn_e.data())[jOffset + kl] =
          crmn_sym_e[kl];
      const_cast<double*>(m_forces.crmn_o.data())[jOffset + kl] =
          crmn_sym_o[kl];
      const_cast<double*>(m_forces.czmn_e.data())[jOffset + kl] =
          czmn_sym_e[kl];
      const_cast<double*>(m_forces.czmn_o.data())[jOffset + kl] =
          czmn_sym_o[kl];
    }

    // Store asymmetric components in the asymmetric force arrays
    // Only store the ones that are not empty and have valid data pointers
    if (!m_forces_asym.armn_a.empty() &&
        m_forces_asym.armn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        const_cast<double*>(m_forces_asym.armn_a.data())[jOffset + kl] =
            armn_asym_e[kl] + armn_asym_o[kl];  // Combine even and odd parts
      }
    }
    if (!m_forces_asym.azmn_a.empty() &&
        m_forces_asym.azmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        const_cast<double*>(m_forces_asym.azmn_a.data())[jOffset + kl] =
            azmn_asym_e[kl] + azmn_asym_o[kl];
      }
    }
    if (!m_forces_asym.brmn_a.empty() &&
        m_forces_asym.brmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        const_cast<double*>(m_forces_asym.brmn_a.data())[jOffset + kl] =
            brmn_asym_e[kl] + brmn_asym_o[kl];
      }
    }
    if (!m_forces_asym.bzmn_a.empty() &&
        m_forces_asym.bzmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        const_cast<double*>(m_forces_asym.bzmn_a.data())[jOffset + kl] =
            bzmn_asym_e[kl] + bzmn_asym_o[kl];
      }
    }
    if (!m_forces_asym.blmn_a.empty() &&
        m_forces_asym.blmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        if (jOffset + kl < static_cast<int>(m_forces_asym.blmn_a.size())) {
          const_cast<double*>(m_forces_asym.blmn_a.data())[jOffset + kl] =
              blmn_asym_e[kl] + blmn_asym_o[kl];
        }
      }
    }
    if (!m_forces_asym.clmn_a.empty() &&
        m_forces_asym.clmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        if (jOffset + kl < static_cast<int>(m_forces_asym.clmn_a.size())) {
          const_cast<double*>(m_forces_asym.clmn_a.data())[jOffset + kl] =
              clmn_asym_e[kl] + clmn_asym_o[kl];
        }
      }
    }
    if (!m_forces_asym.crmn_a.empty() &&
        m_forces_asym.crmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        const_cast<double*>(m_forces_asym.crmn_a.data())[jOffset + kl] =
            crmn_asym_e[kl] + crmn_asym_o[kl];
      }
    }
    if (!m_forces_asym.czmn_a.empty() &&
        m_forces_asym.czmn_a.data() != nullptr) {
      for (int kl = 0; kl < nZnT; ++kl) {
        const_cast<double*>(m_forces_asym.czmn_a.data())[jOffset + kl] =
            czmn_asym_e[kl] + czmn_asym_o[kl];
      }
    }
  }
}

}  // namespace vmecpp
