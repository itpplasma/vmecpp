// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT
#ifndef VMECPP_VMEC_IDEAL_MHD_MODEL_FOURIER_ASYMMETRIC_H_
#define VMECPP_VMEC_IDEAL_MHD_MODEL_FOURIER_ASYMMETRIC_H_

#include <span>
#include <vector>

#include "vmecpp/common/fourier_basis_fast_poloidal/fourier_basis_fast_poloidal.h"
#include "vmecpp/common/sizes/sizes.h"
#include "vmecpp/vmec/fourier_forces/fourier_forces.h"
#include "vmecpp/vmec/fourier_geometry/fourier_geometry.h"
#include "vmecpp/vmec/ideal_mhd_model/dft_data.h"
#include "vmecpp/vmec/radial_partitioning/radial_partitioning.h"
#include "vmecpp/vmec/radial_profiles/radial_profiles.h"

namespace vmecpp {

// Structure to hold asymmetric real-space geometry arrays
struct RealSpaceGeometryAsym {
  std::span<double> r1_a;  // R asymmetric part
  std::span<double> ru_a;  // dR/du asymmetric part
  std::span<double> rv_a;  // dR/dv asymmetric part
  std::span<double> z1_a;  // Z asymmetric part
  std::span<double> zu_a;  // dZ/du asymmetric part
  std::span<double> zv_a;  // dZ/dv asymmetric part
  std::span<double> lu_a;  // dlambda/du asymmetric part
  std::span<double> lv_a;  // dlambda/dv asymmetric part
};

// Structure to hold asymmetric real-space force arrays
struct RealSpaceForcesAsym {
  std::span<const double> armn_a;  // R force asymmetric part
  std::span<const double> azmn_a;  // Z force asymmetric part
  std::span<const double> blmn_a;  // lambda force asymmetric part
  std::span<const double> brmn_a;  // R force asymmetric part
  std::span<const double> bzmn_a;  // Z force asymmetric part
  std::span<const double> clmn_a;  // lambda force asymmetric part
  std::span<const double> crmn_a;  // R force asymmetric part
  std::span<const double> czmn_a;  // Z force asymmetric part
};

// totzspa: Fourier transform for anti-symmetric contributions
// Transforms asymmetric Fourier coefficients to real space
void FourierToReal3DAsymmFastPoloidal(const FourierGeometry& physical_x,
                                      const std::vector<double>& xmpq,
                                      const RadialPartitioning& r,
                                      const Sizes& s, const RadialProfiles& rp,
                                      const FourierBasisFastPoloidal& fb,
                                      RealSpaceGeometryAsym& m_geometry_asym);

void FourierToReal2DAsymmFastPoloidal(const FourierGeometry& physical_x,
                                      const std::vector<double>& xmpq,
                                      const RadialPartitioning& r,
                                      const Sizes& s, const RadialProfiles& rp,
                                      const FourierBasisFastPoloidal& fb,
                                      RealSpaceGeometryAsym& m_geometry_asym);

// symrzl: Symmetrize/antisymmetrize real-space quantities on extended theta
// interval Extends geometry from [0,pi] to [0,2pi] using symmetry operations
void SymmetrizeRealSpaceGeometry(const Sizes& s, const RadialPartitioning& r,
                                 RealSpaceGeometry& m_geometry,
                                 RealSpaceGeometryAsym& m_geometry_asym);

// tomnspa: Fourier transform antisymmetric forces back to spectral space
void ForcesToFourier3DAsymmFastPoloidal(const RealSpaceForcesAsym& d_asym,
                                        const std::vector<double>& xmpq,
                                        const RadialPartitioning& rp,
                                        const Sizes& s,
                                        const FourierBasisFastPoloidal& fb,
                                        FourierForces& m_physical_forces);

void ForcesToFourier2DAsymmFastPoloidal(const RealSpaceForcesAsym& d_asym,
                                        const std::vector<double>& xmpq,
                                        const RadialPartitioning& rp,
                                        const Sizes& s,
                                        const FourierBasisFastPoloidal& fb,
                                        FourierForces& m_physical_forces);

// symforce: Symmetrize forces in (theta,zeta) space
// Separates forces into symmetric and antisymmetric components
void SymmetrizeForces(const Sizes& s, const RadialPartitioning& r,
                      RealSpaceForces& m_forces,
                      RealSpaceForcesAsym& m_forces_asym);

}  // namespace vmecpp

#endif  // VMECPP_VMEC_IDEAL_MHD_MODEL_FOURIER_ASYMMETRIC_H_
