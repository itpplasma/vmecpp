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
        if (s.lasym) {
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
  if (s.lasym) {
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
  // TODO: Implement antisymmetric force transform
  // This will be needed for completing the force calculations with lasym=true
  // For now, this is a placeholder
}

// Implementation of symforce: Symmetrize forces in (theta,zeta) space
// Separates forces into symmetric and antisymmetric components
void SymmetrizeForces(const Sizes& s, const RadialPartitioning& r,
                      RealSpaceForces& m_forces,
                      RealSpaceForcesAsym& m_forces_asym) {
  // TODO: Implement force symmetrization
  // This separates the total forces into symmetric and antisymmetric parts
  // For now, this is a placeholder
}

}  // namespace vmecpp