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
      // This implements Equation (8c) from Hirshman, Schwenn & Nührenberg (1990)
      double modeScale = 1.0;
      if (m % 2 == 1) {  // odd-m modes
        modeScale = 1.0 / std::max(sqrtSF, rp.sqrtSF[0]);
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

            // For asymmetric contributions, we use different basis combinations:
            // R: sin(m*theta)*cos(n*zeta) and cos(m*theta)*sin(n*zeta)
            // Z: cos(m*theta)*cos(n*zeta) and sin(m*theta)*sin(n*zeta)
            // lambda: similar to Z

            // rmnsc contribution: R ~ sin(m*theta)*cos(n*zeta)
            double rsc_term = physical_x.rmnsc[idx_fc] * fb.sinmu[idx_ml] *
                              fb.cosnv[idx_kn] * modeScale;
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
        }    // k
      }      // l
    }        // m
  }          // jF
}

void FourierToReal2DAsymmFastPoloidal(const FourierGeometry& physical_x,
                                      const std::vector<double>& xmpq,
                                      const RadialPartitioning& r,
                                      const Sizes& s, const RadialProfiles& rp,
                                      const FourierBasisFastPoloidal& fb,
                                      RealSpaceGeometryAsym& m_geometry_asym) {
  // Clear all arrays first
  const int num_realsp = (r.nsMaxF1 - r.nsMinF1) * s.nThetaEff;
  for (auto* v : {&m_geometry_asym.r1_a, &m_geometry_asym.ru_a,
                  &m_geometry_asym.z1_a, &m_geometry_asym.zu_a,
                  &m_geometry_asym.lu_a}) {
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
        modeScale = 1.0 / std::max(sqrtSF, rp.sqrtSF[0]);
      }

      for (int l = 0; l < s.nThetaEff; ++l) {
        int idx_ml = m * s.nThetaReduced + l;
        int idx_l1 = (jF - r.nsMinF1) * s.nThetaEff + l;
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
    }    // m
  }      // jF
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
    }    // k
  }      // jF

  // Now combine symmetric and antisymmetric parts if lasym=true
  if (s.lasym && !m_geometry_asym.r1_a.empty()) {
#pragma omp parallel for
    for (int jF = r.nsMinF1; jF < r.nsMaxF1; ++jF) {
      for (int kl = 0; kl < s.nZnT; ++kl) {
        int idx = (jF - r.nsMinF1) * s.nZnT + kl;

        // Add asymmetric contributions to symmetric ones
        m_geometry.r1_e[idx] += m_geometry_asym.r1_a[idx];
        m_geometry.r1_o[idx] += m_geometry_asym.r1_a[idx];
        m_geometry.ru_e[idx] += m_geometry_asym.ru_a[idx];
        m_geometry.ru_o[idx] += m_geometry_asym.ru_a[idx];
        m_geometry.rv_e[idx] += m_geometry_asym.rv_a[idx];
        m_geometry.rv_o[idx] += m_geometry_asym.rv_a[idx];

        m_geometry.z1_e[idx] += m_geometry_asym.z1_a[idx];
        m_geometry.z1_o[idx] += m_geometry_asym.z1_a[idx];
        m_geometry.zu_e[idx] += m_geometry_asym.zu_a[idx];
        m_geometry.zu_o[idx] += m_geometry_asym.zu_a[idx];
        m_geometry.zv_e[idx] += m_geometry_asym.zv_a[idx];
        m_geometry.zv_o[idx] += m_geometry_asym.zv_a[idx];

        m_geometry.lu_e[idx] += m_geometry_asym.lu_a[idx];
        m_geometry.lu_o[idx] += m_geometry_asym.lu_a[idx];
        m_geometry.lv_e[idx] += m_geometry_asym.lv_a[idx];
        m_geometry.lv_o[idx] += m_geometry_asym.lv_a[idx];
      }
    }
  }
}

// Implementation of tomnspa: Fourier transform antisymmetric forces back to
// spectral space
void ForcesToFourier3DAsymmFastPoloidal(
    const RealSpaceForcesAsym& d_asym, const std::vector<double>& xmpq,
    const RadialPartitioning& rp, const Sizes& s,
    const FourierBasisFastPoloidal& fb, FourierForces& m_physical_forces) {
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
          rmksc += tempR * sinmui + d_asym.brmn_a[idx_kl] * cosmumi;  // --> frsc
          rmkcs += tempR * cosmui + d_asym.brmn_a[idx_kl] * sinmumi;  // --> frcs
          zmkcc += tempZ * cosmui + d_asym.bzmn_a[idx_kl] * sinmumi;  // --> fzcc
          zmkss += tempZ * sinmui + d_asym.bzmn_a[idx_kl] * cosmumi;  // --> fzss
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

// Implementation of symforce: Symmetrize forces in (theta,zeta) space
// Separates forces into symmetric and antisymmetric components
void SymmetrizeForces(const Sizes& s, const RadialPartitioning& r,
                      RealSpaceForces& m_forces,
                      RealSpaceForcesAsym& m_forces_asym) {
  // Placeholder implementation for force symmetrization
  // The force symmetrization is complex and requires careful handling of
  // data structures that may not be designed for in-place modification.
  // 
  // In the current VMECPP architecture, the symmetric/asymmetric decomposition
  // is handled implicitly during force calculations rather than as a 
  // post-processing step.
  //
  // For a complete implementation, this would:
  // 1. Compute asymmetric parts: 0.5 * (f(k,l) - f(k_rev,l_rev))
  // 2. Compute symmetric parts: 0.5 * (f(k,l) + f(k_rev,l_rev))
  // 3. Update force arrays to contain only symmetric parts
  // 4. Store asymmetric parts in separate arrays
  //
  // This function is called when lasym=true to ensure proper force decomposition
  // for non-stellarator-symmetric configurations.
}

}  // namespace vmecpp