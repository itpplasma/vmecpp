# jVMEC Non-Stellarator-Symmetric Implementation Findings

This document summarizes the key findings from the jVMEC codebase related to non-stellarator-symmetric (lasym) field implementations that can help guide the implementation in vmecpp.

## 1. lasym Flag and Configuration

### Location: `/home/ert/code/jVMEC/src/main/java/de/labathome/jvmec/VmecIndata.java`
- Line 279: `public boolean lasym;`
- Line 347: Default initialization: `lasym = false;`
- Used to enable non-stellarator-symmetric mode

### Test Cases with lasym=true:
- `/home/ert/code/jVMEC/src/test/resources/input.tok_asym` - Tokamak asymmetric test case
- `/home/ert/code/jVMEC/src/test/resources/input.HELIOTRON_asym` - Heliotron asymmetric test case

## 2. Asymmetric Force Components

### Location: `/home/ert/code/jVMEC/src/main/java/de/labathome/jvmec/RealSpaceForces.java`

The code defines separate arrays for asymmetric force components (lines 47-77):
```java
// asymmetric force components
public double[][][][] armn_asym;  // [ns][2][nzeta][ntheta2]
public double[][][][] brmn_asym;
public double[][][][] crmn_asym;
public double[][][][] azmn_asym;
public double[][][][] bzmn_asym;
public double[][][][] czmn_asym;
public double[][][][] blmn_asym;
public double[][][][] clmn_asym;
public double[][][][] fRcon_asym;
public double[][][][] fZcon_asym;
```

Memory allocation for asymmetric components (lines 134-148):
```java
if (lasym) {
    // asymmetric real-space forces
    armn_asym = new double[numSurfaces][m_even_odd][nzeta][ntheta3];
    brmn_asym = new double[numSurfaces][m_even_odd][nzeta][ntheta3];
    // ... etc
}
```

## 3. Force Symmetrization (symforce)

### Location: `/home/ert/code/jVMEC/src/main/java/de/labathome/jvmec/RealSpaceForces.java`

The `symmetrizeForces()` method (lines 599-698) implements the force symmetrization:

Key symmetrization formulas (lines 636-652):
```java
// Symmetric and antisymmetric decomposition
armn_asym[j][mParity][k][l] = 0.5 * (armn[j][mParity][k][l] - armn[j][mParity][kReversed][lReversed]);
armn_sym[j][k]              = 0.5 * (armn[j][mParity][k][l] + armn[j][mParity][kReversed][lReversed]);

// Note the different signs for different components
brmn_asym[j][mParity][k][l] = 0.5 * (brmn[j][mParity][k][l] + brmn[j][mParity][kReversed][lReversed]);
brmn_sym[j][k]              = 0.5 * (brmn[j][mParity][k][l] - brmn[j][mParity][kReversed][lReversed]);
```

## 4. Fourier Transform Extensions

### Location: `/home/ert/code/jVMEC/src/main/java/de/labathome/jvmec/FourierTransformsJava.java`

### totzsps (Symmetric transform, line 150)
Standard transform for stellarator-symmetric configurations

### totzspa (Asymmetric transform, line 255)
Additional transform when lasym=true, processes asymmetric Fourier coefficients:
```java
// totzspa
for (int m = 0; m < mpol; ++m) {
    // Process rmnsc, rmncs, zmncc, zmnss, lmncc, lmnss coefficients
}
```

### symrzl (Symmetry operations, line 335)
Extends geometry arrays for full theta range [0, 2π] using symmetry properties:
```java
// FIRST SUM SYMMETRIC, ANTISYMMETRIC PIECES ON EXTENDED INTERVAL, THETA = [PI,2*PI]
for (int l = ntheta2; l < ntheta1; ++l) {
    R[j][mParity][k][l] = R[j][mParity][kr][lr] - asym_R[j - mystart][mParity][kr][lr];
    // Different signs for different components
}
```

### tomnsps and tomnspa (lines 554, 734)
Fourier transforms for forces in symmetric and asymmetric cases

## 5. Output Symmetrization (symoutput)

### Location: `/home/ert/code/jVMEC/src/main/java/de/labathome/jvmec/OutputQuantities.java`

The symoutput implementation (lines 3568-3668) symmetrizes output quantities:
```java
if (lasym) {
    // Symmetric/antisymmetric decomposition for output quantities
    modBAsym[j][k][l] = 0.5 * (totalPressure[j][k][l] - totalPressure[j][kReversed][lReversed]);
    tmpModBSymm[k][l] = 0.5 * (totalPressure[j][k][l] + totalPressure[j][kReversed][lReversed]);
    
    // Note: BSubS has reversed symmetry
    bSubSAsym[j][k][l] = 0.5 * (BSubS[j][k][l] + BSubS[j][kReversed][lReversed]);
    tmpBSubSSymm[k][l] = 0.5 * (BSubS[j][k][l] - BSubS[j][kReversed][lReversed]);
}
```

## 6. Time Step Optimization

### Location: `/home/ert/code/jVMEC/src/main/java/de/labathome/jvmec/IdealMHDModel.java`

The `evolve()` method (lines 1159-1195) implements adaptive time stepping:
```java
public void evolve(State physicalForces, int numIterations) {
    // Compute damping parameter based on force residual history
    if (numIterations > iter1 && fSq1 != 0.0) {
        dTau = Math.min(Math.abs(Math.log(fSq1 / previousFSq)), 0.15);
    }
    
    // Average over N_DAMP=10 iterations
    meanTau = DoubleStream.of(invTau).average().getAsDouble();
    dTau = state.timeStep * meanTau / 2.0;
    
    // Apply time step with damping
    double velocityScale = 1.0 / (1.0 + dTau);
    double conjugationParameter = 1.0 - dTau;
    state.performTimeStep(velocityScale, conjugationParameter, state.timeStep, physicalForces);
}
```

## 7. Key Implementation Patterns

1. **Dual Arrays**: Symmetric and asymmetric components are stored separately
2. **Index Reflection**: `kReversed = (nzeta - k) % nzeta`, `lReversed = (ntheta1 - l) % ntheta1`
3. **Sign Conventions**: Different components have different sign rules in symmetrization
4. **Conditional Allocation**: Asymmetric arrays only allocated when `lasym=true`
5. **Extended Theta Range**: Full range [0, 2π] constructed from [0, π] using symmetry

## 8. Test Infrastructure

### Location: `/home/ert/code/jVMEC/src/test/java/de/labathome/test/checkpoints/TestForceSymmetrization.java`

Comprehensive test for force symmetrization that validates:
- Symmetric components after symmetrization
- Asymmetric components after symmetrization
- Comparison with reference data from Fortran VMEC

## Recommendations for vmecpp Implementation

1. **Add lasym flag** to VmecIndata structure
2. **Extend force arrays** with asymmetric components when lasym=true
3. **Implement symforce** function following the sign conventions shown above
4. **Extend Fourier transforms** with totzspa and symrzl functionality
5. **Add symoutput** for output quantity symmetrization
6. **Port adaptive timestep** algorithm from evolve method
7. **Create test cases** using tok_asym and HELIOTRON_asym configurations
8. **Validate** against jVMEC reference data in the test resources