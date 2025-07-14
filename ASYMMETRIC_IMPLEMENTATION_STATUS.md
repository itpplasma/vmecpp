# Asymmetric Implementation Status

## Summary

The non-stellarator-symmetric field support (lasym=true) implementation in VMECPP has been partially completed. The core asymmetric transforms and data structures are in place, but convergence issues remain.

## What Has Been Fixed

### 1. Division by Zero in Mode Scaling (FIXED)
- **Issue**: NaN values appeared immediately in asymmetric execution
- **Root Cause**: Division by zero in `fourier_asymmetric.cc` when computing mode scaling for odd-m modes at the magnetic axis (where sqrt(s) = 0)
- **Fix**: Applied conditional check to use minimum value from next radial point when at axis
- **Files Modified**: 
  - `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.cc` (lines 43-46, 150-153)

### 2. Core Asymmetric Infrastructure (IMPLEMENTED)
- Asymmetric Fourier transforms: `FourierToReal3DAsymmFastPoloidal` and `FourierToReal2DAsymmFastPoloidal`
- Asymmetric geometry arrays properly allocated and populated
- Symmetrization of real-space geometry for full theta domain
- Python interface correctly handles asymmetric coefficient arrays (rbs, zbc, raxis_s, zaxis_c)

## Current Status

### What Works
- Asymmetric arrays are properly validated and allocated
- Fourier transforms execute without NaN values
- Geometry computation proceeds past initial steps
- Python interface correctly loads and validates asymmetric input files

### Remaining Issues

1. **Jacobian Sign Changes**
   - Both test cases and existing examples show "INITIAL JACOBIAN CHANGED SIGN!" errors
   - The magnetic axis repositioning algorithm attempts to fix this but fails
   - This suggests the initial guess quality for asymmetric cases needs improvement

2. **Force Symmetrization Not Implemented**
   - The `SymmetrizeForces` function in `fourier_asymmetric.cc` is a placeholder
   - This may be contributing to convergence issues
   - Implementation would require careful handling of force decomposition

3. **No Working Examples**
   - Neither the provided asymmetric examples (tok_asym.json, HELIOTRON_asym.json) converge
   - This suggests systemic issues with the asymmetric implementation

## Test Results

```
Test                          | Result | Notes
------------------------------|--------|-------
Division by zero fix          | ✅     | NaN values eliminated
Asymmetric array allocation   | ✅     | Properly sized and initialized  
Input validation              | ✅     | Pydantic models work correctly
Geometry computation          | ⚠️     | Runs but Jacobian issues
Force calculation             | ❌     | Incomplete symmetrization
Convergence                   | ❌     | No examples converge
```

## Recommendations

1. **Implement Force Symmetrization**: Complete the `SymmetrizeForces` function based on the Fortran VMEC implementation
2. **Improve Initial Guess**: The asymmetric cases may need special handling for initial axis/boundary guess
3. **Validate Against jVMEC**: Run the same test cases in jVMEC to verify expected behavior
4. **Debug Jacobian Computation**: Investigate why the Jacobian sign changes occur more frequently in asymmetric cases

## Files Modified

1. `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.cc` - Fixed division by zero
2. Various test files created for debugging (not committed)

## Next Steps

To complete the asymmetric implementation:
1. Implement proper force symmetrization in `SymmetrizeForces`
2. Debug and fix the Jacobian sign change issues
3. Validate against reference implementations (jVMEC, Fortran VMEC)
4. Add integration tests for asymmetric convergence