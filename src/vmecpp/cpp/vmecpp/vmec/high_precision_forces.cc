// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#include "vmecpp/vmec/high_precision_forces.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace vmecpp {

double CalculateHighPrecisionRadialForce(
    double zup_o, double zup_i,
    double taup_o, double taup_i,
    double gbvbv_o, double gbvbv_i,
    double r1_e, double r1_o,
    double deltaS,
    double sqrtSHo, double sqrtSHi) {
  
  // Use long double for intermediate calculations to reduce round-off error
  const long double zup_o_ld = static_cast<long double>(zup_o);
  const long double zup_i_ld = static_cast<long double>(zup_i);
  const long double taup_o_ld = static_cast<long double>(taup_o);
  const long double taup_i_ld = static_cast<long double>(taup_i);
  const long double gbvbv_o_ld = static_cast<long double>(gbvbv_o);
  const long double gbvbv_i_ld = static_cast<long double>(gbvbv_i);
  const long double r1_e_ld = static_cast<long double>(r1_e);
  const long double r1_o_ld = static_cast<long double>(r1_o);
  const long double deltaS_ld = static_cast<long double>(deltaS);
  const long double sqrtSHo_ld = static_cast<long double>(sqrtSHo);
  const long double sqrtSHi_ld = static_cast<long double>(sqrtSHi);
  
  // Compute finite difference term with higher precision
  const long double finite_diff_term = (zup_o_ld - zup_i_ld) / deltaS_ld;
  
  // Compute pressure term with higher precision
  const long double pressure_term = 0.5L * (taup_o_ld + taup_i_ld);
  
  // Compute magnetic pressure terms with higher precision
  const long double mag_pressure_term1 = 0.5L * (gbvbv_o_ld + gbvbv_i_ld) * r1_e_ld;
  const long double mag_pressure_term2 = 0.5L * (gbvbv_o_ld * sqrtSHo_ld + gbvbv_i_ld * sqrtSHi_ld) * r1_o_ld;
  
  // Combine terms with higher precision
  const long double result_ld = finite_diff_term + pressure_term - mag_pressure_term1 - mag_pressure_term2;
  
  // Convert back to double for interface compatibility
  return static_cast<double>(result_ld);
}

double CalculateHighPrecisionVerticalForce(
    double rup_o, double rup_i, double deltaS) {
  
  // Use long double for the critical finite difference calculation
  const long double rup_o_ld = static_cast<long double>(rup_o);
  const long double rup_i_ld = static_cast<long double>(rup_i);
  const long double deltaS_ld = static_cast<long double>(deltaS);
  
  // High-precision finite difference
  const long double result_ld = -(rup_o_ld - rup_i_ld) / deltaS_ld;
  
  return static_cast<double>(result_ld);
}

double CalculateHighPrecisionLambdaForce() {
  // TODO: Implement based on actual lambda force calculation in ideal_mhd_model.cc
  // This is a placeholder for the lambda force computation
  return 0.0;
}

double CompensatedSum(const std::vector<double>& values) {
  if (values.empty()) return 0.0;
  
  // Kahan summation algorithm for reduced round-off error
  long double sum = 0.0L;
  long double c = 0.0L;  // Compensation for lost low-order bits
  
  for (double value : values) {
    const long double value_ld = static_cast<long double>(value);
    const long double y = value_ld - c;          // Subtract previous error
    const long double t = sum + y;               // Add with current sum
    c = (t - sum) - y;                          // Compute new error
    sum = t;                                    // Update sum
  }
  
  return static_cast<double>(sum);
}

double HighPrecisionDotProduct(const std::vector<double>& a, 
                              const std::vector<double>& b) {
  if (a.size() != b.size()) {
    return 0.0;  // Error case
  }
  
  // Compute dot product with compensated summation
  std::vector<double> products;
  products.reserve(a.size());
  
  for (size_t i = 0; i < a.size(); ++i) {
    // Use long double for multiplication to reduce error
    const long double product_ld = static_cast<long double>(a[i]) * 
                                  static_cast<long double>(b[i]);
    products.push_back(static_cast<double>(product_ld));
  }
  
  return CompensatedSum(products);
}

} // namespace vmecpp