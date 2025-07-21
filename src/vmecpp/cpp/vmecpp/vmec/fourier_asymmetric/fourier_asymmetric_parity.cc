// Copyright 2025 VMEC++ Contributors
//
// SPDX-License-Identifier: MIT

#include "vmecpp/vmec/fourier_asymmetric/fourier_asymmetric.h"

#include <cmath>

#include "vmecpp/common/sizes/sizes.h"
#include "vmecpp/common/fourier_basis_fast_poloidal/fourier_basis_fast_poloidal.h"

namespace vmecpp {

void FourierToReal2DAsymmFastPoloidalWithParity(
    const Sizes& sizes, absl::Span<const double> rmncc,
    absl::Span<const double> rmnss, absl::Span<const double> rmnsc,
    absl::Span<const double> rmncs, absl::Span<const double> zmnsc,
    absl::Span<const double> zmncs, absl::Span<const double> zmncc,
    absl::Span<const double> zmnss, absl::Span<double> r_even,
    absl::Span<double> r_odd, absl::Span<double> z_even,
    absl::Span<double> z_odd, absl::Span<double> lambda_even,
    absl::Span<double> lambda_odd) {
  // This function computes the inverse Fourier transform for 2D asymmetric equilibria
  // with proper separation of even and odd m-parity modes.
  
  FourierBasisFastPoloidal fourier_basis(&sizes);
  
  const int ntheta2 = sizes.nThetaReduced;  // [0, pi]
  const int ntheta1 = sizes.nThetaEff;      // [0, 2pi]
  const int nzeta = sizes.nZeta;
  
  // Initialize output arrays to zero
  std::fill(r_even.begin(), r_even.end(), 0.0);
  std::fill(r_odd.begin(), r_odd.end(), 0.0);
  std::fill(z_even.begin(), z_even.end(), 0.0);
  std::fill(z_odd.begin(), z_odd.end(), 0.0);
  std::fill(lambda_even.begin(), lambda_even.end(), 0.0);
  std::fill(lambda_odd.begin(), lambda_odd.end(), 0.0);
  
  // Temporary arrays for asymmetric contributions [0, pi] only
  std::vector<double> asym_R_even(ntheta2 * nzeta, 0.0);
  std::vector<double> asym_R_odd(ntheta2 * nzeta, 0.0);
  std::vector<double> asym_Z_even(ntheta2 * nzeta, 0.0);
  std::vector<double> asym_Z_odd(ntheta2 * nzeta, 0.0);
  
  // STEP 1: Process symmetric coefficients with m-parity separation
  for (int m = 0; m < sizes.mpol; ++m) {
    // Find mode mn for (m,n=0) in 2D case
    int mn = -1;
    for (int mn_candidate = 0; mn_candidate < sizes.mnmax; ++mn_candidate) {
      if (fourier_basis.xm[mn_candidate] == m && 
          fourier_basis.xn[mn_candidate] / sizes.nfp == 0) {
        mn = mn_candidate;
        break;
      }
    }
    if (mn < 0) continue;
    
    // Get symmetric coefficients
    double rcc = (mn < rmncc.size()) ? rmncc[mn] : 0.0;
    double zsc = (mn < zmnsc.size()) ? zmnsc[mn] : 0.0;
    
    if (std::abs(rcc) < 1e-12 && std::abs(zsc) < 1e-12) continue;
    
    // Determine m-parity: even (m=0,2,4...) or odd (m=1,3,5...)
    const bool is_even_m = (m % 2 == 0);
    
    // Compute symmetric contributions for theta=[0,pi]
    for (int l = 0; l < ntheta2; ++l) {
      double sin_mu = fourier_basis.sinmu[m * ntheta2 + l];
      double cos_mu = fourier_basis.cosmu[m * ntheta2 + l];
      
      for (int k = 0; k < nzeta; ++k) {
        int idx = l * nzeta + k;
        
        // Symmetric: R ~ cos(m*theta), Z ~ sin(m*theta)
        if (is_even_m) {
          r_even[idx] += rcc * cos_mu;
          z_even[idx] += zsc * sin_mu;
        } else {
          r_odd[idx] += rcc * cos_mu;
          z_odd[idx] += zsc * sin_mu;
        }
      }
    }
  }
  
  // STEP 2: Process asymmetric coefficients with m-parity separation
  for (int m = 0; m < sizes.mpol; ++m) {
    // Find mode mn for (m,n=0)
    int mn = -1;
    for (int mn_candidate = 0; mn_candidate < sizes.mnmax; ++mn_candidate) {
      if (fourier_basis.xm[mn_candidate] == m && 
          fourier_basis.xn[mn_candidate] / sizes.nfp == 0) {
        mn = mn_candidate;
        break;
      }
    }
    if (mn < 0) continue;
    
    // Get asymmetric coefficients
    double rsc = (mn < rmnsc.size()) ? rmnsc[mn] : 0.0;
    double zcc = (mn < zmncc.size()) ? zmncc[mn] : 0.0;
    
    if (std::abs(rsc) < 1e-12 && std::abs(zcc) < 1e-12) continue;
    
    // Determine m-parity
    const bool is_even_m = (m % 2 == 0);
    
    // Compute asymmetric contributions for theta=[0,pi]
    for (int l = 0; l < ntheta2; ++l) {
      double sin_mu = fourier_basis.sinmu[m * ntheta2 + l];
      double cos_mu = fourier_basis.cosmu[m * ntheta2 + l];
      
      for (int k = 0; k < nzeta; ++k) {
        int idx = l * nzeta + k;
        
        // Asymmetric: R ~ sin(m*theta), Z ~ cos(m*theta)
        if (is_even_m) {
          asym_R_even[idx] += rsc * sin_mu;
          asym_Z_even[idx] += zcc * cos_mu;
        } else {
          asym_R_odd[idx] += rsc * sin_mu;
          asym_Z_odd[idx] += zcc * cos_mu;
        }
      }
    }
  }
  
  // STEP 3: Add asymmetric contributions to symmetric baseline for theta=[0,pi]
  for (int idx = 0; idx < ntheta2 * nzeta; ++idx) {
    r_even[idx] += asym_R_even[idx];
    r_odd[idx] += asym_R_odd[idx];
    z_even[idx] += asym_Z_even[idx];
    z_odd[idx] += asym_Z_odd[idx];
  }
  
  // STEP 4: Apply stellarator symmetry for theta=[pi,2pi]
  for (int l = ntheta2; l < ntheta1; ++l) {
    int lr = ntheta1 - l;  // reflection index
    
    for (int k = 0; k < nzeta; ++k) {
      int kr = (nzeta - k) % nzeta;
      int idx = l * nzeta + k;
      int idx_reflect = lr * nzeta + kr;
      
      // Apply reflection formulas with asymmetric modifications
      // Even-m modes:
      r_even[idx] = r_even[idx_reflect] - asym_R_even[idx_reflect];
      z_even[idx] = -z_even[idx_reflect] + asym_Z_even[idx_reflect];
      
      // Odd-m modes:
      r_odd[idx] = r_odd[idx_reflect] - asym_R_odd[idx_reflect];
      z_odd[idx] = -z_odd[idx_reflect] + asym_Z_odd[idx_reflect];
      
      // Lambda (if needed in future)
      lambda_even[idx] = lambda_even[idx_reflect];
      lambda_odd[idx] = lambda_odd[idx_reflect];
    }
  }
}

}  // namespace vmecpp