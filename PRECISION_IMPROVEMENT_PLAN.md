# VMEC++ Numerical Precision Improvement Plan

## Problem Identified
VMEC++ cannot achieve 1e-30 convergence tolerance due to numerical precision limitations in MHD force calculations. Forces oscillate around ~1e-4 and cannot decrease to 1e-30.

## Root Cause Analysis
1. **Force calculation precision**: MHD force computations involve many floating-point operations that accumulate numerical error
2. **Finite difference discretization**: Spatial derivatives introduce truncation errors  
3. **Round-off error accumulation**: Matrix-vector operations compound precision loss
4. **Not an algorithmic issue**: VMEC++ has all the sophisticated algorithms that jVMEC has

## Evidence from Debug Output
- Forces start at ~4.68e-02, 2.12e-04, 2.53e-02
- Forces should converge to 1e-30 but oscillate around 1e-4 level
- Standard 1e-20 tolerance works perfectly
- Multi-step resolution exacerbates the issue (more operations)

## Implementation Strategy

### Phase 1: Higher Precision Arithmetic (Critical)
1. **Identify precision bottlenecks in force calculations**
   - Analyze `ideal_mhd_model.cc` force computation loops
   - Focus on MHD quantity calculations (totalPressure, gbvbv, etc.)
   - Look for precision loss in derivatives and matrix operations

2. **Implement selective higher precision**
   - Use `long double` for critical force calculations
   - Keep `double` for non-critical operations for performance
   - Focus on `armn_e`, `azmn_e`, `almn_e` force array calculations

### Phase 2: Improved Numerical Algorithms (Medium Priority)
1. **Better finite difference schemes**
   - Replace first-order differences with higher-order schemes where possible
   - Implement adaptive step size for critical derivatives
   
2. **Compensated summation techniques**
   - Use Kahan summation for force accumulations
   - Implement higher-precision dot products for critical operations

### Phase 3: Convergence Algorithm Tuning (Low Priority)
1. **Adaptive tolerance stepping**
   - Start with loose tolerance, gradually tighten
   - Monitor numerical precision availability
   
2. **Residual conditioning**
   - Scale residuals to maintain numerical precision
   - Use relative tolerances where appropriate

## Files to Modify

### Critical Files:
1. `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/ideal_mhd_model.cc`
   - Lines ~2570-2735: MHD force calculations
   - Focus on `armn_e`, `azmn_e`, `almn_e` computations
   
2. `src/vmecpp/cpp/vmecpp/vmec/vmec/vmec.cc`
   - Lines ~1127-1142: Force residual calculations in `Evolve()`
   - Precision in `fsq1` and convergence checking

### Test Files:
1. Create precision-specific tests to validate improvements
2. Add benchmark comparison with Educational VMEC at 1e-30 tolerance

## Success Criteria
1. **Primary**: VMEC++ achieves 1e-30 convergence on standard circular tokamak
2. **Secondary**: Multi-step resolution with tight tolerances works reliably  
3. **Validation**: Match Educational VMEC convergence behavior exactly

## Implementation Timeline
- **Immediate**: Identify specific precision bottlenecks in force calculations
- **Short-term**: Implement selective higher precision for critical operations
- **Medium-term**: Validate against Educational VMEC with identical test cases
- **Long-term**: Performance optimization of higher-precision calculations

## Note
This is NOT about missing algorithms - VMEC++ has all the sophisticated numerical methods that jVMEC has. This is purely about numerical precision in floating-point calculations reaching the limits of double precision arithmetic.