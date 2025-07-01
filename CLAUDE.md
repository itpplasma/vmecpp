# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Building and Installation
```bash
# Build C++ core with CMake
cmake -B build && cmake --build build --parallel

# Install as editable Python package (rebuilds C++ automatically)
pip install -e .

# Build C++ with Bazel (from src/vmecpp/cpp/)
bazel build //...
```

### Code Quality and Testing
```bash
# Python linting and formatting
ruff check && ruff format

# Type checking
pyright

# Pre-commit validation
pre-commit run --all-files

# Python tests
pytest

# C++ tests (requires Bazel from src/vmecpp/cpp/)
bazel test //vmecpp/...

# Run specific test
pytest tests/test_init.py
bazel test //vmecpp/vmec/vmec:vmec_test
```

### Running VMEC++
```bash
# Command line usage
python -m vmecpp examples/data/w7x.json
python -m vmecpp examples/data/input.w7x

# C++ standalone
./build/vmec_standalone examples/data/solovev.json
```

## Architecture Overview

VMECPP is a modern C++ reimplementation of the VMEC magnetohydrodynamic equilibrium solver with a comprehensive Python interface. It employs a **dual build system architecture** using both CMake (Python packaging) and Bazel (C++ development).

### Core Computational Engine (`src/vmecpp/cpp/vmecpp/`)

**Physics Core**:
- `vmec/ideal_mhd_model/`: Core MHD physics equations and force calculations
- `vmec/vmec/`: Main iterative equilibrium solver with multigrid methods
- `vmec/fourier_geometry/`: Flux surface geometry and coordinate transformations
- `free_boundary/nestor/`: NESTOR vacuum solver for plasma-vacuum interface

**Mathematical Infrastructure**:
- `common/fourier_basis_fast_*/`: DFT-based Fourier transforms using **two basis representations**:
  - **Product basis** (internal): `cos(m*θ)*cos(n*ζ)` - computational efficiency
  - **Combined basis** (external): `cos(m*θ - n*ζ)` - researcher interface
- `common/magnetic_configuration_*/`: Equilibrium data structures and validation

**System Components**:
- `common/vmec_indata/`: Input validation and parsing with Pydantic integration
- `vmec/output_quantities/`: Comprehensive result computation and formatting

### Python Interface Layer (`src/vmecpp/`)

**Data Models**:
- `VmecInput`: Pydantic model with automatic validation for all input parameters
- `VmecOutput`: Container for all output data (wout, jxbout, mercier, threed1)
- `run()`: Primary computational entry point with hot restart support

**Integration Capabilities**:
- `simsopt_compat.py`: Drop-in replacement for SIMSOPT optimization workflows
- `_free_boundary.py`: External magnetic field handling and MGRID support
- **Python-C++ Bridge** (`pybind11/`): Automatic NumPy ↔ Eigen conversion with zero-crash policy

### Key Architectural Features

**Dual Input Format Support**:
- **JSON format**: Modern VMEC++ native with full validation
- **INDATA format**: Legacy Fortran compatibility via automatic conversion

**Hot Restart Capability**: Initialize from previous converged state for efficient parameter scans

**Multi-Threading**: OpenMP parallelization (not MPI like Fortran VMEC)

**Zero-Crash Policy**: All errors reported as Python exceptions with detailed context

## Critical Development Guidelines

### Mandatory Code Standards

**ALWAYS consult `VMECPP_NAMING_GUIDE.md` before making ANY changes**:
- **Physics variables**: Preserve traditional names (`bsupu_`, `iotaf_`, `presf_`)
- **Classes**: `CamelCase` (e.g., `IdealMhdModel`)
- **Functions**: `CamelCase` (e.g., `ComputeGeometry()`)
- **Member variables**: `snake_case_` with trailing underscore
- **Function parameters**: Use `m_` prefix for modified parameters

**ASCII-Only Requirement**:
- Never use Unicode characters in code, comments, or documentation
- Use LaTeX notation for mathematics (e.g., `\nabla p`, `\sum_{m,n}`)

**Pre-commit Validation**:
- All code must pass `clang-format` (Google C++ style)
- Python code must pass `ruff` and `pyright`
- Must include newline at end of files

### Build System Usage

**CMake vs Bazel**:
- **CMake**: Python package development, editable installs
- **Bazel**: C++ core development, testing, optimization

**Key CMake Features**:
- **scikit-build-core** backend with automatic C++ rebuilds
- **Editable installs**: `pip install -e .` rebuilds C++ on changes
- **Cross-platform**: Linux, macOS, Windows support

**Bazel Configurations** (from `src/vmecpp/cpp/.bazelrc`):
- `--config=opt`: Optimized release builds
- `--config=debug`: Debug builds with symbols
- `--config=asan`: AddressSanitizer for memory debugging

## Testing Infrastructure

### Multi-Repository Testing Strategy

**Local Tests** (`tests/`): Python API integration and Pydantic validation

**External C++ Tests**: Physics validation in separate repos:
- `proximafusion/vmecpp_large_cpp_tests`: Core physics accuracy
- `proximafusion/vmecpp-validation`: Bit-for-bit Fortran VMEC v8.52 comparison

**Test Execution Patterns**:
```bash
# Python integration tests
pytest tests/test_simsopt_compat.py -v

# C++ component tests
bazel test //util/file_io:file_io_test --test_output=all

# Run all tests with verbose output
bazel test //... --test_output=errors
```

## Physics Domain Knowledge

### Fourier Basis Architecture
**Critical**: Read `docs/fourier_basis_implementation.md` before modifying Fourier code.

**Two Basis System**:
- **Internal (Product)**: Separable DFT using `cos(m*θ)*cos(n*ζ)` - optimized for computation
- **External (Combined)**: Traditional `cos(m*θ - n*ζ)` - compatible with research literature

**Mode Handling**: Only `n ≥ 0` coefficients stored, exploiting VMEC symmetry

**Symmetry Control**:
- `lasym`: Controls stellarator symmetry assumptions
- `nfp`: Number of field periods (=1 for tokamaks)
- `lthreed`: Derived flag for 3D vs axisymmetric handling

### Input/Output Patterns

**Standard Fixed-Boundary Run**:
```python
import vmecpp
input = vmecpp.VmecInput.from_file("w7x.json")
output = vmecpp.run(input)
output.wout.save("wout_result.nc")
```

**Hot Restart for Parameter Scans**:
```python
base_output = vmecpp.run(base_input)
perturbed_input.rbc[0, 0] *= 1.1
# Single multigrid step required for hot restart
perturbed_input.ns_array = perturbed_input.ns_array[-1:]
hot_output = vmecpp.run(perturbed_input, restart_from=base_output)
```

**Free-Boundary Execution**:
```python
# Requires mgrid_file specification in input
input.lfreeb = True
input.mgrid_file = "path/to/mgrid.nc"
output = vmecpp.run(input)  # Automatically uses NESTOR solver
```

## Development Workflow

### Code Modification Process
1. **Read relevant documentation**: `VMECPP_NAMING_GUIDE.md`, component docs
2. **Understand existing patterns**: Use Task tool for architecture searches
3. **Make focused changes**: Small, testable modifications
4. **Validate early**: Run pre-commit hooks on modified files
5. **Test thoroughly**: Both C++ and Python components

### Common Development Tasks

**Adding new physics functionality**:
- Extend `IdealMhdModel` for new force calculations
- Update `OutputQuantities` for new results
- Add Pydantic validation in `VmecInput`

**Modifying Fourier operations**:
- Understand product vs combined basis distinction
- Preserve numerical accuracy in transformations
- Test with both symmetric and asymmetric configurations

**Python API changes**:
- Update type hints and Pydantic models
- Ensure backward compatibility
- Add comprehensive docstrings

### Integration Points

**SIMSOPT Compatibility**: Changes to `VmecInput`/`VmecOutput` may require updates to `simsopt_compat.py`

**Build System Integration**: C++ API changes require corresponding pybind11 binding updates

**External Dependencies**: Core physics depends on Eigen (linear algebra) and abseil (utilities)

## Key File Locations

**Configuration Files**:
- `pyproject.toml`: Python packaging, dependencies, build configuration
- `src/vmecpp/cpp/.bazelrc`: C++ build configurations and compiler flags
- `src/vmecpp/cpp/MODULE.bazel`: Bazel module dependencies

**Documentation**:
- `docs/the_numerics_of_vmecpp.pdf`: Mathematical foundations
- `docs/fourier_basis_implementation.md`: Fourier transform implementation details
- `VMECPP_NAMING_GUIDE.md`: Comprehensive coding standards

**Test Data**:
- `examples/data/`: Sample input files (JSON and INDATA formats)
- `src/vmecpp/cpp/vmecpp/test_data/`: C++ test configurations and reference outputs