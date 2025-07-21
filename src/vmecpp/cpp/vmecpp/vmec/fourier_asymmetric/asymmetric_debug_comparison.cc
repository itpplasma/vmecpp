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
#include "vmecpp/vmec/vmec/vmec.h"
#include "vmecpp/common/vmec_indata/vmec_indata.h"

namespace vmecpp {

class AsymmetricDebugComparison : public ::testing::Test {
protected:
    void SetUp() override {
        // Create minimal asymmetric configuration for detailed debugging
        config_ = CreateMinimalAsymmetricConfig();
    }

    VmecINDATA CreateMinimalAsymmetricConfig() {
        VmecINDATA config;
        
        // Minimal tokamak parameters - EXACTLY match jVMEC test case
        config.nfp = 1;
        config.mpol = 3;  // Small for detailed debugging
        config.ntor = 0;
        config.ntheta = 0;
        config.nzeta = 0;
        config.lasym = true;  // ASYMMETRIC MODE
        
        // Physics parameters
        config.phiedge = 1.0;  // Simple unit values
        config.gamma = 0.0;
        config.spres_ped = 1.0;
        config.ncurr = 0;
        config.delt = 0.9;
        config.tcon0 = 1.0;
        config.nstep = 200;
        config.nvacskip = 3;
        
        // Single resolution step for debugging
        config.ns_array = {5};  // Minimal radial points
        config.ftol_array = {1e-12};  // Reasonable tolerance
        config.niter_array = {50};    // Limited iterations for debugging
        
        // Pressure profile (trivial)
        config.pmass_type = "power_series";
        config.am = {0.0};
        config.pres_scale = 1.0;
        
        // Current profile (simple)
        config.piota_type = "power_series";
        config.ai = {0.5};  // Simple iota profile
        
        // Fixed boundary
        config.lfreeb = false;
        config.mgrid_file = "NONE";
        config.lforbal = false;
        
        // Axis (on-axis)
        config.raxis_c = {1.0};  // R_major = 1
        config.zaxis_s = {0.0};  // Z = 0
        config.raxis_s = {0.0};  // No asymmetric axis initially
        config.zaxis_c = {0.0};
        
        // Boundary: circular with TINY asymmetric perturbation
        // Array size: mpol * (2*ntor + 1) = 3 * 1 = 3
        config.rbc.resize(3, 0.0);
        config.zbs.resize(3, 0.0);
        config.rbs.resize(3, 0.0);  // ASYMMETRIC terms
        config.zbc.resize(3, 0.0);  // ASYMMETRIC terms
        
        // Symmetric baseline: R = 1 + 0.3*cos(theta), Z = 0.3*sin(theta) 
        config.rbc[0] = 1.0;   // m=0,n=0: R_major
        config.rbc[1] = 0.3;   // m=1,n=0: R_minor 
        config.zbs[1] = 0.3;   // m=1,n=0: Z_minor
        
        // TINY asymmetric perturbation
        config.rbs[1] = 0.01;  // m=1,n=0: 1% asymmetric R perturbation
        config.zbc[1] = 0.005; // m=1,n=0: 0.5% asymmetric Z perturbation
        
        return config;
    }

    void DebugAsymmetricStep(const std::string& step_name) {
        std::cout << "\n" << std::string(60, '=') << std::endl;
        std::cout << "DEBUGGING STEP: " << step_name << std::endl;
        std::cout << std::string(60, '=') << std::endl;
        
        try {
            Vmec vmec(config_);
            auto result = vmec.run();
            
            if (result.ok()) {
                std::cout << "✅ " << step_name << " SUCCEEDED" << std::endl;
            } else {
                std::cout << "❌ " << step_name << " FAILED: " << result.status() << std::endl;
            }
        } catch (const std::exception& e) {
            std::cout << "💥 " << step_name << " EXCEPTION: " << e.what() << std::endl;
        }
    }

    VmecINDATA config_;
};

TEST_F(AsymmetricDebugComparison, Step1_InitialConfiguration) {
    std::cout << "\n=== STEP 1: CONFIGURATION COMPARISON ===" << std::endl;
    
    std::cout << "VMEC++ Configuration:" << std::endl;
    std::cout << "  lasym = " << (config_.lasym ? "true" : "false") << std::endl;
    std::cout << "  mpol = " << config_.mpol << ", ntor = " << config_.ntor << std::endl;
    std::cout << "  ns_array = " << config_.ns_array[0] << std::endl;
    std::cout << "  ftol_array = " << std::scientific << config_.ftol_array[0] << std::endl;
    
    std::cout << "\nBoundary coefficients:" << std::endl;
    std::cout << "  Symmetric: rbc[0]=" << config_.rbc[0] << ", rbc[1]=" << config_.rbc[1] << std::endl;
    std::cout << "             zbs[1]=" << config_.zbs[1] << std::endl;
    std::cout << "  Asymmetric: rbs[1]=" << config_.rbs[1] << ", zbc[1]=" << config_.zbc[1] << std::endl;
    
    // TODO: Compare with jVMEC input file configuration
    std::cout << "\nTODO: Create identical jVMEC input file and compare configurations" << std::endl;
}

TEST_F(AsymmetricDebugComparison, Step2_BoundaryCoefficients) {
    std::cout << "\n=== STEP 2: BOUNDARY COEFFICIENT INDEXING ===" << std::endl;
    
    // Examine boundary coefficient storage and indexing
    int mpol = config_.mpol;
    int ntor = config_.ntor;
    
    std::cout << "Array sizes:" << std::endl;
    std::cout << "  Expected size: mpol * (2*ntor + 1) = " << mpol << " * " << (2*ntor + 1) << " = " << mpol * (2*ntor + 1) << std::endl;
    std::cout << "  rbc.size() = " << config_.rbc.size() << std::endl;
    std::cout << "  rbs.size() = " << config_.rbs.size() << std::endl;
    
    std::cout << "\nIndexing scheme (m,n -> index):" << std::endl;
    for (int m = 0; m < mpol; ++m) {
        for (int n = -ntor; n <= ntor; ++n) {
            int idx = m * (2*ntor + 1) + (ntor + n);
            std::cout << "  (" << m << "," << n << ") -> idx=" << idx;
            if (idx < static_cast<int>(config_.rbc.size())) {
                std::cout << ": rbc=" << config_.rbc[idx];
                if (idx < static_cast<int>(config_.rbs.size())) {
                    std::cout << ", rbs=" << config_.rbs[idx];
                }
            }
            std::cout << std::endl;
        }
    }
    
    // TODO: Compare with jVMEC boundary coefficient indexing
    std::cout << "\nTODO: Examine jVMEC boundary coefficient indexing in rbc/zbs arrays" << std::endl;
}

TEST_F(AsymmetricDebugComparison, Step3_FourierTransformSetup) {
    std::cout << "\n=== STEP 3: FOURIER TRANSFORM SETUP ===" << std::endl;
    
    // This will trigger the asymmetric transform path
    DebugAsymmetricStep("Fourier Transform Setup");
    
    // TODO: Add detailed Fourier transform debugging
    std::cout << "\nTODO: Add detailed debugging of:" << std::endl;
    std::cout << "  1. FourierToReal3DAsymmFastPoloidal input coefficients" << std::endl;
    std::cout << "  2. Real space geometry values after transform" << std::endl;
    std::cout << "  3. SymmetrizeRealSpaceGeometry operation" << std::endl;
    std::cout << "  4. Compare with jVMEC totzspa.f90 implementation" << std::endl;
}

TEST_F(AsymmetricDebugComparison, Step4_InitialGeometry) {
    std::cout << "\n=== STEP 4: INITIAL GEOMETRY GENERATION ===" << std::endl;
    
    DebugAsymmetricStep("Initial Geometry");
    
    // TODO: Detailed geometry debugging
    std::cout << "\nTODO: Compare initial geometry generation:" << std::endl;
    std::cout << "  1. R(theta) and Z(theta) values at boundary" << std::endl; 
    std::cout << "  2. Jacobian calculation and sign" << std::endl;
    std::cout << "  3. Magnetic axis position" << std::endl;
    std::cout << "  4. Compare with jVMEC geometry setup" << std::endl;
}

TEST_F(AsymmetricDebugComparison, Step5_JacobianAndForces) {
    std::cout << "\n=== STEP 5: JACOBIAN AND FORCE CALCULATION ===" << std::endl;
    
    DebugAsymmetricStep("Jacobian and Forces");
    
    // TODO: Force calculation debugging
    std::cout << "\nTODO: Compare force calculations:" << std::endl;
    std::cout << "  1. MHD force computation in ideal_mhd_model" << std::endl;
    std::cout << "  2. Asymmetric force transform (tomnspa)" << std::endl;
    std::cout << "  3. Force symmetrization" << std::endl;
    std::cout << "  4. Compare with jVMEC force calculation" << std::endl;
}

} // namespace vmecpp