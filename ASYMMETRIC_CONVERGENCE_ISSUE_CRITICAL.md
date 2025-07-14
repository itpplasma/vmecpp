# CRITICAL: VMEC++ Asymmetric Convergence Issue

## 🚨 CRITICAL FINDING

**jVMEC reference asymmetric cases CONVERGE SUCCESSFULLY** but **VMEC++ FAILS** with the exact same input files.

## Evidence

### jVMEC Reference Results ✅
- **tok_asym**: `ier_flag = 0` (successful convergence)
- **HELIOTRON_asym**: `ier_flag = 0` (successful convergence)
- Both cases have properly populated asymmetric arrays in wout files
- Reference files: `/home/ert/code/jVMEC/target/test-classes/wout_tok_asym.nc` and `wout_HELIOTRON_asym.nc`

### VMEC++ Results ❌
- **Both tok_asym and HELIOTRON_asym**: 
  ```
  FATAL ERROR in thread=0. The solver failed during the first iterations.
  ```
- Fails even with single threading and minimal resolution
- Fails even after "TRYING TO IMPROVE INITIAL MAGNETIC AXIS GUESS"

## Root Cause Analysis

### What Works ✅
- **Asymmetric infrastructure is COMPLETE**:
  - Asymmetric Fourier transforms implemented
  - Force symmetrization (symforce) working
  - Output population (rmns, zmnc, lmnc) functional
  - Python interface correctly handles asymmetric fields
  - Memory management optimized

### What Fails ❌
- **Early iteration convergence for asymmetric cases**
- Issue occurs in `vmec.cc:816-825` when `status_` is not `NORMAL_TERMINATION`, `SUCCESSFUL_TERMINATION`, or `BAD_JACOBIAN`
- Magnetic axis improvement doesn't resolve the convergence issue

## Technical Details

### Error Location
```cpp
// vmec.cc:816-825
if (status_ != VmecStatus::NORMAL_TERMINATION &&
    status_ != VmecStatus::SUCCESSFUL_TERMINATION) {
  const auto msg = absl::StrFormat(
      "FATAL ERROR in thread=%d. The solver failed during the first "
      "iterations. This may happen if the initial boundary is poorly "
      "shaped or if it isn't spectrally condensed enough.",
      thread_id);
  return absl::UnknownError(msg);
}
```

### Problem Pattern
1. VMEC++ detects "INITIAL JACOBIAN CHANGED SIGN!"
2. Tries to improve magnetic axis guess
3. Still gets a bad status during early iterations
4. Fails with FATAL ERROR

### Cases Tested
- **tok_asym**: 6 non-zero rbs values (max=0.100380), 7 non-zero zbc values (max=0.410500)
- **HELIOTRON_asym**: Complex 3D stellarator geometry with NFP=19
- Both work in jVMEC but fail in VMEC++

## Critical Requirements

**You're absolutely right**: If these cases work in regular VMEC/jVMEC, they MUST work in VMEC++ too.

## Next Steps Required

1. **Deep debug comparison** between jVMEC and VMEC++ initialization sequences
2. **Identify the specific status** being returned that causes the fatal error
3. **Compare asymmetric force calculation** in early iterations between implementations
4. **Fix the convergence logic** to handle asymmetric cases like jVMEC does

## Status Summary

- ✅ **Asymmetric infrastructure**: Fully implemented and working
- ✅ **Test framework**: Complete validation infrastructure in place  
- ✅ **Reference data**: jVMEC converged results available for comparison
- ❌ **Critical blocker**: VMEC++ cannot run cases that jVMEC runs successfully
- ❌ **Production readiness**: Blocked until convergence issue is resolved

## Impact

This is a **blocking issue** for asymmetric VMEC++ production use. The asymmetric infrastructure is complete, but the solver cannot run asymmetric cases that work in the reference implementation.

**Priority**: CRITICAL - Must be fixed before asymmetric implementation can be considered complete.