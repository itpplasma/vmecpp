# VMECPP Benchmarking Guide

This document describes how to run and add benchmark test cases in VMECPP for performance testing and regression detection.

## Current Benchmarking Status

### ✅ Available Infrastructure
- **Google Benchmark 1.8.2** included as Bazel dependency
- **Optimized build configuration** with `-O3 -fno-math-errno`
- **Functions designed for benchmarking** in core computation modules
- **Performance examples** demonstrating scaling behavior
- **CMake and Bazel build systems** with release mode optimization
- **OpenMP parallelization** for multi-threaded force calculations

### ⚠️ Partially Implemented
- Google Benchmark framework available but **not actively used**
- No dedicated benchmark executables currently exist
- No automated performance regression testing in CI/CD

### ❌ Missing
- Systematic benchmark test suite
- Performance regression detection
- Timing instrumentation in core functions

## Performance Examples (Current Approach)

### 1. Hot Restart Scaling Analysis

**File:** `examples/hot_restart_scaling.py`

```bash
# Run convergence scaling analysis
cd examples/
python hot_restart_scaling.py
```

**Purpose:** Demonstrates how perturbation size affects convergence iterations in hot-restarted equilibrium computations.

**Metrics Measured:**
- Iteration count vs perturbation amplitude
- Convergence behavior visualization

### 2. VMEC++ vs PARVMEC Comparison

**File:** `examples/compare_vmecpp_to_parvmec.py`

```bash
# Compare performance against reference implementation
cd examples/
python compare_vmecpp_to_parvmec.py
```

**Purpose:** Comparative analysis of VMEC++ performance and accuracy against PARVMEC reference.

### 3. MPI Parallel Finite Difference

**File:** `examples/mpi_finite_difference.py`

```bash
# Demonstrate parallel performance
mpirun -n 4 python examples/mpi_finite_difference.py
```

**Purpose:** Shows parallel workload distribution for Jacobian evaluation.

## Build Configuration for Performance

### Release Mode Optimization

```bash
# CMake Release build with full optimization (from AGENTS.md)
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel

# Bazel optimized build (from src/vmecpp/cpp/)
cd src/vmecpp/cpp/
bazel build -c opt //...

# Install as editable Python package (rebuilds C++ automatically)
pip install -e .
```

### Enable OpenMP Parallelization

```bash
# Set OpenMP threads for multi-threaded force calculations
export OMP_NUM_THREADS=8

# VMECPP uses OpenMP parallelization (not MPI like Fortran VMEC)
# Multi-threading optimized for force calculations and Fourier transforms
```

## How to Add Benchmark Test Cases

### Step 1: Create Benchmark Source File

Create a new file `src/vmecpp/cpp/vmecpp/[component]/[component]_benchmark.cc`:

```cpp
#include <benchmark/benchmark.h>
#include "vmecpp/[component]/[component].h"

// Benchmark a specific function
static void BM_ComponentFunction(benchmark::State& state) {
  // Setup test data
  auto test_data = CreateTestData(state.range(0));
  
  // Benchmark loop
  for (auto _ : state) {
    // Call function to benchmark
    auto result = ComponentFunction(test_data);
    // Prevent optimization
    benchmark::DoNotOptimize(result);
  }
  
  // Optional: Set custom counters
  state.SetComplexityN(state.range(0));
  state.SetItemsProcessed(state.iterations() * state.range(0));
}

// Register benchmark with different input sizes
BENCHMARK(BM_ComponentFunction)
    ->RangeMultiplier(2)
    ->Range(64, 8192)
    ->Complexity(benchmark::oN);

BENCHMARK_MAIN();
```

### Step 2: Add Bazel BUILD Target

Add to the appropriate `BUILD.bazel` file:

```bazel
cc_binary(
    name = "component_benchmark",
    srcs = ["component_benchmark.cc"],
    deps = [
        ":component",
        "@google_benchmark//:benchmark_main",
    ],
    testonly = True,
)
```

### Step 3: Run Benchmark

```bash
# Build and run benchmark
bazel run //vmecpp/[component]:component_benchmark

# Run with specific options
bazel run //vmecpp/[component]:component_benchmark -- \
    --benchmark_format=json \
    --benchmark_out=results.json
```

## Recommended Benchmark Test Cases

### Core Computation Functions

Based on code analysis, these functions are designed for benchmarking:

1. **Fourier Transform Performance** (Critical for VMECPP performance)
   ```cpp
   // Fast transforms for spectral decomposition (AGENTS.md architecture)
   ForcesToFourier3DSymmFastPoloidal()   // Force calculations to Fourier space
   FourierToReal3DSymmFastPoloidal()     // Fourier to real-space transforms
   ```

2. **Fourier Basis Operations** (Product vs Combined basis conversions)
   ```cpp
   // Two different Fourier representations (see AGENTS.md)
   CombinedToProduct()  // Traditional VMEC format → computational efficiency
   ProductToCombined()  // Computational efficiency → researcher interface
   ```

3. **VMEC Solver** (Main iterative equilibrium solver)
   ```cpp
   // Multigrid methods for equilibrium solving
   IterateEquilibrium()  // Core VMEC algorithm iterations
   ```

4. **Ideal MHD Model** (Physics equations and force calculations)
   ```cpp
   // Force balance calculations (computationally intensive)
   ComputeForces()      // MHD force calculations
   UpdateGeometry()     // Flux surface geometry updates
   ```

5. **Free Boundary Solver** (NESTOR/BIEST methods)
   ```cpp
   // Plasma-vacuum interface calculations
   EvaluateMagneticField()  // External magnetic field evaluation
   ```

### Example Benchmark Implementation

```cpp
// File: src/vmecpp/cpp/vmecpp/common/fourier_basis_fast_poloidal/fourier_basis_benchmark.cc
#include <benchmark/benchmark.h>
#include "vmecpp/common/fourier_basis_fast_poloidal/fourier_basis_fast_poloidal.h"

static void BM_FourierBasisTransform(benchmark::State& state) {
  int mpol = state.range(0);
  int nzeta = state.range(1);
  
  // Setup test data
  FourierBasisFastPoloidal basis(mpol);
  std::vector<double> combined_coeffs(2 * mpol, 1.0);
  std::vector<double> product_coeffs(4 * mpol);
  
  for (auto _ : state) {
    basis.CombinedToProduct(combined_coeffs, product_coeffs);
    benchmark::DoNotOptimize(product_coeffs);
  }
  
  state.SetItemsProcessed(state.iterations() * 2 * mpol);
  state.SetBytesProcessed(state.iterations() * 2 * mpol * sizeof(double));
}

BENCHMARK(BM_FourierBasisTransform)
    ->Args({32, 64})
    ->Args({64, 128})
    ->Args({128, 256});
```

## Performance Measurement Patterns

### 1. Basic Timing

```cpp
#include <chrono>

auto start = std::chrono::high_resolution_clock::now();
// ... code to measure ...
auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
```

### 2. Google Benchmark Features

```cpp
// Measure memory allocations
state.counters["Memory"] = benchmark::Counter(
    memory_used, benchmark::Counter::kDefaults, benchmark::Counter::OneK::kIs1024);

// Set algorithmic complexity
state.SetComplexityN(input_size);

// Process rate metrics  
state.SetItemsProcessed(state.iterations() * items_per_iteration);
```

## CI/CD Integration

### Add to GitHub Actions

Create `.github/workflows/benchmarks.yml`:

```yaml
name: Benchmarks

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Bazel
      uses: bazelbuild/setup-bazelisk@v2
      
    - name: Run Benchmarks
      run: |
        bazel run //vmecpp/common/fourier_basis_fast_poloidal:fourier_basis_benchmark -- \
          --benchmark_format=json --benchmark_out=benchmark_results.json
          
    - name: Store Benchmark Results
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'googlecpp'
        output-file-path: benchmark_results.json
```

## Performance Testing Best Practices

### 1. Isolate Benchmark Environment
```bash
# Disable CPU frequency scaling
sudo cpupower frequency-set --governor performance

# Set CPU affinity
taskset -c 0-3 bazel run //path/to:benchmark
```

### 2. Multiple Iterations
```cpp
// Use sufficient iterations for stable measurements
BENCHMARK(BM_Function)->MinTime(2.0)->Repetitions(5);
```

### 3. Input Size Scaling
```cpp
// Test algorithmic complexity
BENCHMARK(BM_Function)
    ->RangeMultiplier(2)
    ->Range(8, 8192)
    ->Complexity(benchmark::oNLogN);
```

### 4. Memory Usage Tracking
```cpp
// Monitor memory allocations
benchmark::RegisterMemoryManager(benchmark::MemoryManager::Create());
```

## Next Steps for Complete Benchmark Suite

1. **Implement Core Benchmarks**: Add benchmark files for key computational functions
2. **Automated Regression Testing**: Integrate with CI/CD for performance regression detection
3. **Cross-Platform Validation**: Ensure consistent performance across different architectures
4. **Memory Profiling**: Add memory usage benchmarks alongside timing
5. **Parallel Performance**: Benchmark OpenMP and MPI scaling behavior

## Performance Optimization Targets

Based on VMEC++ computational architecture (from AGENTS.md):

### Core Performance Bottlenecks
- **Fourier transforms**: Most time-critical operations (fast transforms for spectral decomposition)
- **Force calculations**: Computationally intensive OpenMP-parallelized loops (Ideal MHD model)
- **Multigrid methods**: Iterative equilibrium solver performance
- **Geometry calculations**: Flux surface geometry and coordinate transformations
- **Basis conversions**: Product ↔ Combined Fourier basis transformations

### Memory and I/O Performance
- **NumPy ↔ Eigen conversion**: Python-C++ bridge efficiency
- **Matrix assembly**: Memory-bound operations with large sparse matrices
- **Hot restart**: Memory-efficient data sharing for parameter scans
- **Boundary condition evaluation**: I/O intensive operations

### Architecture-Specific Optimizations
- **SIMSOPT integration**: Optimization workflow performance
- **Free boundary methods**: NESTOR/BIEST computational efficiency
- **Multi-threading**: OpenMP scaling for force calculations
- **Convergence iterations**: Overall algorithm efficiency and zero-crash policy