// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#include <gtest/gtest.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <vector>
#include <cmath>
#include "vmecpp/vmec/fourier_asymmetric/fourier_asymmetric.h"
#include "vmecpp/common/sizes/sizes.h"

namespace vmecpp {

class DetailedJVMECComparison : public ::testing::Test {
protected:
    void SetUp() override {
        // Create identical configuration to jVMEC test case
        sizes_ = std::make_unique<Sizes>(true, 1, 3, 0, 16, 1);
        sizes_->nThetaReduced = sizes_->nThetaEff / 2 + 1; // 9
        sizes_->nZnT = sizes_->nZeta * sizes_->nThetaEff;
        sizes_->mnmax = sizes_->mpol * (2 * sizes_->ntor + 1); // 3 * 1 = 3
        
        std::cout << "Setup: mpol=" << sizes_->mpol << ", ntor=" << sizes_->ntor 
                  << ", nThetaEff=" << sizes_->nThetaEff 
                  << ", nThetaReduced=" << sizes_->nThetaReduced
                  << ", mnmax=" << sizes_->mnmax << std::endl;
    }

    std::unique_ptr<Sizes> sizes_;
};

TEST_F(DetailedJVMECComparison, Step1_CoefficientsInput) {
    std::cout << "\n=== STEP 1: COEFFICIENT INPUT COMPARISON ===" << std::endl;
    
    // Set up boundary coefficients EXACTLY like jVMEC test case
    std::vector<double> rmncc(sizes_->mnmax, 0.0);
    std::vector<double> rmnsc(sizes_->mnmax, 0.0);
    std::vector<double> zmnsc(sizes_->mnmax, 0.0);
    std::vector<double> zmncc(sizes_->mnmax, 0.0);
    
    // Mode indexing: mn = m * (2*ntor + 1) + (ntor + n)
    // For ntor=0: mn = m for n=0
    
    // Mode (m=0, n=0): Major radius
    rmncc[0] = 1.0;  // R_major = 1.0
    
    // Mode (m=1, n=0): Minor radius  
    rmncc[1] = 0.3;  // Symmetric R_minor
    zmnsc[1] = 0.3;  // Symmetric Z_minor
    
    // ASYMMETRIC perturbations
    rmnsc[1] = 0.01;  // 1% asymmetric R perturbation 
    zmncc[1] = 0.005; // 0.5% asymmetric Z perturbation
    
    std::cout << "Input coefficients (VMEC++ format):" << std::endl;
    for (int mn = 0; mn < sizes_->mnmax; ++mn) {
        std::cout << "  mn=" << mn << ": rmncc=" << rmncc[mn] 
                  << ", rmnsc=" << rmnsc[mn]
                  << ", zmnsc=" << zmnsc[mn] 
                  << ", zmncc=" << zmncc[mn] << std::endl;
    }
    
    // TODO: Create jVMEC input file with identical coefficients
    std::ofstream jvmec_input("/home/ert/code/vmecpp/jvmec_comparison_input.txt");
    jvmec_input << "# jVMEC input file for detailed comparison\n";
    jvmec_input << "mpol = " << sizes_->mpol << "\n";
    jvmec_input << "ntor = " << sizes_->ntor << "\n";
    jvmec_input << "nfp = " << sizes_->nfp << "\n";
    jvmec_input << "lasym = true\n";
    jvmec_input << "ns = 5\n";
    jvmec_input << "ftol = 1e-12\n";
    jvmec_input << "niter = 50\n";
    jvmec_input << "\n# Boundary coefficients\n";
    jvmec_input << "rmncc[0][0] = " << rmncc[0] << "\n";
    jvmec_input << "rmncc[1][0] = " << rmncc[1] << "\n"; 
    jvmec_input << "rmnsc[1][0] = " << rmnsc[1] << "\n";
    jvmec_input << "zmnsc[1][0] = " << zmnsc[1] << "\n";
    jvmec_input << "zmncc[1][0] = " << zmncc[1] << "\n";
    jvmec_input.close();
    
    std::cout << "Created jVMEC input file: jvmec_comparison_input.txt" << std::endl;
}

TEST_F(DetailedJVMECComparison, Step2_ForwardTransformDetailed) {
    std::cout << "\n=== STEP 2: FORWARD TRANSFORM STEP-BY-STEP ===" << std::endl;
    
    // Set up test coefficients
    std::vector<double> rmncc(sizes_->mnmax, 0.0);
    std::vector<double> rmnss(sizes_->mnmax, 0.0);
    std::vector<double> rmnsc(sizes_->mnmax, 0.0);
    std::vector<double> rmncs(sizes_->mnmax, 0.0);
    std::vector<double> zmnsc(sizes_->mnmax, 0.0);
    std::vector<double> zmncs(sizes_->mnmax, 0.0);
    std::vector<double> zmncc(sizes_->mnmax, 0.0);
    std::vector<double> zmnss(sizes_->mnmax, 0.0);
    std::vector<double> lmnsc(sizes_->mnmax, 0.0);
    std::vector<double> lmncc(sizes_->mnmax, 0.0);
    
    // Simple test case
    rmncc[0] = 1.0;   // Major radius
    rmncc[1] = 0.3;   // Symmetric minor radius
    rmnsc[1] = 0.01;  // TINY asymmetric perturbation
    zmnsc[1] = 0.3;   // Symmetric Z
    zmncc[1] = 0.005; // TINY asymmetric Z perturbation
    
    // Output arrays
    std::vector<double> r_real(sizes_->nZnT, 0.0);
    std::vector<double> z_real(sizes_->nZnT, 0.0);
    std::vector<double> lambda_real(sizes_->nZnT, 0.0);
    
    std::cout << "BEFORE transform - Input coefficients:" << std::endl;
    std::cout << "  rmncc[0]=" << rmncc[0] << ", rmncc[1]=" << rmncc[1] << std::endl;
    std::cout << "  rmnsc[1]=" << rmnsc[1] << std::endl;
    std::cout << "  zmnsc[1]=" << zmnsc[1] << ", zmncc[1]=" << zmncc[1] << std::endl;
    
    // STEP 1: Apply symmetric baseline manually (simple 2D case)
    std::cout << "\nSTEP 1: Apply symmetric baseline..." << std::endl;
    for (int i = 0; i < sizes_->nThetaEff; ++i) {
        double theta = 2.0 * M_PI * i / sizes_->nThetaEff;
        
        // Apply symmetric coefficients: R ~ rmncc*cos(m*theta), Z ~ zmnsc*sin(m*theta)
        double R_symm = rmncc[0];  // m=0: R_major
        double Z_symm = 0.0;
        
        // m=1 symmetric contributions
        R_symm += rmncc[1] * cos(1.0 * theta);  // rmncc[1]*cos(theta)
        Z_symm += zmnsc[1] * sin(1.0 * theta);  // zmnsc[1]*sin(theta)
        
        for (int k = 0; k < sizes_->nZeta; ++k) {
            int idx = i * sizes_->nZeta + k;
            if (idx < r_real.size()) {
                r_real[idx] = R_symm;
                z_real[idx] = Z_symm;
                lambda_real[idx] = 0.0;
            }
        }
    }
    
    std::cout << "AFTER symmetric baseline (first 8 points):" << std::endl;
    for (int i = 0; i < std::min(8, static_cast<int>(r_real.size())); ++i) {
        double theta = 2.0 * M_PI * i / sizes_->nThetaEff;
        std::cout << "  i=" << i << ", theta=" << std::fixed << std::setprecision(6) << theta 
                  << ": R=" << r_real[i] << ", Z=" << z_real[i] << std::endl;
    }
    
    // STEP 2: Apply asymmetric transform on top of symmetric baseline
    std::cout << "\nSTEP 2: Calling VMEC++ FourierToReal2DAsymmFastPoloidal..." << std::endl;
    
    FourierToReal2DAsymmFastPoloidal(
        *sizes_,
        absl::MakeConstSpan(rmncc),
        absl::MakeConstSpan(rmnss),
        absl::MakeConstSpan(rmnsc),
        absl::MakeConstSpan(rmncs),
        absl::MakeConstSpan(zmnsc),
        absl::MakeConstSpan(zmncs),
        absl::MakeConstSpan(zmncc),
        absl::MakeConstSpan(zmnss),
        absl::MakeSpan(r_real),
        absl::MakeSpan(z_real),
        absl::MakeSpan(lambda_real)
    );
    
    std::cout << "AFTER transform - Real space values (first 8 points):" << std::endl;
    for (int i = 0; i < std::min(8, static_cast<int>(r_real.size())); ++i) {
        double theta = 2.0 * M_PI * i / sizes_->nThetaEff;
        std::cout << "  i=" << i << ", theta=" << std::fixed << std::setprecision(6) << theta 
                  << ": R=" << r_real[i] << ", Z=" << z_real[i] << std::endl;
    }
    
    // TODO: Compare with jVMEC totzspa output
    std::cout << "\nTODO: Run jVMEC with identical input and compare real space values" << std::endl;
    std::cout << "Expected pattern: R should be ~1.0 ± minor variations" << std::endl;
    std::cout << "                  Z should show asymmetric pattern around ±0.3" << std::endl;
}

TEST_F(DetailedJVMECComparison, Step3_SymmetrizationDetailed) {
    std::cout << "\n=== STEP 3: SYMMETRIZATION STEP-BY-STEP ===" << std::endl;
    
    // Create asymmetric real space data for testing symmetrization
    std::vector<double> r_real(sizes_->nZnT, 0.0);
    std::vector<double> z_real(sizes_->nZnT, 0.0);
    std::vector<double> lambda_real(sizes_->nZnT, 0.0);
    
    // Fill with test pattern - asymmetric data for theta=[0,pi]
    for (int i = 0; i < sizes_->nThetaReduced; ++i) {
        double theta = M_PI * i / (sizes_->nThetaReduced - 1);
        r_real[i] = 1.0 + 0.3 * cos(theta) + 0.01 * sin(theta);  // R = major + minor + asymmetric
        z_real[i] = 0.3 * sin(theta) + 0.005 * cos(theta);       // Z = symmetric + asymmetric
        lambda_real[i] = 0.0;
    }
    
    std::cout << "BEFORE symmetrization (theta=[0,pi] only):" << std::endl;
    for (int i = 0; i < sizes_->nThetaReduced; ++i) {
        double theta = M_PI * i / (sizes_->nThetaReduced - 1);
        std::cout << "  i=" << i << ", theta=" << std::fixed << std::setprecision(4) << theta 
                  << ": R=" << r_real[i] << ", Z=" << z_real[i] << std::endl;
    }
    
    // Call VMEC++ symmetrization
    std::cout << "\nCalling VMEC++ SymmetrizeRealSpaceGeometry..." << std::endl;
    
    SymmetrizeRealSpaceGeometry(
        *sizes_,
        absl::MakeSpan(r_real),
        absl::MakeSpan(z_real),
        absl::MakeSpan(lambda_real)
    );
    
    std::cout << "AFTER symmetrization (full theta=[0,2pi]):" << std::endl;
    for (int i = 0; i < sizes_->nThetaEff; ++i) {
        double theta = 2.0 * M_PI * i / sizes_->nThetaEff;
        std::cout << "  i=" << i << ", theta=" << std::fixed << std::setprecision(4) << theta 
                  << ": R=" << r_real[i] << ", Z=" << z_real[i] << std::endl;
    }
    
    // Verify symmetrization properties
    std::cout << "\nSymmetrization verification:" << std::endl;
    for (int i = 0; i < sizes_->nThetaReduced - 1; ++i) {
        int ir = sizes_->nThetaEff - 1 - i;  // Reflection index
        double r_diff = std::abs(r_real[i] - r_real[ir]);
        double z_diff = std::abs(z_real[i] + z_real[ir]);  // Z should be antisymmetric
        std::cout << "  i=" << i << ", ir=" << ir 
                  << ": |R[i] - R[ir]|=" << r_diff 
                  << ", |Z[i] + Z[ir]|=" << z_diff << std::endl;
    }
    
    // TODO: Compare with jVMEC symrzl implementation
    std::cout << "\nTODO: Compare symmetrization with jVMEC symrzl function" << std::endl;
    std::cout << "jVMEC reflection: kr = (nzeta - k) % nzeta, lr = ntheta1 - l" << std::endl;
}

TEST_F(DetailedJVMECComparison, Step4_InverseTransformDetailed) {
    std::cout << "\n=== STEP 4: INVERSE TRANSFORM STEP-BY-STEP ===" << std::endl;
    
    // Create known real space pattern
    std::vector<double> r_real(sizes_->nZnT, 0.0);
    std::vector<double> z_real(sizes_->nZnT, 0.0);
    std::vector<double> lambda_real(sizes_->nZnT, 0.0);
    
    // Create symmetric + asymmetric pattern
    for (int i = 0; i < sizes_->nThetaEff; ++i) {
        double theta = 2.0 * M_PI * i / sizes_->nThetaEff;
        r_real[i] = 1.0 + 0.3 * cos(theta) + 0.01 * sin(theta);  // Known pattern
        z_real[i] = 0.3 * sin(theta) + 0.005 * cos(theta);       // Known pattern
    }
    
    std::cout << "Input real space (first 8 points):" << std::endl;
    for (int i = 0; i < 8; ++i) {
        double theta = 2.0 * M_PI * i / sizes_->nThetaEff;
        std::cout << "  i=" << i << ", theta=" << theta 
                  << ": R=" << r_real[i] << ", Z=" << z_real[i] << std::endl;
    }
    
    // Output coefficient arrays
    std::vector<double> rmncc(sizes_->mnmax, 0.0);
    std::vector<double> rmnss(sizes_->mnmax, 0.0);
    std::vector<double> rmnsc(sizes_->mnmax, 0.0);
    std::vector<double> rmncs(sizes_->mnmax, 0.0);
    std::vector<double> zmnsc(sizes_->mnmax, 0.0);
    std::vector<double> zmncs(sizes_->mnmax, 0.0);
    std::vector<double> zmncc(sizes_->mnmax, 0.0);
    std::vector<double> zmnss(sizes_->mnmax, 0.0);
    std::vector<double> lmnsc(sizes_->mnmax, 0.0);
    std::vector<double> lmncs(sizes_->mnmax, 0.0);
    std::vector<double> lmncc(sizes_->mnmax, 0.0);
    std::vector<double> lmnss(sizes_->mnmax, 0.0);
    
    // Call VMEC++ inverse transform
    std::cout << "\nCalling VMEC++ RealToFourier2DAsymmFastPoloidal..." << std::endl;
    
    RealToFourier2DAsymmFastPoloidal(
        *sizes_,
        absl::MakeConstSpan(r_real),
        absl::MakeConstSpan(z_real),
        absl::MakeConstSpan(lambda_real),
        absl::MakeSpan(rmncc),
        absl::MakeSpan(rmnss),
        absl::MakeSpan(rmnsc),
        absl::MakeSpan(rmncs),
        absl::MakeSpan(zmnsc),
        absl::MakeSpan(zmncs),
        absl::MakeSpan(zmncc),
        absl::MakeSpan(zmnss),
        absl::MakeSpan(lmnsc),
        absl::MakeSpan(lmncs),
        absl::MakeSpan(lmncc),
        absl::MakeSpan(lmnss)
    );
    
    std::cout << "Output coefficients:" << std::endl;
    for (int mn = 0; mn < sizes_->mnmax; ++mn) {
        std::cout << "  mn=" << mn << ": rmncc=" << rmncc[mn] 
                  << ", rmnsc=" << rmnsc[mn]
                  << ", zmnsc=" << zmnsc[mn] 
                  << ", zmncc=" << zmncc[mn] << std::endl;
    }
    
    // Expected values for verification
    std::cout << "\nExpected coefficients (analytical):" << std::endl;
    std::cout << "  rmncc[0] ≈ 1.0 (major radius)" << std::endl;
    std::cout << "  rmncc[1] ≈ 0.3 (symmetric minor radius)" << std::endl;
    std::cout << "  rmnsc[1] ≈ 0.01 (asymmetric R perturbation)" << std::endl;
    std::cout << "  zmnsc[1] ≈ 0.3 (symmetric Z)" << std::endl;
    std::cout << "  zmncc[1] ≈ 0.005 (asymmetric Z perturbation)" << std::endl;
    
    // TODO: Compare with jVMEC tomnspa implementation
    std::cout << "\nTODO: Compare inverse transform with jVMEC tomnspa function" << std::endl;
    std::cout << "jVMEC uses theta integration over [0,π] only for asymmetric case" << std::endl;
}

} // namespace vmecpp