// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#include <gtest/gtest.h>
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include "vmecpp/vmec/fourier_asymmetric/fourier_asymmetric.h"
#include "vmecpp/common/sizes/sizes.h"

namespace vmecpp {

TEST(RoundtripTest, AsymmetricTransformRoundtrip) {
    std::cout << "\n=== ASYMMETRIC TRANSFORM ROUND-TRIP TEST ===" << std::endl;
    
    // Simple test configuration
    Sizes sizes(true, 1, 3, 0, 16, 1);  // lasym=true, nfp=1, mpol=3, ntor=0, ntheta=16, nzeta=1
    
    std::cout << "Setup: mpol=" << sizes.mpol << ", ntor=" << sizes.ntor 
              << ", nThetaEff=" << sizes.nThetaEff 
              << ", nThetaReduced=" << sizes.nThetaReduced
              << ", mnmax=" << sizes.mnmax << std::endl;
    
    // STEP 1: Set up known input coefficients
    std::vector<double> rmncc_in(sizes.mnmax, 0.0);
    std::vector<double> rmnss_in(sizes.mnmax, 0.0);
    std::vector<double> rmnsc_in(sizes.mnmax, 0.0);
    std::vector<double> rmncs_in(sizes.mnmax, 0.0);
    std::vector<double> zmnsc_in(sizes.mnmax, 0.0);
    std::vector<double> zmncs_in(sizes.mnmax, 0.0);
    std::vector<double> zmncc_in(sizes.mnmax, 0.0);
    std::vector<double> zmnss_in(sizes.mnmax, 0.0);
    std::vector<double> lmnsc_in(sizes.mnmax, 0.0);
    std::vector<double> lmncs_in(sizes.mnmax, 0.0);
    std::vector<double> lmncc_in(sizes.mnmax, 0.0);
    std::vector<double> lmnss_in(sizes.mnmax, 0.0);
    
    // Set simple test values
    rmncc_in[0] = 1.0;   // Major radius
    rmncc_in[1] = 0.3;   // Symmetric minor radius
    rmnsc_in[1] = 0.01;  // Asymmetric R perturbation
    zmnsc_in[1] = 0.3;   // Symmetric Z
    zmncc_in[1] = 0.005; // Asymmetric Z perturbation
    
    std::cout << "Input coefficients:" << std::endl;
    for (int mn = 0; mn < sizes.mnmax; ++mn) {
        std::cout << "  mn=" << mn << ": rmncc=" << rmncc_in[mn] 
                  << ", rmnsc=" << rmnsc_in[mn]
                  << ", zmnsc=" << zmnsc_in[mn] 
                  << ", zmncc=" << zmncc_in[mn] << std::endl;
    }
    
    // STEP 2: Forward transform to real space
    std::vector<double> r_real(sizes.nZnT, 0.0);
    std::vector<double> z_real(sizes.nZnT, 0.0);
    std::vector<double> lambda_real(sizes.nZnT, 0.0);
    
    // First apply symmetric baseline manually
    for (int i = 0; i < sizes.nThetaEff; ++i) {
        double theta = 2.0 * M_PI * i / sizes.nThetaEff;
        
        double R_symm = rmncc_in[0] + rmncc_in[1] * cos(1.0 * theta);
        double Z_symm = zmnsc_in[1] * sin(1.0 * theta);
        
        for (int k = 0; k < sizes.nZeta; ++k) {
            int idx = i * sizes.nZeta + k;
            if (idx < static_cast<int>(r_real.size())) {
                r_real[idx] = R_symm;
                z_real[idx] = Z_symm;
                lambda_real[idx] = 0.0;
            }
        }
    }
    
    // Then apply asymmetric transform
    FourierToReal2DAsymmFastPoloidal(
        sizes,
        absl::MakeConstSpan(rmncc_in),
        absl::MakeConstSpan(rmnss_in),
        absl::MakeConstSpan(rmnsc_in),
        absl::MakeConstSpan(rmncs_in),
        absl::MakeConstSpan(zmnsc_in),
        absl::MakeConstSpan(zmncs_in),
        absl::MakeConstSpan(zmncc_in),
        absl::MakeConstSpan(zmnss_in),
        absl::MakeSpan(r_real),
        absl::MakeSpan(z_real),
        absl::MakeSpan(lambda_real)
    );
    
    std::cout << "\nReal space (first 4 points):" << std::endl;
    for (int i = 0; i < std::min(4, static_cast<int>(r_real.size())); ++i) {
        double theta = 2.0 * M_PI * i / sizes.nThetaEff;
        std::cout << "  i=" << i << ", theta=" << std::fixed << std::setprecision(4) << theta 
                  << ": R=" << r_real[i] << ", Z=" << z_real[i] << std::endl;
    }
    
    // STEP 3: Inverse transform back to coefficients
    std::vector<double> rmncc_out(sizes.mnmax, 0.0);
    std::vector<double> rmnss_out(sizes.mnmax, 0.0);
    std::vector<double> rmnsc_out(sizes.mnmax, 0.0);
    std::vector<double> rmncs_out(sizes.mnmax, 0.0);
    std::vector<double> zmnsc_out(sizes.mnmax, 0.0);
    std::vector<double> zmncs_out(sizes.mnmax, 0.0);
    std::vector<double> zmncc_out(sizes.mnmax, 0.0);
    std::vector<double> zmnss_out(sizes.mnmax, 0.0);
    std::vector<double> lmnsc_out(sizes.mnmax, 0.0);
    std::vector<double> lmncs_out(sizes.mnmax, 0.0);
    std::vector<double> lmncc_out(sizes.mnmax, 0.0);
    std::vector<double> lmnss_out(sizes.mnmax, 0.0);
    
    RealToFourier2DAsymmFastPoloidal(
        sizes,
        absl::MakeConstSpan(r_real),
        absl::MakeConstSpan(z_real),
        absl::MakeConstSpan(lambda_real),
        absl::MakeSpan(rmncc_out),
        absl::MakeSpan(rmnss_out),
        absl::MakeSpan(rmnsc_out),
        absl::MakeSpan(rmncs_out),
        absl::MakeSpan(zmnsc_out),
        absl::MakeSpan(zmncs_out),
        absl::MakeSpan(zmncc_out),
        absl::MakeSpan(zmnss_out),
        absl::MakeSpan(lmnsc_out),
        absl::MakeSpan(lmncs_out),
        absl::MakeSpan(lmncc_out),
        absl::MakeSpan(lmnss_out)
    );
    
    std::cout << "\nOutput coefficients:" << std::endl;
    for (int mn = 0; mn < sizes.mnmax; ++mn) {
        std::cout << "  mn=" << mn << ": rmncc=" << rmncc_out[mn] 
                  << ", rmnsc=" << rmnsc_out[mn]
                  << ", zmnsc=" << zmnsc_out[mn] 
                  << ", zmncc=" << zmncc_out[mn] << std::endl;
    }
    
    // STEP 4: Check round-trip accuracy
    std::cout << "\nRound-trip errors:" << std::endl;
    double max_error = 0.0;
    
    for (int mn = 0; mn < sizes.mnmax; ++mn) {
        double err_rmncc = std::abs(rmncc_out[mn] - rmncc_in[mn]);
        double err_rmnsc = std::abs(rmnsc_out[mn] - rmnsc_in[mn]);
        double err_zmnsc = std::abs(zmnsc_out[mn] - zmnsc_in[mn]);
        double err_zmncc = std::abs(zmncc_out[mn] - zmncc_in[mn]);
        
        max_error = std::max(max_error, std::max({err_rmncc, err_rmnsc, err_zmnsc, err_zmncc}));
        
        std::cout << "  mn=" << mn << ": |Δrmncc|=" << err_rmncc 
                  << ", |Δrmnsc|=" << err_rmnsc 
                  << ", |Δzmnsc|=" << err_zmnsc 
                  << ", |Δzmncc|=" << err_zmncc << std::endl;
    }
    
    std::cout << "\nMaximum round-trip error: " << max_error << std::endl;
    
    // Test passes if round-trip error is small
    EXPECT_LT(max_error, 0.1) << "Round-trip error too large: " << max_error;
}

} // namespace vmecpp