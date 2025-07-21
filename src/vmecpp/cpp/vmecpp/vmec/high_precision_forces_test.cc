// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#include "vmecpp/vmec/high_precision_forces.h"
#include <gtest/gtest.h>
#include <cmath>
#include <limits>
#include <vector>

namespace vmecpp {

class HighPrecisionForcesTest : public ::testing::Test {
protected:
    // Test values that would cause precision issues in standard calculations
    static constexpr double kSmallDeltaS = 1.111111e-01;  // From debug output
    static constexpr double kVerySmallDeltaS = 1e-10;     // Extreme case
    static constexpr double kTinyDifference = 1e-15;      // Near machine epsilon
};

TEST_F(HighPrecisionForcesTest, RadialForceBasicCalculation) {
    // Test with values from actual VMEC++ debug output
    double zup_o = 4.465671e+01;
    double zup_i = 0.0;
    double taup_o = -2.927686e+01;
    double taup_i = 0.0;
    double gbvbv_o = -9.012379e+00;
    double gbvbv_i = 0.0;
    double r1_e = 6.0;
    double r1_o = 2.0;
    double deltaS = kSmallDeltaS;
    double sqrtSHo = 2.357023e-01;
    double sqrtSHi = 1.0;
    
    double result = CalculateHighPrecisionRadialForce(
        zup_o, zup_i, taup_o, taup_i, gbvbv_o, gbvbv_i,
        r1_e, r1_o, deltaS, sqrtSHo, sqrtSHi);
    
    // Should compute finite value (not NaN)
    EXPECT_TRUE(std::isfinite(result));
    
    // Should be different from zero given non-zero inputs
    EXPECT_NE(result, 0.0);
}

TEST_F(HighPrecisionForcesTest, VerticalForceBasicCalculation) {
    // Test with values from debug output
    double rup_o = -1.254442e+01;
    double rup_i = 0.0;
    double deltaS = kSmallDeltaS;
    
    double result = CalculateHighPrecisionVerticalForce(rup_o, rup_i, deltaS);
    
    EXPECT_TRUE(std::isfinite(result));
    EXPECT_NE(result, 0.0);
    
    // Should match expected calculation: -(rup_o - rup_i) / deltaS
    double expected = -(rup_o - rup_i) / deltaS;
    EXPECT_NEAR(result, expected, 1e-12);  // Should be very close
}

TEST_F(HighPrecisionForcesTest, PrecisionComparisonWithRealisticValues) {
    // Test with realistic VMEC values that show precision improvement
    double rup_o = 1.254442e+01;  // From actual debug output
    double rup_i = 1.254441e+01;  // Very close value (precision challenge)
    double deltaS = kSmallDeltaS;  // 1.111111e-01
    
    // High-precision calculation
    double hp_result = CalculateHighPrecisionVerticalForce(rup_o, rup_i, deltaS);
    
    // Should be finite and reasonable
    EXPECT_TRUE(std::isfinite(hp_result));
    
    // The tiny difference should be preserved and amplified by division
    double expected_magnitude = 1e-5 / deltaS;  // ~1e-4
    EXPECT_GT(std::abs(hp_result), expected_magnitude * 0.1);  // At least 10% of expected
    
    std::cout << "High-precision result for small difference: " << hp_result << std::endl;
}

TEST_F(HighPrecisionForcesTest, CompensatedSumAccuracy) {
    // Test compensated summation with many small values
    std::vector<double> small_values;
    int num_values = 1000000;
    double small_val = 1e-10;
    
    for (int i = 0; i < num_values; ++i) {
        small_values.push_back(small_val);
    }
    
    // Standard summation
    double standard_sum = 0.0;
    for (double val : small_values) {
        standard_sum += val;
    }
    
    // Compensated summation
    double compensated_sum = CompensatedSum(small_values);
    
    // Expected result
    double expected = num_values * small_val;
    
    std::cout << "Standard sum: " << standard_sum << std::endl;
    std::cout << "Compensated sum: " << compensated_sum << std::endl;
    std::cout << "Expected: " << expected << std::endl;
    
    // Compensated sum should be more accurate
    EXPECT_NEAR(compensated_sum, expected, 1e-12);
}

TEST_F(HighPrecisionForcesTest, HighPrecisionDotProductAccuracy) {
    // Test high-precision dot product
    std::vector<double> a = {1e10, 1e-10, 1e5};
    std::vector<double> b = {1e-10, 1e10, 1e-5};
    
    double result = HighPrecisionDotProduct(a, b);
    
    // Expected: (1e10 * 1e-10) + (1e-10 * 1e10) + (1e5 * 1e-5) = 1 + 1 + 1 = 3
    EXPECT_NEAR(result, 3.0, 1e-12);
    
    EXPECT_TRUE(std::isfinite(result));
}

TEST_F(HighPrecisionForcesTest, EdgeCasesHandling) {
    // Test with zero values
    double zero_result = CalculateHighPrecisionVerticalForce(0.0, 0.0, 1.0);
    EXPECT_EQ(zero_result, 0.0);
    
    // Test with very small deltaS
    double small_delta_result = CalculateHighPrecisionVerticalForce(1e-15, 0.0, kVerySmallDeltaS);
    EXPECT_TRUE(std::isfinite(small_delta_result));
    
    // Test empty vector for compensated sum
    std::vector<double> empty_vec;
    double empty_sum = CompensatedSum(empty_vec);
    EXPECT_EQ(empty_sum, 0.0);
}

} // namespace vmecpp