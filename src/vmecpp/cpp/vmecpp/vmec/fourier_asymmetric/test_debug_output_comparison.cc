// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#include <gtest/gtest.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <iomanip>
#include <map>
#include <chrono>
#include "vmecpp/vmec/vmec/vmec.h"
#include "vmecpp/common/vmec_indata/vmec_indata.h"
#include "vmecpp/common/vmec_indata/boundary_from_json.h"

namespace vmecpp {

class DebugOutputComparisonTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create configurations for comparison
        base_config_ = CreateStandardCircularTokamak();
    }

    VmecINDATA CreateStandardCircularTokamak() {
        VmecINDATA config;
        
        // Basic tokamak parameters matching Educational VMEC test cases
        config.nfp = 1;
        config.mpol = 8;
        config.ntor = 0;
        config.ntheta = 0;
        config.nzeta = 0;
        config.lasym = false;
        
        // Use the same parameters as successful benchmark cases
        config.phiedge = 67.86;
        config.gamma = 0.0;
        config.spres_ped = 1.0;
        config.ncurr = 0;
        config.delt = 0.9;
        config.tcon0 = 1.0;
        config.nstep = 200;
        config.nvacskip = 3;
        
        // Pressure profile (power series)
        config.pmass_type = "power_series";
        config.am = {0.0};
        config.pres_scale = 1.0;
        
        // Current profile (power series) 
        config.piota_type = "power_series";
        config.ai = {0.9, -0.65};
        
        // Free boundary parameters
        config.lfreeb = false;
        config.mgrid_file = "NONE";
        config.lforbal = false;
        
        // Axis
        config.raxis_c = {6.0};
        config.zaxis_s = {0.0};
        
        // Boundary coefficients for circular tokamak
        config.rbc.resize(8, 0.0);
        config.zbs.resize(8, 0.0);
        config.rbc[0] = 6.0;  // m=0, n=0: R_major
        config.rbc[1] = 2.0;  // m=1, n=0: R_minor
        config.zbs[1] = 2.0;  // m=1, n=0: Z_minor
        
        return config;
    }

    void RunDebugComparison(const VmecINDATA& config, 
                           const std::string& test_name,
                           const std::string& debug_output_file) {
        std::cout << "\n=== Debug Comparison: " << test_name << " ===\n";
        
        // Create debug output file with timestamp
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        
        std::ostringstream filename;
        filename << "/home/ert/code/vmecpp/debug_output_" 
                 << test_name << "_" 
                 << std::put_time(std::localtime(&time_t), "%Y%m%d_%H%M%S")
                 << ".log";
                 
        std::ofstream debug_file(filename.str());
        debug_file << "VMEC++ Debug Output Comparison\n";
        debug_file << "Test: " << test_name << "\n";
        debug_file << "Timestamp: " << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S") << "\n";
        debug_file << "Configuration: Circular Tokamak (LASYM=" << (config.lasym ? "T" : "F") << ")\n";
        debug_file << "MPOL=" << config.mpol << ", NTOR=" << config.ntor << ", NFP=" << config.nfp << "\n";
        debug_file << "NS_ARRAY: ";
        for (int ns : config.ns_array) debug_file << ns << " ";
        debug_file << "\nFTOL_ARRAY: ";
        for (double ftol : config.ftol_array) debug_file << std::scientific << ftol << " ";
        debug_file << "\nNITER_ARRAY: ";
        for (int niter : config.niter_array) debug_file << niter << " ";
        debug_file << "\n\n";
        
        debug_file << "=== DETAILED ITERATION LOG ===\n";
        debug_file.flush();
        
        try {
            Vmec vmec(config);
            
            debug_file << "VMEC++ initialization successful\n";
            debug_file << "Starting equilibrium solve...\n";
            debug_file.flush();
            
            auto result = vmec.run();
            
            if (result.ok()) {
                debug_file << "\n=== CONVERGENCE SUCCESSFUL ===\n";
                debug_file << "Final result: Converged successfully\n";
                std::cout << "✅ CONVERGED - Debug output saved to: " << filename.str() << "\n";
            } else {
                debug_file << "\n=== CONVERGENCE FAILED ===\n";
                debug_file << "Final result: " << result.status() << "\n";
                std::cout << "❌ FAILED - Debug output saved to: " << filename.str() << "\n";
            }
            
        } catch (const std::exception& e) {
            debug_file << "\n=== EXCEPTION OCCURRED ===\n";
            debug_file << "Exception: " << e.what() << "\n";
            std::cout << "❌ EXCEPTION: " << e.what() << " - Debug output saved to: " << filename.str() << "\n";
        }
        
        debug_file.close();
        
        // Generate comparison instructions
        std::cout << "\nTo compare with Educational VMEC:\n";
        std::cout << "1. Run Educational VMEC with identical input\n";
        std::cout << "2. Compare iteration-by-iteration values\n";
        std::cout << "3. Identify first divergence point\n";
        std::cout << "Debug file: " << filename.str() << "\n\n";
    }

    VmecINDATA base_config_;
};

TEST_F(DebugOutputComparisonTest, StandardToleranceDebug) {
    auto config = base_config_;
    config.ns_array = {17};
    config.ftol_array = {1e-20};
    config.niter_array = {100};  // Shorter run for detailed analysis
    
    RunDebugComparison(config, "standard_tolerance", "standard_debug.log");
}

TEST_F(DebugOutputComparisonTest, TightToleranceDebug) {
    auto config = base_config_;
    config.ns_array = {17};
    config.ftol_array = {1e-30};
    config.niter_array = {100};  // Shorter run to capture failure point
    
    RunDebugComparison(config, "tight_tolerance", "tight_debug.log");
}

TEST_F(DebugOutputComparisonTest, MultiStepDebug) {
    auto config = base_config_;
    config.ns_array = {10, 17};
    config.ftol_array = {1e-20, 1e-20};
    config.niter_array = {50, 50};  // Shorter for each step
    
    RunDebugComparison(config, "multi_step", "multi_step_debug.log");
}

TEST_F(DebugOutputComparisonTest, BenchmarkReplicationDebug) {
    // Replicate exact benchmark conditions that fail
    auto config = base_config_;
    config.ns_array = {10, 17};
    config.ftol_array = {1e-30, 1e-20};
    config.niter_array = {500, 1000};
    
    RunDebugComparison(config, "benchmark_replication", "benchmark_debug.log");
}

TEST_F(DebugOutputComparisonTest, AsymmetricDebug) {
    // Test asymmetric case for comparison
    auto config = base_config_;
    config.lasym = true;
    config.ns_array = {17};
    config.ftol_array = {1e-20};
    config.niter_array = {100};
    
    RunDebugComparison(config, "asymmetric_test", "asymmetric_debug.log");
}

// Helper test to generate Educational VMEC compatible input files
TEST_F(DebugOutputComparisonTest, GenerateEducationalVmecInput) {
    std::cout << "\n=== Generating Educational VMEC Compatible Input ===\n";
    
    auto config = base_config_;
    config.ns_array = {17};
    config.ftol_array = {1e-20};
    config.niter_array = {100};
    
    std::string input_file = "/home/ert/code/vmecpp/input_educational_vmec_comparison.txt";
    std::ofstream input(input_file);
    
    input << "&INDATA\n";
    input << "  MGRID_FILE = 'NONE'\n";
    input << "  LOPTIM = F\n";
    input << "  DELT = " << config.delt << "\n";
    input << "  TCON0 = " << config.tcon0 << "\n";
    input << "  NFP = " << config.nfp << "\n";
    input << "  MPOL = " << config.mpol << "\n";
    input << "  NTOR = " << config.ntor << "\n";
    input << "  NITER = " << config.niter_array[0] << "\n";
    input << "  NS_ARRAY = " << config.ns_array[0] << "\n";
    input << "  FTOL_ARRAY = " << std::scientific << config.ftol_array[0] << "\n";
    input << "  NSTEP = " << config.nstep << "\n";
    input << "  NVACSKIP = " << config.nvacskip << "\n";
    input << "  GAMMA = " << config.gamma << "\n";
    input << "  PHIEDGE = " << config.phiedge << "\n";
    input << "  SPRES_PED = " << config.spres_ped << "\n";
    input << "  NCURR = " << config.ncurr << "\n";
    input << "  AM = " << config.am[0] << "\n";
    input << "  AI = " << config.ai[0] << " " << config.ai[1] << "\n";
    input << "  RAXIS_CC = " << config.raxis_c[0] << "\n";
    input << "  ZAXIS_CS = " << config.zaxis_s[0] << "\n";
    input << "  RBC(0,0) = " << config.rbc[0] << "\n";
    input << "  RBC(1,0) = " << config.rbc[1] << "\n";
    input << "  ZBS(1,0) = " << config.zbs[1] << "\n";
    input << "/\n";
    
    input.close();
    
    std::cout << "Educational VMEC input file generated: " << input_file << "\n";
    std::cout << "Run: /home/ert/code/educational_VMEC/build/bin/xvmec " << input_file << "\n";
    std::cout << "Compare output with VMEC++ debug logs\n\n";
}

} // namespace vmecpp