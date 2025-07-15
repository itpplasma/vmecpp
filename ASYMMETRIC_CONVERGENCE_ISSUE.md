# VMEC++ Asymmetric Convergence Issue Analysis

## Problem Summary

VMEC++ fails to converge for asymmetric cases with "INITIAL JACOBIAN CHANGED SIGN!" error, while the same input files work correctly with educational_VMEC.

## Root Cause Analysis

### 1. Boundary Handling is Mathematically Identical

Comprehensive comparison between VMEC++ and educational_VMEC boundary handling shows:
- **checkSignOfJacobian()**: Identical logic and implementation
- **flipTheta()**: Identical parity transformations
- **Delta calculation**: Same corrected Matt Landreman formula
- **Asymmetric coefficient processing**: Identical transformations

### 2. Axis Recomputation Algorithm

The axis recomputation algorithm (`RecomputeMagneticAxisToFixJacobianSign`) appears to be correctly implemented:
- Grid search algorithm matches educational_VMEC logic
- Asymmetric handling includes proper coefficient processing
- Toroidal plane processing is correct

### 3. Key Findings

1. **Boundary coefficients are processed correctly**: The boundary setup produces the same internal arrays as educational_VMEC
2. **Axis recomputation runs but doesn't converge**: The algorithm attempts to fix the jacobian sign but fails to find a valid solution
3. **Infinite loop occurs**: The axis recomputation is called repeatedly without success

## Suspected Issues

### 1. Boundary Initialization Timing

The issue may be related to **when** the boundary setup occurs relative to other initialization steps. The jacobian sign check happens during boundary processing, but asymmetric cases may require different initialization order.

### 2. Geometric Constraints

Asymmetric cases may have stricter geometric constraints that the axis recomputation algorithm cannot satisfy. The grid search may be too coarse or the search space too limited.

### 3. Numerical Precision

Small numerical differences in the jacobian computation could cause the sign check to fail when it should pass.

## Attempted Fixes

1. **Conservative axis recomputation**: Added fallback logic for asymmetric cases when grid search fails
2. **Improved robustness**: Added smaller perturbation search around center point
3. **Boundary coefficient validation**: Verified all coefficient arrays are properly initialized

## Test Results

After implementing fixes, the issue persists:
- **tok_asym**: Still fails with jacobian sign error
- **HELIOTRON_asym**: Still fails with jacobian sign error
- **Symmetric cases**: Continue to work correctly

## Working Reference Implementation

The same input files (`input.tok_asym`, `input.HELIOTRON_asym`) work correctly with educational_VMEC:
- `../educational_VMEC/build/bin/xvmec input.tok_asym` - **CONVERGES**
- VMEC++ with same file - **FAILS**

## Recommendations

### Short-term Workaround
1. Use educational_VMEC for asymmetric cases until this issue is resolved
2. Document the limitation in VMEC++ documentation

### Long-term Solution
1. **Detailed debugging**: Add extensive logging to boundary initialization to compare step-by-step with educational_VMEC
2. **Geometric validation**: Implement stricter validation of boundary geometry before jacobian sign check
3. **Alternative axis algorithms**: Consider implementing the Zeno Tecchiolli axis estimation method mentioned in the code

## Technical Details

### Error Sequence
1. Boundary setup calls `checkSignOfJacobian()` 
2. Returns true (jacobian sign needs flipping)
3. Calls `flipTheta()` to modify boundary coefficients
4. During first iteration, jacobian sign is still wrong
5. Calls `RecomputeMagneticAxisToFixJacobianSign()`
6. Axis recomputation fails to find valid solution
7. Loop repeats until max iterations reached

### Code Locations
- Boundary setup: `src/vmecpp/cpp/vmecpp/vmec/boundaries/boundaries.cc`
- Axis recomputation: `src/vmecpp/cpp/vmecpp/vmec/boundaries/guess_magnetic_axis.cc`
- Main loop: `src/vmecpp/cpp/vmecpp/vmec/vmec/vmec.cc`

## Status

**UNRESOLVED** - This is a fundamental issue in VMEC++ asymmetric handling that prevents convergence for valid asymmetric equilibria.

The boundary mathematics are correct, but the geometric initialization fails to produce a valid initial state for the asymmetric solver.