#include <iostream>
#include <string>

#include "util/file_io/file_io.h"
#include "vmecpp/common/vmec_indata/vmec_indata.h"
#include "vmecpp/vmec/vmec/vmec.h"

int main() {
  // Test symmetric circular tokamak
  std::string input_file = "vmecpp/test_data/circular_tokamak.json";

  std::cout << "Loading circular tokamak (symmetric) from: " << input_file
            << std::endl;

  // Load input
  auto json_result = file_io::ReadFile(input_file);
  if (!json_result.ok()) {
    std::cout << "Failed to read file: " << json_result.status() << std::endl;
    return 1;
  }

  auto vmec_input = vmecpp::VmecINDATA::FromJson(*json_result);
  if (!vmec_input.ok()) {
    std::cout << "Failed to parse input: " << vmec_input.status() << std::endl;
    return 1;
  }

  std::cout << "LASYM = " << (vmec_input->lasym ? "true" : "false")
            << std::endl;

  // Run VMEC
  try {
    vmecpp::Vmec vmec(*vmec_input);
    auto result = vmec.run();
    if (result.ok()) {
      std::cout << "✅ Converged!" << std::endl;
      return 0;
    } else {
      std::cout << "❌ Failed to converge: " << result.status() << std::endl;
      return 1;
    }
  } catch (const std::exception& e) {
    std::cout << "❌ Exception: " << e.what() << std::endl;
    return 1;
  }
}
