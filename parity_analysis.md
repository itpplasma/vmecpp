# VMEC++ Parity Rules Analysis

## Current Implementation in SymmetrizeRealSpaceGeometry

### Symmetric Parts (_e, _o suffixes)
| Quantity | Parity | Rule for θ ∈ [π, 2π] |
|----------|--------|---------------------|
| R (r1_e, r1_o) | Even | f(2π-θ) = f(θ) |
| Z (z1_e, z1_o) | Even | f(2π-θ) = f(θ) |
| ∂R/∂θ (ru_e, ru_o) | Odd | f(2π-θ) = -f(θ) |
| ∂Z/∂θ (zu_e, zu_o) | Odd | f(2π-θ) = -f(θ) |
| ∂R/∂ζ (rv_e, rv_o) | Even | f(2π-θ) = f(θ) |
| ∂Z/∂ζ (zv_e, zv_o) | Even | f(2π-θ) = f(θ) |

### Asymmetric Parts (_a suffix)
| Quantity | Parity | Rule for θ ∈ [π, 2π] |
|----------|--------|---------------------|
| R (r1_a) | Odd | f(2π-θ) = -f(θ) |
| Z (z1_a) | Odd | f(2π-θ) = -f(θ) |
| ∂R/∂θ (ru_a) | Even | f(2π-θ) = f(θ) |
| ∂Z/∂θ (zu_a) | Even | f(2π-θ) = f(θ) |
| ∂R/∂ζ (rv_a) | Odd | f(2π-θ) = -f(θ) |
| ∂Z/∂ζ (zv_a) | Odd | f(2π-θ) = -f(θ) |

## Key Observation

The asymmetric parts have **opposite parity** compared to the symmetric parts:
- For R and Z: Symmetric is even, Asymmetric is odd
- For ∂/∂θ derivatives: Symmetric is odd, Asymmetric is even
- For ∂/∂ζ derivatives: Symmetric is even, Asymmetric is odd

## Potential Issue

When computing the Jacobian:
```
tau = ru * zs - rs * zu
```

Where:
- ru = ru_e + ru_a (symmetric + asymmetric)
- zs = ∂z/∂s (radial derivative)
- rs = ∂r/∂s (radial derivative)
- zu = zu_e + zu_a (symmetric + asymmetric)

The combination of opposite parities might be causing sign cancellations or incorrect values.

## Critical Finding in Code

Looking at the asymmetric combination in `SymmetrizeRealSpaceGeometry` for θ ∈ [π, 2π]:

```cpp
// R: R[extended] = R[reflected] - R_asym[reflected]
m_geometry.r1_e[idx_full] = m_geometry.r1_e[idx_reflected] - m_geometry_asym.r1_a[idx_reflected];

// dR/dtheta: dR/dtheta[extended] = -dR/dtheta[reflected] + dR_asym/dtheta[reflected]
m_geometry.ru_e[idx_full] = -m_geometry.ru_e[idx_reflected] + m_geometry_asym.ru_a[idx_reflected];
```

The sign pattern shows:
- R_asym is **subtracted** from R_symmetric
- ru_asym is **added** to -ru_symmetric

This inconsistent sign treatment between R and its derivative could be causing the Jacobian issues.

## Hypothesis

The sign conventions in the asymmetric combination might be incorrect. Educational_VMEC likely uses
a different sign pattern that maintains consistency between quantities and their derivatives.
