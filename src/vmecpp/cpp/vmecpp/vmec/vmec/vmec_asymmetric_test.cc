// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT
#include "vmecpp/vmec/vmec/vmec.h"

#include <string>

#include "absl/log/check.h"
#include "gtest/gtest.h"
#include "util/file_io/file_io.h"
#include "vmecpp/common/vmec_indata/vmec_indata.h"
#include "vmecpp/vmec/output_quantities/output_quantities.h"

using file_io::ReadFile;
using vmecpp::VmecINDATA;
using vmecpp::WOutFileContents;

namespace {

TEST(TestVmecAsymmetric, SymmetricCaseWithLasymTrue) {
  // Test that a symmetric equilibrium can be run with lasym=true
  // This validates the basic asymmetric infrastructure
  const std::string filename = "vmecpp/test_data/solovev.json";
  absl::StatusOr<std::string> indata_json = ReadFile(filename);
  ASSERT_TRUE(indata_json.ok());

  absl::StatusOr<VmecINDATA> indata = VmecINDATA::FromJson(*indata_json);
  ASSERT_TRUE(indata.ok());

  // Enable asymmetric mode on symmetric case
  indata->lasym = true;
  
  // Add required asymmetric axis arrays (zeros for symmetric case)
  if (indata->raxis_s.empty()) {
    indata->raxis_s.resize(indata->ntor + 1, 0.0);
  }
  if (indata->zaxis_c.empty()) {
    indata->zaxis_c.resize(indata->ntor + 1, 0.0);
  }

  // Run should succeed
  const auto output = vmecpp::run(*indata);
  ASSERT_TRUE(output.ok()) << "Failed: " << output.status();
  
  // Should converge
  EXPECT_LT(output->wout.fsqr, 1e-6);
}

TEST(TestVmecAsymmetric, CircularTokamakAsymmetric) {
  // Test circular tokamak with asymmetric mode enabled
  const std::string filename = "vmecpp/test_data/circular_tokamak.json";
  
  absl::StatusOr<std::string> indata_json = ReadFile(filename);
  ASSERT_TRUE(indata_json.ok()) << "Failed to read " << filename;

  absl::StatusOr<VmecINDATA> indata = VmecINDATA::FromJson(*indata_json);
  ASSERT_TRUE(indata.ok());
  
  // Enable asymmetric mode
  indata->lasym = true;
  
  // Add required asymmetric axis arrays (zeros for symmetric case)
  if (indata->raxis_s.empty()) {
    indata->raxis_s.resize(indata->ntor + 1, 0.0);
  }
  if (indata->zaxis_c.empty()) {
    indata->zaxis_c.resize(indata->ntor + 1, 0.0);
  }
  
  // Use reduced resolution for faster testing
  indata->ns_array = {5};
  indata->ftol_array = {1e-4};
  indata->niter_array = {50};
  
  // Run VMEC++
  const auto output = vmecpp::run(*indata);
  
  // Should succeed with asymmetric infrastructure
  ASSERT_TRUE(output.ok()) << "Failed: " << output.status();
  
  // Should converge
  EXPECT_LT(output->wout.fsqr, 1e-3);
  
  // Verify asymmetric mode was enabled
  EXPECT_TRUE(output->wout.lasym);
}

TEST(TestVmecAsymmetric, StellaratorAsymmetricInfrastructure) {
  // Test stellarator with asymmetric mode enabled
  // This validates the core asymmetric physics implementation
  const std::string filename = "vmecpp/test_data/cma.json";
  
  absl::StatusOr<std::string> indata_json = ReadFile(filename);
  ASSERT_TRUE(indata_json.ok());

  absl::StatusOr<VmecINDATA> indata = VmecINDATA::FromJson(*indata_json);
  ASSERT_TRUE(indata.ok());
  
  // Enable asymmetric mode
  indata->lasym = true;
  
  // Add required asymmetric axis arrays (zeros for symmetric case)
  if (indata->raxis_s.empty()) {
    indata->raxis_s.resize(indata->ntor + 1, 0.0);
  }
  if (indata->zaxis_c.empty()) {
    indata->zaxis_c.resize(indata->ntor + 1, 0.0);
  }
  
  // Use reduced resolution for faster testing
  indata->ns_array = {5};
  indata->ftol_array = {1e-4};
  indata->niter_array = {50};
  
  // Should run without Initial Jacobian errors
  const auto output = vmecpp::run(*indata);
  
  // Test should succeed with asymmetric infrastructure
  ASSERT_TRUE(output.ok()) << "Failed: " << output.status();
  
  // Should converge
  EXPECT_LT(output->wout.fsqr, 1e-3);
  
  // Verify asymmetric mode was enabled
  EXPECT_TRUE(output->wout.lasym);
}

}  // namespace