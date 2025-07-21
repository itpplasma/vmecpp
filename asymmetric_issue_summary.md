# Asymmetric Fourier Transform Issue Summary

## Problem Description

The asymmetric Fourier transform in VMEC++ is not working correctly. When `lasym=True`, the code fails to converge even with tiny asymmetric perturbations.

## Root Cause

The asymmetric transform is **overwriting** the geometry arrays instead of **adding** to them. This can be seen in the debug output:

1. **Before asymmetric transform**: Geometry is computed correctly
   ```
   VMEC++ GEOMETRY: jF=1, kl=0, R=11, Z=0.0005
   VMEC++ GEOMETRY: jF=1, kl=1, R=10.8093, Z=0.58819
   ```

2. **After asymmetric transform**: All values become zero
   ```
   DEBUG: After 2D asymmetric transform, checking first few values:
     i=0: R=0, Z=0
     i=1: R=0, Z=0
   ```

## Expected Behavior

The asymmetric transform should:
1. First compute the symmetric contribution (from rmncc, zmnsc)
2. Then ADD the asymmetric contribution (from rmnsc, zmncc)

## Current Behavior

The asymmetric transform appears to:
1. Zero out the arrays
2. Only compute the asymmetric part
3. This results in near-zero geometry values that cause numerical issues

## Test Results

- **Symmetric case**: Works correctly (large aspect ratio tokamak converges)
- **Asymmetric case**: Fails even with tiny perturbations (0.001)

## Code Location

The issue is likely in the `FourierToReal2DAsymmFastPoloidal` function or how it's being called in the geometry computation.

## Recommendation

The asymmetric transform function needs to be modified to ADD to existing values rather than overwriting them. This matches the behavior shown in the test file `compare_implementations_test.cc` where the symmetric baseline is initialized first.