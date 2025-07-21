// SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
// <info@proximafusion.com>
//
// SPDX-License-Identifier: MIT

#ifndef VMECPP_VMEC_HIGH_PRECISION_FORCES_H_
#define VMECPP_VMEC_HIGH_PRECISION_FORCES_H_

#include <cmath>
#include <vector>

namespace vmecpp {

/**
 * High-precision force calculations for tight convergence tolerances.
 * 
 * This module provides higher-precision implementations of critical MHD force
 * calculations to enable convergence to tolerances like 1e-30. The standard
 * double-precision calculations accumulate round-off errors that prevent
 * convergence below ~1e-15 to 1e-20.
 * 
 * Strategy:
 * - Use long double (typically 80-bit) for critical operations
 * - Implement compensated arithmetic where beneficial  
 * - Focus on finite difference calculations that amplify errors
 * - Maintain double precision interface for performance
 */

/**
 * High-precision calculation of radial force component (A_R).
 * 
 * Standard calculation:
 * armn_e = (zup_o - zup_i) / deltaS + 0.5*(taup_o + taup_i) 
 *          - 0.5*(gbvbv_o + gbvbv_i)*r1_e - 0.5*(gbvbv_o*sqrtSHo + gbvbv_i*sqrtSHi)*r1_o
 * 
 * @param zup_o Outer Z-derivative  
 * @param zup_i Inner Z-derivative
 * @param taup_o Outer pressure*tau
 * @param taup_i Inner pressure*tau
 * @param gbvbv_o Outer magnetic pressure term
 * @param gbvbv_i Inner magnetic pressure term
 * @param r1_e Edge radial coordinate
 * @param r1_o Outer radial coordinate  
 * @param deltaS Radial step size
 * @param sqrtSHo Outer sqrt(s) factor
 * @param sqrtSHi Inner sqrt(s) factor
 * @return High-precision A_R force component
 */
double CalculateHighPrecisionRadialForce(
    double zup_o, double zup_i,
    double taup_o, double taup_i,
    double gbvbv_o, double gbvbv_i,
    double r1_e, double r1_o,
    double deltaS,
    double sqrtSHo, double sqrtSHi);

/**
 * High-precision calculation of vertical force component (A_Z).
 * 
 * Standard calculation:
 * azmn_e = -(rup_o - rup_i) / deltaS
 * 
 * @param rup_o Outer R-derivative
 * @param rup_i Inner R-derivative  
 * @param deltaS Radial step size
 * @return High-precision A_Z force component
 */
double CalculateHighPrecisionVerticalForce(
    double rup_o, double rup_i, double deltaS);

/**
 * High-precision calculation of lambda force component (A_L).
 * 
 * Standard calculation:
 * almn_e = complex expression involving multiple derivatives and geometric factors
 * 
 * @param various MHD quantities (to be expanded based on actual lambda force calculation)
 * @return High-precision A_L force component
 */
double CalculateHighPrecisionLambdaForce(
    // Parameters to be added based on actual lambda force implementation
    );

/**
 * Compensated summation using Kahan algorithm for high-precision accumulation.
 * 
 * Used for summing force contributions where many small terms must be accumulated
 * without losing precision.
 * 
 * @param values Vector of values to sum
 * @return High-precision sum with reduced round-off error
 */
double CompensatedSum(const std::vector<double>& values);

/**
 * High-precision dot product with compensated arithmetic.
 * 
 * @param a First vector
 * @param b Second vector  
 * @return High-precision dot product
 */
double HighPrecisionDotProduct(const std::vector<double>& a, 
                              const std::vector<double>& b);

} // namespace vmecpp

#endif // VMECPP_VMEC_HIGH_PRECISION_FORCES_H_