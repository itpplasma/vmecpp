# VMEC++ Asymmetric Mode Debugging Summary

## Root Cause Found
We identified that VMEC++ incorrectly handles the theta range in `guess_magnetic_axis.cc` for asymmetric cases:
- Only fills theta indices 0 to nThetaReduced-1
- Leaves indices 9-15 as zeros
- This causes rmin=0 instead of ~5.27, leading to wrong axis initialization

## Fix Applied
Modified `guess_magnetic_axis.cc` to use theta range 0 to nThetaReduced for asymmetric cases, matching educational_VMEC behavior.

## Current Status
Despite the theta range fix, VMEC++ still fails with BAD_JACOBIAN error. **Critical new findings from Jacobian tracing:**

### Debug Step 5 Results: Jacobian Tracing
- **Both codes have negative tau values initially** - this is NOT unique to VMEC++
- **Educational_VMEC**: tau ~ -0.75 to -3.17 initially, detects BAD_JACOBIAN, triggers axis recovery
- **VMEC++**: tau ~ -1.41 to -4.28 initially, fails immediately without reaching axis recovery
- **Key difference**: Educational_VMEC after axis recovery has tau ~ -0.18 with tau_main ~ -0.004 to +0.01
- **Critical issue**: VMEC++ doesn't seem to reach the axis recovery stage at all

## Additional Observations
1. **Theta shift warning**: "need to shift theta by delta = 0.463648" appears before BAD_JACOBIAN
2. **Multiple threads failing**: All OpenMP threads report the same FATAL ERROR
3. **Educational_VMEC succeeds**: Converges after 1214 iterations with same input

## Next Steps
1. **Investigate theta shift**: The delta=0.463648 shift might indicate another asymmetric handling issue
2. **Check boundary evaluation**: The theta shift happens in boundaries.cc, need to verify asymmetric boundary setup
3. **Compare Fourier transforms**: VMEC++ uses product basis vs educational_VMEC's combined basis
4. **Trace Jacobian calculation**: Find exactly where the Jacobian becomes negative after axis recovery

## Hypothesis
The theta range fix in axis guessing is correct but insufficient. There are likely multiple places where VMEC++ doesn't properly handle the asymmetric theta range or Fourier basis differences.
