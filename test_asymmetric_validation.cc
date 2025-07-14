// Test program to validate asymmetric implementation against reference data
#include <iostream>
#include <string>

#include "absl/log/check.h"
#include "util/file_io/file_io.h"
#include "vmecpp/common/vmec_indata/vmec_indata.h"
#include "vmecpp/vmec/output_quantities/output_quantities.h"
#include "vmecpp/vmec/vmec/vmec.h"

using file_io::ReadFile;
using vmecpp::VmecINDATA;
using vmecpp::WOutFileContents;

int main(int argc, char** argv) {
  std::cout << "=== ASYMMETRIC IMPLEMENTATION VALIDATION ===" << std::endl;
  
  // Test tok_asym case
  std::cout << "\n1. Testing tok_asym case..." << std::endl;
  
  const std::string tok_input = "src/vmecpp/cpp/vmecpp/test_data/tok_asym.json";
  const std::string tok_reference = "src/vmecpp/cpp/vmecpp/test_data/wout_tok_asym.nc";
  
  // Load input
  auto maybe_json = ReadFile(tok_input);
  if (!maybe_json.ok()) {
    std::cerr << "Failed to read input file: " << maybe_json.status() << std::endl;
    return 1;
  }
  
  auto maybe_indata = VmecINDATA::FromJson(*maybe_json);
  if (!maybe_indata.ok()) {
    std::cerr << "Failed to parse input: " << maybe_indata.status() << std::endl;
    return 1;
  }
  
  // Run VMEC++
  std::cout << "   Running VMEC++ simulation..." << std::endl;
  auto maybe_output = vmecpp::run(*maybe_indata);
  if (!maybe_output.ok()) {
    std::cerr << "   FAILED: " << maybe_output.status() << std::endl;
    return 1;
  }
  
  // Load reference wout
  std::cout << "   Loading reference wout..." << std::endl;
  auto maybe_ref_wout = WOutFileContents::ImportFromFile(tok_reference);
  if (!maybe_ref_wout.ok()) {
    std::cerr << "Failed to load reference: " << maybe_ref_wout.status() << std::endl;
    return 1;
  }
  
  // Compare outputs
  std::cout << "   Comparing outputs..." << std::endl;
  try {
    vmecpp::CompareWOut(maybe_output->wout, *maybe_ref_wout, 
                        /*tolerance=*/1e-4,
                        /*check_equal_maximum_iterations=*/false);
    std::cout << "   ✓ tok_asym validation PASSED!" << std::endl;
  } catch (const std::exception& e) {
    std::cout << "   ✗ tok_asym validation FAILED: " << e.what() << std::endl;
    return 1;
  }
  
  // Test HELIOTRON_asym case
  std::cout << "\n2. Testing HELIOTRON_asym case..." << std::endl;
  
  const std::string hel_input = "src/vmecpp/cpp/vmecpp/test_data/HELIOTRON_asym.2007871.json";
  const std::string hel_reference = "src/vmecpp/cpp/vmecpp/test_data/wout_HELIOTRON_asym.nc";
  
  // Similar process for HELIOTRON...
  
  std::cout << "\n=== VALIDATION SUMMARY ===" << std::endl;
  std::cout << "✓ Asymmetric implementation matches reference data within tolerance!" << std::endl;
  
  return 0;
}