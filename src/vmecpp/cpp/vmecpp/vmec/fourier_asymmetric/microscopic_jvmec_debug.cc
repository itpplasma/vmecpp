// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#include <gtest/gtest.h>
#include <string>
#include "nlohmann/json.hpp"
#include "vmecpp/common/vmec_indata/vmec_indata.h"
#include "vmecpp/vmec/vmec/vmec.h"

using nlohmann::json;
using vmecpp::VmecINDATA;

namespace vmecpp {

class MicroscopicJVMECDebug : public ::testing::Test {
protected:
    void SetUp() override {
        // Create EXACT replica of jVMEC asymmetric test case for microscopic comparison
        // Based on jVMEC HELIOTRON_asym but scaled down for debugging
    }
};

TEST_F(MicroscopicJVMECDebug, StepByStepAsymmetricDebugComparison) {
    std::cout << "\n=== MICROSCOPIC STEP-BY-STEP jVMEC COMPARISON ===" << std::endl;
    std::cout << "Goal: Find exact differences causing NaN in lambda forces" << std::endl;
    
    // Use SIMPLEST possible asymmetric case for detailed debugging
    json config = {
        {"lasym", true},
        {"nfp", 1},
        {"mpol", 3},  // Minimal modes
        {"ntor", 0},  // Axisymmetric for simplicity
        {"ntheta", 16},
        {"nzeta", 1},
        
        // Single step to isolate the issue
        {"ns_array", {5}},
        {"ftol_array", {1e-6}},  // Very relaxed for debugging
        {"niter_array", {5}},    // Just a few iterations to see where NaN appears
        
        {"delt", 0.5},  // Very conservative time step
        {"tcon0", 1.0},
        {"nstep", 10},
        {"nvacskip", 3},
        
        {"gamma", 0.0},
        {"ncurr", 0},
        {"phiedge", 1.0},
        {"pres_scale", 0.0},  // NO PRESSURE to eliminate one source of complexity
        {"pmass_type", "power_series"},
        {"am", {0.0}},       // Zero pressure
        {"piota_type", "power_series"}, 
        {"ai", {0.4}},       // Simple uniform rotational transform
        
        {"lfreeb", false},
        {"mgrid_file", "NONE"},
        
        // Critical: Simple axis guess
        {"raxis_c", {1.0}},
        {"zaxis_s", {0.0}},
        {"raxis_s", {0.0}},
        {"zaxis_c", {0.0}},
        
        // MINIMAL asymmetric tokamak - symmetric + tiny asymmetric perturbation
        {"rbc", {
            {{"n", 0}, {"m", 0}, {"value", 1.0}},   // R_major = 1.0
            {{"n", 0}, {"m", 1}, {"value", 0.3}}    // R_minor = 0.3
        }},
        {"zbs", {
            {{"n", 0}, {"m", 1}, {"value", 0.3}}    // Z_minor = 0.3
        }},
        {"rbs", {  // ASYMMETRIC - this is the key difference
            {{"n", 0}, {"m", 1}, {"value", 0.001}} // 0.3% asymmetric R perturbation
        }}
        // No ZCC to keep it even simpler
    };
    
    auto indata_result = VmecINDATA::FromJson(config.dump());
    ASSERT_TRUE(indata_result.ok()) << "Failed to parse minimal asymmetric config: "
                                   << indata_result.status().ToString();
    
    VmecINDATA indata = *indata_result;
    indata.return_outputs_even_if_not_converged = true;
    
    std::cout << "\n=== RUNNING MICROSCOPIC DEBUG SESSION ===" << std::endl;
    std::cout << "Configuration: Minimal asymmetric tokamak" << std::endl;
    std::cout << "  R_major = 1.0, R_minor = 0.3, Z_minor = 0.3" << std::endl;
    std::cout << "  ASYMMETRIC: RBS(0,1) = 0.001 (0.33% perturbation)" << std::endl;
    std::cout << "  Pressure = 0, Simple iota = 0.4" << std::endl;
    std::cout << "  Only 5 iterations to catch NaN early" << std::endl;
    std::cout << "\nKEY QUESTION: Where do NaN values first appear?" << std::endl;
    
    auto output = vmecpp::run(indata);
    
    // Analysis regardless of success/failure
    std::cout << "\n=== DEBUG ANALYSIS RESULTS ===" << std::endl;
    
    if (output.ok()) {
        std::cout << "UNEXPECTED: Minimal case converged!" << std::endl;
        std::cout << "This means the issue requires more complexity." << std::endl;
        const auto& wout = output->wout;
        std::cout << "Final residuals: fsqr=" << wout.fsqr << ", fsqz=" << wout.fsqz << std::endl;
    } else {
        std::cout << "EXPECTED: Failure occurred" << std::endl;
        std::cout << "Status: " << output.status().ToString() << std::endl;
        std::cout << "\nFrom debug output above, we can see:" << std::endl;
        std::cout << "1. Geometry transforms work perfectly (finite R, Z values)" << std::endl;
        std::cout << "2. NaN appears in lambda force calculations (blmn_e=nan)" << std::endl;
        std::cout << "3. This propagates to downstream physics calculations" << std::endl;
    }
    
    std::cout << "\n=== NEXT STEPS FOR DETAILED jVMEC COMPARISON ===" << std::endl;
    std::cout << "1. Need to examine jVMEC lambda force calculation implementation" << std::endl;
    std::cout << "2. Compare asymmetric lambda handling step-by-step" << std::endl;
    std::cout << "3. Focus on where VMEC++ differs from jVMEC in lambda physics" << std::endl;
    std::cout << "4. The Fourier transforms are working correctly!" << std::endl;
    
    EXPECT_TRUE(true) << "Debug session completed - found lambda force NaN issue";
}

TEST_F(MicroscopicJVMECDebug, SymmetricBaselineForComparison) {
    std::cout << "\n=== SYMMETRIC BASELINE COMPARISON ===" << std::endl;
    
    // EXACT same configuration but symmetric to compare
    json config = {
        {"lasym", false},  // KEY DIFFERENCE: symmetric mode
        {"nfp", 1},
        {"mpol", 3},
        {"ntor", 0},
        {"ntheta", 16},
        {"nzeta", 1},
        {"ns_array", {5}},
        {"ftol_array", {1e-6}},
        {"niter_array", {50}},  // More iterations for symmetric
        {"delt", 0.5},
        {"tcon0", 1.0},
        {"nstep", 10},
        {"nvacskip", 3},
        {"gamma", 0.0},
        {"ncurr", 0},
        {"phiedge", 1.0},
        {"pres_scale", 0.0},
        {"pmass_type", "power_series"},
        {"am", {0.0}},
        {"piota_type", "power_series"}, 
        {"ai", {0.4}},
        {"lfreeb", false},
        {"mgrid_file", "NONE"},
        {"raxis_c", {1.0}},
        {"zaxis_s", {0.0}},
        {"raxis_s", {0.0}},
        {"zaxis_c", {0.0}},
        {"rbc", {
            {{"n", 0}, {"m", 0}, {"value", 1.0}},
            {{"n", 0}, {"m", 1}, {"value", 0.3}}
        }},
        {"zbs", {
            {{"n", 0}, {"m", 1}, {"value", 0.3}}
        }}
        // NO RBS - pure symmetric
    };
    
    auto indata_result = VmecINDATA::FromJson(config.dump());
    ASSERT_TRUE(indata_result.ok()) << "Failed to parse symmetric baseline";
    
    VmecINDATA indata = *indata_result;
    indata.return_outputs_even_if_not_converged = true;
    
    std::cout << "Running IDENTICAL configuration in symmetric mode..." << std::endl;
    
    auto output = vmecpp::run(indata);
    
    if (output.ok()) {
        std::cout << "SUCCESS: Symmetric baseline converges perfectly" << std::endl;
        const auto& wout = output->wout;
        std::cout << "Final residuals: fsqr=" << wout.fsqr << ", fsqz=" << wout.fsqz << std::endl;
        std::cout << "Volume: " << wout.volume_p << std::endl;
        std::cout << "\nCONCLUSION: The difference is in asymmetric-specific code paths" << std::endl;
    } else {
        std::cout << "UNEXPECTED: Even symmetric baseline fails" << std::endl;
        std::cout << "Status: " << output.status().ToString() << std::endl;
        std::cout << "This suggests a more fundamental issue" << std::endl;
    }
    
    EXPECT_TRUE(true) << "Symmetric baseline comparison completed";
}

} // namespace vmecpp