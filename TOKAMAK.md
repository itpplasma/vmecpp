# Enabling Tokamak Mode in VMECPP

This document provides a comprehensive analysis of how to enable tokamak mode (non-stellarator-symmetric configurations) in VMECPP. The analysis identifies all locations in the codebase that assume stellarator symmetry and documents the changes needed to support general tokamak configurations.

**Architecture Context**: VMECPP is a modern C++ reimplementation of the VMEC magnetohydrodynamic equilibrium solver with a Python interface (see AGENTS.md for complete architecture overview).

## Executive Summary

VMECPP currently has **full support for axisymmetric tokamaks** (`nfp=1`, `ntor=0`, `lasym=false`) and **partial support for non-stellarator-symmetric configurations** (`lasym=true`). The main limitation is that the `lasym=true` implementation is incomplete, with several TODO items remaining.

## Configuration Parameters for Different Magnetic Configurations

| Configuration Type | `nfp` | `ntor` | `lasym` | Support Status |
|-------------------|-------|--------|---------|----------------|
| Axisymmetric Tokamak | 1 | 0 | false | ✅ Fully supported |
| Stellarator (symmetric) | >1 | >0 | false | ✅ Fully supported |
| Non-symmetric Stellarator | >1 | >0 | true | ⚠️ Partially implemented |
| Non-axisymmetric Tokamak | 1 | >0 | true | ⚠️ Partially implemented |

## Key Symmetry Control Parameters

### Primary Configuration Flags

1. **`lasym`** (`src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:63-64`)
   - `false`: Assumes stellarator symmetry (up-down symmetric)
   - `true`: Allows non-stellarator-symmetric terms
   - **Key insight**: This is the primary flag controlling symmetry assumptions

2. **`nfp`** (`src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:66-67`)
   - Number of toroidal field periods
   - `nfp = 1` for tokamaks
   - `nfp > 1` for stellarators

3. **`lthreed`** (derived flag in `src/vmecpp/cpp/vmecpp/common/sizes/sizes.cc:84`)
   - `lthreed = (ntor > 0)`
   - Controls whether 3D toroidal coupling is used

## Fourier Mode Structure and Symmetry Assumptions

### Mode Coefficient Storage Based on Symmetry

#### Stellarator-Symmetric Coefficients (`lasym = false`)
**Magnetic axis:**
- `raxis_c`: R ~ cos(n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:217`)
- `zaxis_s`: Z ~ sin(n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:220`)

**Boundary:**
- `rbc`: R ~ cos(m*u - n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:237`)
- `zbs`: Z ~ sin(m*u - n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:241`)

#### Non-Stellarator-Symmetric Coefficients (`lasym = true`)
**Magnetic axis:**
- `raxis_s`: R ~ sin(n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:225`)
- `zaxis_c`: Z ~ cos(n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:229`)

**Boundary:**
- `rbs`: R ~ sin(m*u - n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:246`)
- `zbc`: Z ~ cos(m*u - n*v) (line `src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:250`)

### Internal Fourier Basis Functions

VMECPP uses a product basis internally with conditional allocation based on symmetry:

**Always present:**
- `rmncc`: R ~ cos(m*θ)*cos(n*ζ)
- `zmnsc`: Z ~ sin(m*θ)*cos(n*ζ)

**3D cases (`lthreed = true`):**
- `rmnss`: R ~ sin(m*θ)*sin(n*ζ)
- `zmncs`: Z ~ cos(m*θ)*sin(n*ζ)

**Non-stellarator-symmetric cases (`lasym = true`):**
- `rmnsc`: R ~ sin(m*θ)*cos(n*ζ)
- `zmncc`: Z ~ cos(m*θ)*cos(n*ζ)
- `rmncs`: R ~ cos(m*θ)*sin(n*ζ) (if `lthreed = true`)
- `zmnss`: Z ~ sin(m*θ)*sin(n*ζ) (if `lthreed = true`)

## Code Locations with Stellarator Symmetry Assumptions

### 1. Grid Size and Integration Weight Handling
**File:** `src/vmecpp/cpp/vmecpp/common/sizes/sizes.cc:104-133`

```cpp
if (lasym) {
  nThetaEff = nThetaEven;
} else {
  // use stellarator- or up/down-symmetry
  // --> only eval on reduced [0, pi] poloidal interval
  nThetaEff = nThetaReduced;
}
```

**Impact:** Stellarator-symmetric configurations use a reduced poloidal grid (0 to π), while asymmetric configurations require the full grid (0 to 2π).

### 2. Boundary Coefficient Allocation
**File:** `src/vmecpp/cpp/vmecpp/vmec/boundaries/boundaries.cc:26-37`

```cpp
if (s_.lthreed) {
  rbss.resize(s_.mpol * (s_.ntor + 1));
  zbcs.resize(s_.mpol * (s_.ntor + 1));
}
if (s_.lasym) {
  rbsc.resize(s_.mpol * (s_.ntor + 1));
  zbcc.resize(s_.mpol * (s_.ntor + 1));
  if (s_.lthreed) {
    rbcs.resize(s_.mpol * (s_.ntor + 1));
    zbss.resize(s_.mpol * (s_.ntor + 1));
  }
}
```

### 3. Mode Number Calculation
**File:** `src/vmecpp/cpp/vmecpp/common/sizes/sizes.cc:136-138`

```cpp
// m = 0: n = 0, 1, ..., ntor --> ntor + 1
// m > 0: n = -ntor, ..., ntor --> (mpol - 1) * (2 * ntor + 1)
mnmax = (ntor + 1) + (mpol - 1) * (2 * ntor + 1);
```

### 4. Tokamak-Specific Grid Requirements
**File:** `src/vmecpp/cpp/vmecpp/common/sizes/sizes.cc:60-65`

```cpp
if (ntor == 0 && nZeta < 1) {
  // Tokamak (ntor=0) needs (at least) nzeta=1
  nZeta = 1;
}
```

### 5. Stellarator Symmetry Mirroring
**File:** `src/vmecpp/cpp/vmecpp/free_boundary/surface_geometry/surface_geometry.cc:300-301`

```cpp
if (!s_.lasym) {
  // mirror into non-stellarator-symmetric half of poloidal range
```

**File:** `src/vmecpp/cpp/vmecpp/vmec/boundaries/guess_magnetic_axis.cc:335-336, 453-454`

```cpp
// flip-mirror geometry into non-stellarator-symmetric half in case of
// stellarator symmetry
```

### 6. Fourier Basis Mode-Dependent Scaling
**File:** `src/vmecpp/cpp/vmecpp/common/fourier_basis_fast_poloidal/fourier_basis_fast_poloidal.cc:66-70`

```cpp
if (m == 0) {
  mscale[m] = 1.0;
} else {
  mscale[m] = std::numbers::sqrt2;
}
```

### 7. Mode Parity and Sign Handling
**File:** `src/vmecpp/cpp/vmecpp/vmec/boundaries/boundaries.cc:216-234`

```cpp
int m_parity = ((m % 2 == 0) ? 1 : -1);
rbcc[idx_mn] *= m_parity;
zbsc[idx_mn] *= -m_parity;
if (s_.lthreed) {
  rbss[idx_mn] *= -m_parity;
  zbcs[idx_mn] *= m_parity;
}
```

## Incomplete Implementation Areas (`lasym = true`)

### Major TODO Items Found

1. **Core VMEC Algorithm** (`src/vmecpp/cpp/vmecpp/vmec/vmec/vmec.cc:1384, 1405`)
   ```cpp
   // TODO(jons) : non-stellarator-symmetric terms!
   ```

2. **Output Processing** (`src/vmecpp/cpp/vmecpp/vmec/output_quantities/output_quantities.cc:4572`)
   ```cpp
   // TODO(jons): implement symoutput() once lasym=true test case is set up
   ```

3. **Optional Data Structures** (`src/vmecpp/cpp/vmecpp/common/vmec_indata/vmec_indata.h:224, 229, 245, 250`)
   ```cpp
   // TODO(jurasic) make theses optional after the Eigen3 refactor
   ```

### Areas Requiring Completion for `lasym = true`

1. **Force Calculation Updates**: Core equilibrium solver needs updates for asymmetric terms
2. **Output Data Processing**: Symmetric/antisymmetric output separation 
3. **Memory Optimization**: Optional allocation of asymmetric coefficient arrays
4. **Test Coverage**: No test cases currently exist for `lasym = true` configurations

## Educational VMEC Reference Analysis

The educational VMEC implementation shows that asymmetric handling requires:

1. **Additional Fourier Transform Routines**:
   - `totzspa()`: Anti-symmetric contributions to inverse transforms
   - `symrzl()`: Sum symmetric/antisymmetric pieces appropriately  
   - `symforce()`: Symmetrize forces in u-v space

2. **Mode Scaling**: Odd modes scaled by sqrt(s) in transformations

3. **Conditional Algorithm Paths**: Different code paths for stellarator vs tokamak cases

## VMECPP Architecture Considerations for Tokamak Mode

### Fourier Basis Implementation (AGENTS.md)
VMECPP uses **two different Fourier representations** which impacts tokamak implementation:

**Internal Product Basis** (computational efficiency):
- Enables separable DFT operations using pre-computed basis arrays
- Must support asymmetric modes for `lasym=true`

**External Combined Basis** (researcher interface):
- Traditional VMEC format compatible with research literature
- Requires proper conversion routines for asymmetric cases

### Core Components Affected
- **VMEC Solver**: Main iterative equilibrium solver using multigrid methods
- **Ideal MHD Model**: Physics equations and force calculations for asymmetric configurations
- **Fourier Transforms**: Fast transforms for spectral decomposition with asymmetric terms
- **Geometry Engine**: Flux surface geometry and coordinate transformations

## Recommendations for Enabling Full Tokamak Mode

### Phase 1: Complete `lasym = true` Implementation (Following AGENTS.md Standards)
1. **Implement missing TODO items** in `vmec.cc` for asymmetric force calculations
   - Follow Google C++ Style Guide with physics domain adaptations
   - Preserve traditional physics variable names (e.g., `bsupu_`, `iotaf_`, `presf_`)
2. **Complete output processing** for asymmetric configurations
3. **Add comprehensive test cases** for `lasym = true` configurations
   - Use Google Test framework for C++ components
   - Use pytest for Python integration tests
4. **Optimize memory allocation** for optional asymmetric coefficient arrays

### Phase 2: Validation and Testing (AGENTS.md Testing Framework)
1. **Validate against educational VMEC** results for asymmetric cases
2. **Add tokamak-specific test cases** with `nfp = 1`, `lasym = true`
   - Follow test data organization in `src/vmecpp/cpp/vmecpp/test_data/`
   - Use existing examples structure (`examples/data/`)
3. **Performance benchmarking** for asymmetric vs symmetric cases
   - Implement Google Benchmark test cases
   - Focus on Fourier transform performance with asymmetric modes

### Phase 3: Development Workflow (AGENTS.md Guidelines)
1. **Pre-commit validation**: All code must pass `clang-format` and naming checks
2. **Incremental development**: Make small, focused changes that can be validated independently
3. **Build and test cycle**:
   ```bash
   cd src/vmecpp/cpp
   bazel build //...  # Ensure current code builds
   bazel test //vmecpp/...  # Run tests after changes
   pre-commit run --files <modified_files>  # Validate changes
   ```
4. **Testing requirements**:
   - Zero-crash policy: All errors as Python exceptions
   - Dual input format support: Both INDATA and JSON
   - Hot restart functionality for parameter scans

## Current Tokamak Support Status

### ✅ Fully Working
- **Axisymmetric tokamaks** (`nfp = 1`, `ntor = 0`, `lasym = false`)
- **Grid handling** for tokamak geometries
- **Mode number calculations** for axisymmetric cases
- **Boundary condition setup** for symmetric tokamaks

### ⚠️ Partially Implemented  
- **Non-axisymmetric tokamaks** (`nfp = 1`, `ntor > 0`, `lasym = true`)
- **Asymmetric boundary conditions** (data structures exist, algorithms incomplete)
- **Output processing** for asymmetric cases

### ❌ Missing
- **Complete force calculations** for `lasym = true`
- **Symmetric/antisymmetric output separation**
- **Comprehensive test coverage** for asymmetric cases
- **Performance optimization** for tokamak-specific algorithms

## Development Standards for Tokamak Implementation

### Coding Standards (AGENTS.md)
**C++ Code Requirements**:
- **Naming Conventions**: Classes (`CamelCase`), functions (`CamelCase`), constants (`kCamelCase`)
- **Physics Variables**: Preserve traditional names (e.g., `bsupu_`, `iotaf_`, `presf_`)
- **Function Parameters**: Use `m_` prefix for parameters that will be modified
- **Modern C++**: Use `std::array<>` instead of C-style arrays
- **ASCII Only**: Never use Unicode, special symbols, or non-ASCII characters

**Python Code Requirements**:
- **Style**: `ruff` linting and formatting with line length 88
- **Type Checking**: Must pass `pyright` type validation
- **Input Validation**: Use Pydantic models for type safety

### Architecture Integration
**Python-C++ Bridge**: 
- Automatic NumPy ↔ Eigen conversion for asymmetric coefficient arrays
- Exception translation from C++ to Python for tokamak-specific errors
- Memory-efficient data sharing for hot restart functionality

**SIMSOPT Compatibility**:
- Drop-in replacement support for tokamak optimization workflows
- Hot restart support for tokamak parameter scans
- Seamless integration with existing tokamak design tools

The codebase demonstrates excellent architectural design for handling both symmetric and asymmetric magnetic configurations, with clear separation of concerns and conditional compilation of the appropriate components based on symmetry flags.