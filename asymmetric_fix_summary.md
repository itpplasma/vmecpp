# Asymmetric Mode Fix Summary

## Problem Solved
VMEC++ was stuck in an infinite BAD_JACOBIAN loop when running in asymmetric mode (lasym=true), making it impossible to compute non-stellarator-symmetric equilibria.

## Root Cause
Incorrect zeta reflection logic in `SymmetrizeRealSpaceGeometry` function:
- VMEC++ was applying zeta reflection for ALL cases (including axisymmetric)
- Educational_VMEC only applies zeta reflection for non-axisymmetric cases
- For axisymmetric cases (nZeta=1), no zeta reflection should occur

## The Fix
In `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.cc`, lines 306-313:

```cpp
// Fix: Match educational_VMEC's ireflect behavior
// For axisymmetric (nZeta=1): no zeta reflection
// For non-axisymmetric: apply zeta reflection
int k_mirror = k;  // Default: no zeta reflection
if (s.nZeta > 1) {
  k_mirror = s.nZeta - k;
  if (k == 0) k_mirror = 0;  // k=0 maps to itself
}
```

## Impact
- Asymmetric mode no longer gets stuck in infinite loop
- Solver can now iterate and make progress
- Opens the door for non-stellarator-symmetric equilibrium calculations

## Verification
- Tested with minimal asymmetric tokamak configuration
- Confirmed solver progresses through iterations
- No more "INITIAL JACOBIAN CHANGED SIGN!" infinite loop

## Minimal Changeset
From hundreds of debug changes, we've identified the essential fix:
- **1 file changed**: `fourier_asymmetric.cc`
- **7 lines modified**: The zeta reflection logic
- **All debug code removed**: Clean implementation ready for upstream

## Next Steps
1. Create clean PR for upstream with just the critical fix
2. Add minimal test case demonstrating the problem and solution
3. Continue investigating remaining convergence issues (negative Jacobians)
4. Implement missing asymmetric features (inv-DFT, full symrzl)
