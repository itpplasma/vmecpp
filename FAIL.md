# Deep Investigation: Asymmetric Tokamak Jacobian Sign Issue

## Problem Summary

The asymmetric tokamak test case (`input.tok_asym`) fails with "INITIAL JACOBIAN CHANGED SIGN!" error, preventing convergence of the VMEC++ solver. This document records the comprehensive investigation into the root cause.

## Investigation Methodology

A systematic verification of every component in the pre-jacobian error sequence against reference implementations (jVMEC and educational_VMEC).

## Key Findings

### ✅ VERIFIED CORRECT: Boundary Processing Components

#### 1. Theta Shift Calculation (delta)
- **VMEC++**: `delta = -0.005357678034488968`
- **Reference**: `delta = -0.00535768` (runtime output)
- **Status**: ✅ EXACT MATCH

#### 2. Boundary Coefficient Parsing and Rotation
- All coefficient transformations verified against educational_VMEC reference data
- Theta rotation formulas match exactly: `cos(m*delta)`, `sin(m*delta)`
- Array indexing and storage verified correct
- **Status**: ✅ EXACT MATCH

#### 3. m=1 Constraint Application
- Scaling factor and constraint logic verified against reference
- Applied correctly during boundary processing
- **Status**: ✅ EXACT MATCH

#### 4. Jacobian Sign Check Logic
- **VMEC++**: `rTest = 1.91942, zTest = 3.62256`
- **jVMEC Reference**: `rTest = 1.9194245244986412, zTest = 3.6225550157797239`
- **Flip Condition**: `rTest * zTest * sign_of_jacobian > 0.0`
- **Status**: ✅ EXACT MATCH (within numerical precision)

### ❌ ROOT CAUSE IDENTIFIED: Axis Recomputation Algorithm

The issue is **NOT** in the jacobian sign check itself, but in the axis recomputation algorithm's inability to find a valid magnetic axis position for challenging asymmetric tokamak cases.

#### Current Algorithm Limitations
- Uses simple grid search with small perturbations around estimated center
- Enhanced with conservative strategies but still insufficient
- Fails for asymmetric cases with complex boundary shapes
- Located in: `src/vmecpp/cpp/vmecpp/vmec/boundaries/guess_magnetic_axis.cc:453-511`

#### Error Sequence
1. Jacobian sign check correctly identifies need for axis recomputation
2. `RecomputeMagneticAxisToFixJacobianSign()` called
3. Grid search fails to find point with positive jacobian
4. Solver terminates with "INITIAL JACOBIAN CHANGED SIGN!" error

## False Leads Eliminated

### ❌ Array Indexing Issues
- Initially suspected coefficient array ordering problems
- Comprehensive verification showed all indexing is correct
- VMEC++ uses `idx_mn = m * (ntor + 1) + n` correctly

### ❌ Coefficient Value Discrepancies  
- Educational_VMEC reference data of `rTest = 8.21383` was misleading
- Actual correct value is `rTest = 1.91942` (verified against jVMEC)
- VMEC++ computes exactly the right values

### ❌ Boundary Processing Errors
- All boundary processing steps verified correct
- No issues with theta shift, coefficient parsing, or m=1 constraint
- Problem is downstream in axis recomputation

## Technical Analysis

### Input Case Details
- **File**: `src/vmecpp/cpp/vmecpp/test_data/input.tok_asym`
- **Type**: Asymmetric tokamak (`ntor=0`, `mpol=7`, `lasym=true`)  
- **Boundary**: Complex shape with 9 toroidal harmonics for n=0 mode
- **Challenge**: Axis recomputation for asymmetric boundary

### Jacobian Sign Check Mathematics
For tokamak cases with `ntor=0`:
- Only n=0 toroidal mode present
- Jacobian check sums: `rTest = Σ rbcc[n=0][m=1]`, `zTest = Σ zbsc[n=0][m=1]`
- Since only one coefficient: `rTest = rbcc[0][1]`, `zTest = zbsc[0][1]`
- Values match reference implementations exactly

### Axis Recomputation Requirements
The current algorithm needs:
1. **Robust search strategies** for complex boundary shapes
2. **Polygon area method** for geometric jacobian evaluation
3. **Boundary centroid methods** as fallback strategies
4. **Better initial guesses** for asymmetric cases

## Solution Path

### Immediate Fix Required
Implement the **polygon area method** as suggested in the TODO comment:

```cpp
// TODO(jons): potentially more robust version of this
// - eval boundary in a given poloidal plane at equal theta intervals, enough
//   to satisfy Nyquist requirement  
// - compute signed polygon area
// --> handedness of polygon is given by sign of polygon area
```

### Implementation Strategy
1. Replace simple point-based jacobian check with polygon area method
2. Evaluate boundary at multiple theta points (Nyquist sampling)
3. Compute signed polygon area to determine orientation
4. Use area sign to determine correct jacobian orientation

## Investigation Timeline

- **Initial Error**: "INITIAL JACOBIAN CHANGED SIGN!" preventing convergence
- **Hypothesis 1**: Coefficient array indexing issues → ❌ ELIMINATED
- **Hypothesis 2**: Boundary processing errors → ❌ ELIMINATED  
- **Hypothesis 3**: Jacobian sign check logic → ❌ ELIMINATED
- **Root Cause**: Axis recomputation algorithm limitations → ✅ CONFIRMED

## Verification Against Reference Codes

- **jVMEC**: All boundary processing matches exactly
- **educational_VMEC**: Coefficient transformations verified
- **Both references**: Jacobian sign check logic identical

## Conclusion

The VMEC++ implementation is mathematically correct for all boundary processing components. The failure occurs in the axis recomputation algorithm, which lacks the robustness needed for challenging asymmetric tokamak cases. The solution is to implement the polygon area method for more reliable jacobian sign determination.

## Files Modified During Investigation

- `src/vmecpp/cpp/vmecpp/vmec/boundaries/boundaries.cc`: Added debug output
- `src/vmecpp/cpp/vmecpp/vmec/boundaries/guess_magnetic_axis.cc`: Enhanced search strategies
- `debug_boundary_values.py`: Created for coefficient verification
- `TODO.md`, `TOKAMAK.md`, `CLAUDE.md`: Updated with findings

## Next Steps

1. Implement polygon area method in `checkSignOfJacobian()`
2. Test with asymmetric tokamak case
3. Verify against reference implementations
4. Remove debug output and commit final solution