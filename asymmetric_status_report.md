# VMEC++ Asymmetric Equilibria Status Report

## Summary

After extensive debugging and comparison with jVMEC, we have fixed several critical bugs in the asymmetric equilibria implementation:

### Fixed Issues

1. **Wrong derivative arrays** - Fixed using `asym_dRdTheta_odd` instead of `asym_dRdZeta`
2. **Zero Jacobian due to missing geometry copy** - Added copy from `m_ls_` arrays to working arrays
3. **Bounds checking rejecting valid coefficients** - Fixed to only check arrays used in 2D asymmetric
4. **Asymmetric transform zeroing symmetric baseline** - Restructured to call only asymmetric transform when `lasym=true`
5. **Transform logic** - Modified `FourierToReal2DAsymmFastPoloidal` to compute both symmetric and asymmetric parts

### Current Status

- The geometry values (R, Z) are now computed correctly with reasonable values
- Derivatives are being computed and are non-zero
- Jacobian is no longer zero
- However, the solver still fails with "poorly shaped boundary" error

### Remaining Issues

1. **Solver convergence failure** - Even with tiny asymmetric perturbations (0.05), the solver fails during first iterations
2. **Symmetric case regression** - The symmetric case now crashes with vector assertion failure
3. **Force residuals** - Need to check if forces are being computed correctly

### Next Steps

1. Fix the symmetric case regression by ensuring proper array initialization
2. Compare force calculations between VMEC++ and jVMEC
3. Investigate why solver fails even with correct geometry
4. Check if there are additional asymmetric-specific initialization steps needed

### Technical Details

The asymmetric Fourier transform now correctly:
- Computes symmetric baseline from `rmncc`/`zmnsc` coefficients  
- Adds asymmetric perturbations from `rmnsc`/`zmncc` coefficients
- Applies stellarator symmetry reflections for theta > pi
- Computes proper derivatives for Jacobian calculation

But the solver still cannot converge, suggesting there may be issues in:
- Force calculation
- Initial guess generation
- Preconditioner setup
- Or other asymmetric-specific components