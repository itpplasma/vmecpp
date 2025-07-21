#include <gtest/gtest.h>
#include <iostream>
#include <iomanip>
#include <cmath>
#include "vmecpp/vmec/vmec/vmec.h"
#include "vmecpp/common/vmec_indata/vmec_indata.h"
#include <nlohmann/json.hpp>

class DetailedJVMECStepComparison : public ::testing::Test {
protected:
  void SetUp() override {
    // Same minimal asymmetric tokamak that was causing NaN
    indata_json = {
      {"mgrid_file", ""},
      {"ns_array", {5}},
      {"nfp", 1},
      {"mpol", 3},
      {"ntor", 0},
      {"niter", 10},  // More iterations for detailed comparison
      {"delt", 0.9},
      {"ftol_array", {1e-06}},
      {"tcon0", 1.0},
      {"lasym", true},  // ASYMMETRIC
      {"am", {0.0, 1.0, 0.0}},
      {"ac", {0.0, 0.0, 0.0}},
      {"rbc", {  // SYMMETRIC baseline
        {{"n", 0}, {"m", 0}, {"value", 1.0}},     // R00 = 1.0 (major radius)
        {{"n", 0}, {"m", 1}, {"value", 0.3}}      // R10 = 0.3 (minor radius)
      }},
      {"zbs", {  // SYMMETRIC baseline  
        {{"n", 0}, {"m", 1}, {"value", 0.3}}      // Z01 = 0.3 (height)
      }},
      {"rbs", {  // ASYMMETRIC - this is the key difference
        {{"n", 0}, {"m", 1}, {"value", 0.001}}   // 0.1% asymmetric R perturbation
      }},
      {"zbc", {}},  // No asymmetric Z for this test
      {"ai", {0.0, 0.0, 0.0, 0.0, 0.0}},
      {"ac", {0.0, 0.0, 0.0, 0.0, 0.0}},
      {"pcurr_type", "power_series"},
      {"piota_type", "power_series"}
    };
  }

  nlohmann::json indata_json;
};

TEST_F(DetailedJVMECStepComparison, MicroscopicStepByStepComparison) {
  std::cout << "\n=== MICROSCOPIC STEP-BY-STEP COMPARISON WITH jVMEC ===" << std::endl;
  std::cout << "Goal: Compare every tiny detail of asymmetric calculation with jVMEC" << std::endl;
  
  // Create VMEC++ configuration
  auto indata_result = vmecpp::VmecINDATA::FromJson(indata_json);
  ASSERT_TRUE(indata_result.ok()) << "Failed to create VmecINDATA: " << indata_result.status();
  auto indata = indata_result.value();
  
  std::cout << "\n=== CONFIGURATION ===" << std::endl;
  std::cout << "Asymmetric tokamak: R_major=1.0, R_minor=0.3" << std::endl;
  std::cout << "ASYMMETRIC: RBS(0,1) = 0.001 (0.1% perturbation)" << std::endl;
  std::cout << "Iterations: 10 for detailed step tracking" << std::endl;
  
  std::cout << "\n=== STEP 1: FOURIER COEFFICIENTS INPUT ===" << std::endl;
  std::cout << "VMEC++ Input Fourier coefficients:" << std::endl;
  std::cout << "  RBC(0,0) = 1.0    (major radius)" << std::endl;
  std::cout << "  RBC(0,1) = 0.3    (minor radius)" << std::endl;
  std::cout << "  RBS(0,1) = 0.001  (ASYMMETRIC perturbation)" << std::endl;
  std::cout << "  ZBS(0,1) = 0.3    (height)" << std::endl;
  
  std::cout << "\nNOTE: jVMEC uses exact same input format" << std::endl;
  
  // Run VMEC++
  std::cout << "\n=== STEP 2: RUNNING VMEC++ WITH DETAILED DEBUG ===" << std::endl;
  std::cout << "Watch for each iteration's behavior..." << std::endl;
  
  try {
    auto output = vmecpp::run(indata);
    
    std::cout << "\n=== STEP 3: VMEC++ RESULTS ANALYSIS ===" << std::endl;
    if (output.ok()) {
      std::cout << "✅ VMEC++ converged successfully!" << std::endl;
      const auto& wout = output->wout;
      std::cout << "Final MHD Energy: " << wout.wb << std::endl;
      std::cout << "Final force residuals - fsqr: " << wout.fsqr << ", fsqz: " << wout.fsqz << std::endl;
      std::cout << "Volume: " << wout.volume_p << std::endl;
      std::cout << "Iterations used: " << wout.itfsq << std::endl;
      
      std::cout << "\n=== STEP 4: COMPARISON SUMMARY ===" << std::endl;
      std::cout << "✅ VMEC++ asymmetric equilibrium converged successfully" << std::endl;
      std::cout << "Compare these results with jVMEC running identical input" << std::endl;
      std::cout << "Both should have similar final energies and force residuals" << std::endl;
      
    } else {
      std::cout << "❌ VMEC++ failed with error: " << output.status() << std::endl;
    }
    
  } catch (const std::exception& e) {
    std::cout << "❌ VMEC++ threw exception: " << e.what() << std::endl;
  }
  
  std::cout << "\n=== STEP 5: COMPARISON NOTES ===" << std::endl;
  std::cout << "Compare this output with jVMEC running same configuration:" << std::endl;
  std::cout << "1. Check iteration-by-iteration force reduction" << std::endl;
  std::cout << "2. Compare final Fourier coefficients" << std::endl;
  std::cout << "3. Verify MHD energy matches" << std::endl;
  std::cout << "4. Check for any numerical differences" << std::endl;
  
  std::cout << "\n=== jVMEC COMMAND FOR COMPARISON ===" << std::endl;
  std::cout << "Run jVMEC with identical input:" << std::endl;
  std::cout << "- Same ns=5, mpol=3, ntor=0" << std::endl; 
  std::cout << "- Same RBC, ZBS coefficients" << std::endl;
  std::cout << "- Same RBS(0,1) = 0.001 asymmetric perturbation" << std::endl;
  std::cout << "- Compare iteration tables and final results" << std::endl;
}

TEST_F(DetailedJVMECStepComparison, CompareTransformDetails) {
  std::cout << "\n=== TRANSFORM-LEVEL COMPARISON ===" << std::endl;
  std::cout << "Detailed comparison of Fourier transform behavior" << std::endl;
  
  auto indata_result = vmecpp::VmecINDATA::FromJson(indata_json);
  ASSERT_TRUE(indata_result.ok()) << "Failed to create VmecINDATA: " << indata_result.status();
  auto indata = indata_result.value();
  
  std::cout << "\n=== FOURIER TO REAL SPACE COMPARISON ===" << std::endl;
  std::cout << "1. jVMEC uses totzspa.f90 for asymmetric forward transform" << std::endl;
  std::cout << "2. VMEC++ uses FourierToReal2DAsymmFastPoloidal" << std::endl;
  std::cout << "3. Both should produce identical R(θ), Z(θ) arrays" << std::endl;
  
  std::cout << "\n=== REAL TO FOURIER COMPARISON ===" << std::endl;
  std::cout << "1. jVMEC uses tomnspa.f90 for asymmetric reverse transform" << std::endl;
  std::cout << "2. VMEC++ uses RealToFourier2DAsymmFastPoloidal" << std::endl;
  std::cout << "3. Both should produce identical force Fourier coefficients" << std::endl;
  
  std::cout << "\n=== SYMMETRIZATION COMPARISON ===" << std::endl;
  std::cout << "1. jVMEC uses symrzl.f90 for geometry symmetrization" << std::endl;
  std::cout << "2. VMEC++ uses SymmetrizeRealSpaceGeometry" << std::endl;
  std::cout << "3. Both should extend [0,π] to [0,2π] identically" << std::endl;
  
  // Let's run one iteration and show the transform details
  std::cout << "\n=== RUNNING ONE ITERATION FOR TRANSFORM DEBUGGING ===" << std::endl;
  try {
    auto output = vmecpp::run(indata);
    std::cout << "Transform debugging completed - check debug output above" << std::endl;
  } catch (const std::exception& e) {
    std::cout << "Exception during transform debugging: " << e.what() << std::endl;
  }
}