# Asymmetric Geometry Doubling Bug Analysis

## Executive Summary

VMECPP has a bug where forces are approximately doubled when running with `lasym=true` (non-stellarator symmetric configurations). The root cause is an architectural difference between VMECPP and jVMEC in how asymmetric Fourier modes are handled.

## Root Cause Analysis

### The Bug

In `SymmetrizeRealSpaceGeometry` (fourier_asymmetric.cc, lines 271-301), VMECPP adds asymmetric contributions to BOTH even and odd components:

```cpp
m_geometry.r1_e[idx] += m_geometry_asym.r1_a[idx];
m_geometry.r1_o[idx] += m_geometry_asym.r1_a[idx];  // This doubles the contribution!
```

When these components are later combined as `full = even + sqrt(s) * odd`, the asymmetric contribution appears twice, effectively doubling the forces.

### Architectural Difference

**jVMEC Implementation:**
- Asymmetric arrays have an mParity dimension: `asym_R[j][mParity][k][l]`
- Even-m modes go to mParity=0, odd-m modes go to mParity=1
- When combining, each mParity is added to its corresponding component

**VMECPP Implementation:**
- Asymmetric arrays are single dimensional: `r1_a[idx]`
- All m-modes (even and odd) are mixed in a single array
- The same mixed array is added to both even and odd components

## Why Simple Fixes Failed

### Attempt 1: Add only to even component
```cpp
m_geometry.r1_e[idx] += m_geometry_asym.r1_a[idx];
// m_geometry.r1_o[idx] += m_geometry_asym.r1_a[idx];  // Removed
```
**Result:** Solver fails with "INITIAL JACOBIAN CHANGED SIGN"

### Attempt 2: Scale by 0.5
```cpp
m_geometry.r1_e[idx] += 0.5 * m_geometry_asym.r1_a[idx];
m_geometry.r1_o[idx] += 0.5 * m_geometry_asym.r1_a[idx];
```
**Result:** Same solver failure

### Attempt 3: Weighted distribution
Tried to distribute based on sqrt(s) weighting.
**Result:** Same solver failure

All these approaches fail because they disrupt the initial equilibrium guess, which is extremely sensitive to the geometry representation.

## Proper Solution

The correct fix requires architectural changes:

### Option 1: Modify Asymmetric DFT (Recommended)
Modify `FourierToReal3DAsymmFastPoloidal` to produce separate even/odd outputs:
```cpp
struct RealSpaceGeometryAsym {
  std::span<double> r1_a_e;  // Even-m modes
  std::span<double> r1_a_o;  // Odd-m modes
  // ... similar for other components
};
```

Then in symrzl:
```cpp
m_geometry.r1_e[idx] += m_geometry_asym.r1_a_e[idx];
m_geometry.r1_o[idx] += m_geometry_asym.r1_a_o[idx];
```

### Option 2: Track m-parity During DFT
Modify the DFT to track which modes contribute and distribute accordingly during the combination step.

## Impact

This bug affects all non-stellarator symmetric configurations:
- Asymmetric tokamaks (e.g., tok_asym, ITER-like)
- Asymmetric stellarators (e.g., HELIOTRON_asym)

The doubled forces prevent proper convergence and produce incorrect equilibria for these configurations.

## Temporary Workaround

Until the architectural fix is implemented, users should be aware that VMECPP may produce incorrect results for asymmetric configurations. The symmetric case (lasym=false) is not affected.

## References

1. jVMEC implementation: `src/main/java/de/labathome/jvmec/FourierTransformsJava.java`, lines 335-392
2. VMECPP bug location: `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.cc`, lines 264-304
3. Related test: `tests/test_simsopt_compat.py::test_asymmetric_run`