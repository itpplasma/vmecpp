# jVMEC Fourier Transform Implementation Analysis

Based on bytecode analysis of `FourierTransformsJava$1.run()`, here's how jVMEC handles Fourier transforms with asymmetric coefficients:

## Key Data Structures

### Fourier Coefficients
1. **Symmetric arrays** (always present):
   - `rmncc[ns][ntor+1][mpol+1]` - R symmetric cosine coefficients
   - `zmnsc[ns][ntor+1][mpol+1]` - Z symmetric sine coefficients  
   - `lmnsc[ns][ntor+1][mpol+1]` - Lambda symmetric sine coefficients

2. **Asymmetric arrays** (only if `lthreed=true`):
   - `rmnss[ns][ntor+1][mpol+1]` - R asymmetric sine coefficients
   - `zmncs[ns][ntor+1][mpol+1]` - Z asymmetric cosine coefficients
   - `lmncs[ns][ntor+1][mpol+1]` - Lambda asymmetric cosine coefficients

### Basis Functions
- `cosmu[ntheta][mpol+1]` - cos(m*theta) poloidal basis
- `sinmu[ntheta][mpol+1]` - sin(m*theta) poloidal basis
- `cosmum[ntheta][mpol+1]` - m*cos(m*theta) derivative basis
- `sinmum[ntheta][mpol+1]` - m*sin(m*theta) derivative basis
- `cosnv[nzeta][ntor+1]` - cos(n*zeta) toroidal basis
- `sinnv[nzeta][ntor+1]` - sin(n*zeta) toroidal basis
- `cosnvn[nzeta][ntor+1]` - n*cos(n*zeta) derivative basis
- `sinnvn[nzeta][ntor+1]` - n*sin(n*zeta) derivative basis

## Transform Algorithm

### Step 1: Toroidal Transform
First, transform from (m,n) Fourier space to (m,zeta) mixed space using a temporary array `temp[12][ns][nzeta]`:

```java
// For each poloidal mode m and toroidal angle zeta
for (m = 0; m < mpol; m++) {
    for (zeta_idx = 0; zeta_idx < nzeta; zeta_idx++) {
        for (n = 0; n <= ntor; n++) {
            // Symmetric terms (always computed)
            temp[0][s][zeta_idx] += rmncc[s][n][m] * cosnv[zeta_idx][n];
            temp[5][s][zeta_idx] += zmnsc[s][n][m] * cosnv[zeta_idx][n];  
            temp[9][s][zeta_idx] += lmnsc[s][n][m] * cosnv[zeta_idx][n];
            
            if (lthreed) {
                // Asymmetric terms (3D only)
                temp[1][s][zeta_idx] += rmnss[s][n][m] * sinnv[zeta_idx][n];
                temp[4][s][zeta_idx] += zmncs[s][n][m] * sinnv[zeta_idx][n];
                temp[8][s][zeta_idx] += lmncs[s][n][m] * sinnv[zeta_idx][n];
                
                // Derivative terms for symmetric
                temp[2][s][zeta_idx] += rmncc[s][n][m] * sinnvn[zeta_idx][n];
                temp[7][s][zeta_idx] += zmnsc[s][n][m] * sinnvn[zeta_idx][n];
                temp[11][s][zeta_idx] += lmnsc[s][n][m] * sinnvn[zeta_idx][n];
                
                // Derivative terms for asymmetric  
                temp[3][s][zeta_idx] += rmnss[s][n][m] * cosnvn[zeta_idx][n];
                temp[6][s][zeta_idx] += zmncs[s][n][m] * cosnvn[zeta_idx][n];
                temp[10][s][zeta_idx] += lmncs[s][n][m] * cosnvn[zeta_idx][n];
            }
        }
    }
}
```

### Step 2: Poloidal Transform
Then transform from (m,zeta) to real space (theta,zeta):

```java
// For each poloidal and toroidal angle
for (theta_idx = 0; theta_idx < ntheta; theta_idx++) {
    for (zeta_idx = 0; zeta_idx < nzeta; zeta_idx++) {
        // Symmetric contributions
        R[s][parity][zeta_idx][theta_idx] += temp[0][s][zeta_idx] * cosmu[theta_idx][m];
        Z[s][parity][zeta_idx][theta_idx] += temp[5][s][zeta_idx] * sinmu[theta_idx][m];
        Lambda[s][parity][zeta_idx][theta_idx] += temp[9][s][zeta_idx] * sinmu[theta_idx][m];
        
        // Derivatives for symmetric
        dRdTheta[s][parity][zeta_idx][theta_idx] += temp[0][s][zeta_idx] * sinmum[theta_idx][m];
        dZdTheta[s][parity][zeta_idx][theta_idx] += temp[5][s][zeta_idx] * cosmum[theta_idx][m];
        dLdTheta[s][parity][zeta_idx][theta_idx] += temp[9][s][zeta_idx] * cosmum[theta_idx][m];
        
        if (lthreed) {
            // Asymmetric contributions
            R[s][parity][zeta_idx][theta_idx] += temp[1][s][zeta_idx] * sinmu[theta_idx][m];
            Z[s][parity][zeta_idx][theta_idx] += temp[4][s][zeta_idx] * cosmu[theta_idx][m];
            Lambda[s][parity][zeta_idx][theta_idx] += temp[8][s][zeta_idx] * cosmu[theta_idx][m];
            
            // Additional derivative terms...
        }
    }
}
```

## Key Observations

1. **Parity Structure**: 
   - Symmetric R uses cosine basis (stellarator symmetric)
   - Symmetric Z and Lambda use sine basis
   - Asymmetric terms use opposite parity: R→sine, Z/Lambda→cosine

2. **2D/3D Control**: 
   - `lthreed = (ntor > 0)` - automatically set based on toroidal resolution
   - When `ntor=0` (axisymmetric/2D), `lthreed=false` and asymmetric terms are skipped
   - When `ntor>0` (3D), `lthreed=true` and asymmetric terms are included

3. **Spectral Condensation**:
   - The `xmpq` factor is applied to condensed quantities (R_con, Z_con)
   - This appears to be a preconditioning technique for m=1 modes

4. **Derivative Computation**:
   - Derivatives are computed analytically using the derivative basis functions
   - Both theta and zeta derivatives are computed in the same transform

5. **Parallelization**:
   - The transform is parallelized over flux surfaces
   - Uses a thread pool with size min(ns, maxNumThreads)

## Critical Implementation Details

### Transform Structure
The transform uses a two-step process:
1. **Toroidal transform**: (m,n) → (m,zeta) using temporary arrays
2. **Poloidal transform**: (m,zeta) → (theta,zeta) to real space

### Array Indexing
- Temporary array: `temp[12][surface][zeta]` holds intermediate results
- Real space arrays: `[surface][parity][zeta][theta]` where parity ∈ {0,1}
- The parity index relates to stellarator symmetry boundary conditions

### Special m=0,1 Handling
The code has special logic for m=0 and m=1:
```java
if (m == 0 || m == 1) {
    istart = 0;  // Start from surface 0
} else {
    istart = 1;  // Skip axis for m≥2
}
```

## Differences from VMEC++

The main differences from VMEC++ implementation:
1. **Naming Convention**: jVMEC uses clearer names (rmncc/rmnss vs rmn_s/rmn_a)
2. **Transform Order**: jVMEC does toroidal first, then poloidal
3. **Asymmetric Handling**: jVMEC has explicit lthreed flag that controls asymmetric terms
4. **Single Pass**: jVMEC computes values and derivatives in one transform