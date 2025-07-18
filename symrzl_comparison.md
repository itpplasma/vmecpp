# Comparison of symrzl Implementation: educational_VMEC vs VMEC++

## Purpose
The `symrzl` function symmetrizes R, Z, and lambda components by combining symmetric and antisymmetric contributions in stellarator geometry.

## Key Differences Found

### 1. Sign Conventions in Extended Interval (theta = [pi, 2*pi])

#### educational_VMEC (symrzl.f90)
```fortran
! Lines 46-52 in symrzl.f90
r1s(jk,i,mpar) = r1s(jka,ir,mpar) - r1a(jka,ir,mpar)  ! R: even parity
rus(jk,i,mpar) =-rus(jka,ir,mpar) + rua(jka,ir,mpar)  ! Ru: odd parity
z1s(jk,i,mpar) =-z1s(jka,ir,mpar) + z1a(jka,ir,mpar)  ! Z: odd parity
zus(jk,i,mpar) = zus(jka,ir,mpar) - zua(jka,ir,mpar)  ! Zu: even parity
```

#### VMEC++ (fourier_asymmetric.cc)
```cpp
// Lines 316-341 in fourier_asymmetric.cc
// R: R[extended] = R[reflected] - R_asym[reflected]
m_geometry.r1_e[idx_full] = m_geometry.r1_e[idx_reflected] - m_geometry_asym.r1_a[idx_reflected];

// dR/dtheta: dR/dtheta[extended] = -dR/dtheta[reflected] + dR_asym/dtheta[reflected]
m_geometry.ru_e[idx_full] = -m_geometry.ru_e[idx_reflected] + m_geometry_asym.ru_a[idx_reflected];

// Z: Z[extended] = -Z[reflected] + Z_asym[reflected]
m_geometry.z1_e[idx_full] = -m_geometry.z1_e[idx_reflected] + m_geometry_asym.z1_a[idx_reflected];

// dZ/dtheta: dZ/dtheta[extended] = dZ/dtheta[reflected] - dZ_asym/dtheta[reflected]
m_geometry.zu_e[idx_full] = m_geometry.zu_e[idx_reflected] - m_geometry_asym.zu_a[idx_reflected];
```

### 2. Index Mapping Differences

#### educational_VMEC
- Uses `ir = ntheta1 + 2 - i` for theta reflection
- Uses `jka = ireflect(jk)` for zeta reflection
- Works directly with the indices

#### VMEC++
- Uses `l_mirror = s.nThetaEven - l` for theta reflection
- Uses `k_mirror = (s.nZeta - k) % s.nZeta` for zeta reflection (line 306)
- Has additional complexity with index calculations

### 3. Direct Addition in Primary Interval

Both implementations add symmetric and antisymmetric parts directly for theta in [0, pi]:

#### educational_VMEC (lines 66-72)
```fortran
r1s(:,:n2,mpar) = r1s(:,:n2,mpar) + r1a(:,:n2,mpar)
rus(:,:n2,mpar) = rus(:,:n2,mpar) + rua(:,:n2,mpar)
z1s(:,:n2,mpar) = z1s(:,:n2,mpar) + z1a(:,:n2,mpar)
zus(:,:n2,mpar) = zus(:,:n2,mpar) + zua(:,:n2,mpar)
```

#### VMEC++ (lines 285-294)
```cpp
// Direct addition for primary interval
m_geometry.r1_e[idx] += m_geometry_asym.r1_a[idx];
m_geometry.ru_e[idx] += m_geometry_asym.ru_a[idx];
m_geometry.z1_e[idx] += m_geometry_asym.z1_a[idx];
m_geometry.zu_e[idx] += m_geometry_asym.zu_a[idx];
```

## Critical Finding

The sign conventions match between the two implementations for:
- R and its derivatives
- Z and its derivatives
- Lambda derivatives

However, there is a critical difference in the **zeta reflection index calculation**:
- VMEC++ uses both theta AND zeta reflection for the extended interval (line 306: `k_mirror = (s.nZeta - k) % s.nZeta`)
- educational_VMEC only mentions zeta reflection through `ireflect(jk)` but applies it differently

This extra zeta reflection in VMEC++ could be causing the incorrect Jacobian values in asymmetric cases.

## Recommendation

1. **Verify the zeta reflection logic**: Check if VMEC++ should be using zeta reflection in the symmetrization process for the extended theta interval.

2. **Simplify index calculations**: The VMEC++ implementation has more complex index calculations that could introduce errors.

3. **Add debug output**: Compare intermediate values during symmetrization between both codes to identify where the divergence occurs.

4. **Focus on the extended interval logic**: The primary interval (theta in [0,pi]) seems correct, but the extended interval (theta in [pi,2*pi]) has potential issues with the combined theta-zeta reflection.
