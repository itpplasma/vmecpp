# VMECPP Testing Guide

This document describes how to run existing unit tests and add new test cases in VMECPP for both C++ and Python components.

## Testing Framework Overview

### C++ Testing
- **Framework**: Google Test (gtest) with Google Mock (gmock)
- **Build System**: Bazel with `cc_test` targets
- **Pattern**: `*_test.cc` files alongside source code
- **Dependencies**: `@googletest//:gtest_main`

### Python Testing  
- **Framework**: pytest with parametrized testing
- **Configuration**: `pyproject.toml` with `test = ["pytest"]` dependency
- **Pattern**: `test_*.py` files in `tests/` directory
- **Features**: Fixtures, parametrization, numerical comparisons

## Running Existing Tests

### Python Tests

#### Run All Python Tests
```bash
# From repository root
pytest

# With verbose output
pytest -v

# With test coverage
pytest --cov=vmecpp
```

#### Run Specific Test Files
```bash
# Run specific test file
pytest tests/test_init.py

# Run specific test function
pytest tests/test_init.py::test_run

# Run parametrized tests with specific parameters
pytest tests/test_simsopt_compat.py -k "cma"
```

#### Python Test Examples
```bash
# Test VMEC core functionality
pytest tests/test_init.py

# Test utility functions
pytest tests/test_util.py

# Test Simsopt compatibility
pytest tests/test_simsopt_compat.py

# Test free boundary functionality  
pytest tests/test_free_boundary.py

# Test pydantic integration
pytest tests/test_pydantic_numpy.py
```

### C++ Tests (Bazel)

#### Run All C++ Tests
```bash
# Run all tests in the project
bazel test //...

# Run all tests with verbose output
bazel test //... --test_output=all
```

#### Run Specific C++ Tests
```bash
# File I/O tests
bazel test //util/file_io:file_io_test

# VMEC core tests
bazel test //vmecpp/vmec/vmec:vmec_test

# Numerical comparison tests  
bazel test //util/testing:numerical_comparison_test

# Fourier basis tests
bazel test //vmecpp/common/fourier_basis_fast_poloidal:fourier_basis_fast_poloidal_test
```

#### Component-Specific Tests
```bash
# JSON I/O functionality
bazel test //util/json_io:json_io_test

# NetCDF I/O functionality  
bazel test //util/netcdf_io:netcdf_io_test

# Magnetic configuration tests
bazel test //vmecpp/common/magnetic_configuration_lib:magnetic_configuration_lib_test

# Surface geometry tests
bazel test //vmecpp/free_boundary/surface_geometry:surface_geometry_test
```

### Running Tests During Development

#### Install in Editable Mode and Test
```bash
# Install package in development mode
pip install -e .

# Run tests after installation
python -m pytest tests/
```

#### Quick Development Cycle
```bash
# Build and test specific component
bazel test //vmecpp/vmec/vmec:vmec_test --test_output=all

# Run Python tests with immediate feedback
pytest tests/test_init.py -v -s
```

## Test Data Organization

### C++ Test Data
**Location**: `src/vmecpp/cpp/vmecpp/test_data/`

**Organized by Test Case**:
```
test_data/
├── solovev.json              # Configuration file
├── input.solovev            # VMEC input file  
├── wout_solovev.nc          # Reference output
├── cma.json                 # CTH-like configuration
├── input.cma               # CTH input file
└── wout_cma.nc             # CTH reference output
```

**Bazel Filegroups**:
```bazel
filegroup(
    name = "solovev",
    visibility = ["//visibility:public"], 
    srcs = [
        "solovev.json",
        "input.solovev", 
        "wout_solovev.nc",
    ],
)
```

### Python Test Data Access
```python
# Standard pattern for accessing test data
REPO_ROOT = Path(__file__).parent.parent.parent
TEST_DATA_PATH = REPO_ROOT / "src" / "vmecpp" / "cpp" / "vmecpp" / "test_data"

def load_test_case(name: str):
    return TEST_DATA_PATH / f"{name}.json"
```

## Adding New Unit Tests

### Adding C++ Unit Tests

#### Step 1: Create Test File
Create `src/vmecpp/cpp/[path]/[component]_test.cc`:

```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "[component].h"

// Basic test structure
TEST(ComponentTest, BasicFunctionality) {
  // Arrange
  auto component = CreateComponent();
  
  // Act  
  auto result = component.DoSomething();
  
  // Assert
  EXPECT_EQ(result.size(), 10);
  EXPECT_DOUBLE_EQ(result[0], 1.0);
}

// Parametrized test example
class ComponentParametrizedTest : public ::testing::TestWithParam<int> {};

TEST_P(ComponentParametrizedTest, ParametrizedFunctionality) {
  int param = GetParam();
  auto result = ProcessWithParameter(param);
  EXPECT_GT(result, 0);
}

INSTANTIATE_TEST_SUITE_P(
  ComponentTests,
  ComponentParametrizedTest, 
  ::testing::Values(1, 5, 10, 100)
);

// Custom matcher example using gmock
MATCHER_P(IsCloseToVector, expected, "") {
  if (arg.size() != expected.size()) return false;
  for (size_t i = 0; i < arg.size(); ++i) {
    if (std::abs(arg[i] - expected[i]) > 1e-10) return false;
  }
  return true;
}

TEST(ComponentTest, VectorComparison) {
  std::vector<double> expected = {1.0, 2.0, 3.0};
  auto result = ComputeVector();
  EXPECT_THAT(result, IsCloseToVector(expected));
}
```

#### Step 2: Add Bazel BUILD Target
Add to `BUILD.bazel` in the same directory:

```bazel
cc_test(
    name = "component_test",
    srcs = ["component_test.cc"],
    deps = [
        ":component",           # The component being tested
        "@googletest//:gtest_main",
        "@googletest//:gmock",
    ],
    data = [
        "//vmecpp/test_data:test_files",  # Test data dependencies
    ],
    size = "small",  # small, medium, large, enormous
    timeout = "short",  # short, moderate, long, eternal
)
```

#### Step 3: Using Custom Testing Utilities
```cpp
#include "util/testing/numerical_comparison_lib.h"

TEST(ComponentTest, NumericalComparison) {
  std::vector<double> computed = {1.0, 2.0, 3.0};
  std::vector<double> expected = {1.000001, 1.999999, 3.000001};
  
  // Use custom comparison with relative/absolute tolerance
  EXPECT_TRUE(IsCloseRelAbs(computed, expected, 1e-5, 1e-12));
}
```

### Adding Python Unit Tests

#### Step 1: Create Test File
Create `tests/test_[component].py`:

```python
import pytest
import numpy as np
import tempfile
from pathlib import Path

import vmecpp

# Module-level fixture
@pytest.fixture(scope="module")
def test_data_path():
    """Path to test data directory."""
    repo_root = Path(__file__).parent.parent
    return repo_root / "src" / "vmecpp" / "cpp" / "vmecpp" / "test_data"

@pytest.fixture
def sample_input(test_data_path):
    """Load a sample VMEC input configuration."""
    input_file = test_data_path / "solovev.json"
    return vmecpp.VmecInput.model_validate_json(input_file.read_text())

# Basic test
def test_component_basic_functionality():
    """Test basic component functionality."""
    component = vmecpp.SomeComponent()
    result = component.process()
    assert result is not None
    assert len(result) > 0

# Parametrized test
@pytest.mark.parametrize(
    "input_file,expected_nfp", 
    [
        ("solovev.json", 1),
        ("cma.json", 4),
        ("w7x.json", 5),
    ]
)
def test_configuration_loading(test_data_path, input_file, expected_nfp):
    """Test loading different configuration files."""
    config_path = test_data_path / input_file
    vmec_input = vmecpp.VmecInput.model_validate_json(config_path.read_text())
    assert vmec_input.nfp == expected_nfp

# Numerical comparison test
def test_numerical_output(sample_input):
    """Test numerical output accuracy."""
    result = vmecpp.run(sample_input)
    
    # Compare against reference values
    np.testing.assert_allclose(
        result.some_quantity,
        reference_values,
        rtol=1e-10, 
        atol=1e-12
    )

# File I/O test with temporary files
def test_file_output():
    """Test file output functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.nc"
        
        # Generate output
        result = vmecpp.run(sample_configuration)
        result.write_netcdf(output_path)
        
        # Verify file exists and contains expected data
        assert output_path.exists()
        
        # Load and verify
        reloaded = vmecpp.load_output(output_path)
        assert reloaded.converged

# Exception testing
def test_invalid_input_raises_error():
    """Test that invalid input raises appropriate errors."""
    invalid_input = vmecpp.VmecInput()
    invalid_input.nfp = -1  # Invalid value
    
    with pytest.raises(ValueError, match="nfp must be positive"):
        vmecpp.run(invalid_input)

# Property-based testing with hypothesis (optional)
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=10))
def test_property_based_nfp(nfp_value):
    """Property-based test for nfp parameter."""
    vmec_input = vmecpp.VmecInput()
    vmec_input.nfp = nfp_value
    
    # Property: nfp should always be preserved
    assert vmec_input.nfp == nfp_value
```

#### Step 2: Test Configuration
Ensure `pyproject.toml` includes test dependencies:

```toml
[project.optional-dependencies]
test = [
    "pytest", 
    "pytest-cov",
    "hypothesis",  # Optional: for property-based testing
]
```

## Test Patterns and Best Practices

### C++ Testing Best Practices

#### 1. Test Organization
```cpp
// Group related tests in test classes
class FourierBasisTest : public ::testing::Test {
protected:
  void SetUp() override {
    // Common setup
    basis_ = std::make_unique<FourierBasisFastPoloidal>(mpol_);
  }
  
  int mpol_ = 64;
  std::unique_ptr<FourierBasisFastPoloidal> basis_;
};

TEST_F(FourierBasisTest, CombinedToProduct) {
  // Test using fixture
}
```

#### 2. Numerical Testing
```cpp
// Use appropriate tolerances for floating-point comparisons
EXPECT_NEAR(computed_value, expected_value, 1e-10);

// Vector comparisons with custom tolerance
EXPECT_TRUE(IsCloseRelAbs(computed_vector, expected_vector, 1e-8, 1e-15));
```

#### 3. Resource Management
```cpp
TEST(ResourceTest, ProperCleanup) {
  auto resource = std::make_unique<Resource>();
  // Test automatically cleans up via RAII
}
```

### Python Testing Best Practices

#### 1. Fixture Reuse
```python
@pytest.fixture(scope="session")
def expensive_setup():
    """Setup that's expensive and can be reused."""
    return create_expensive_resource()

@pytest.fixture
def fresh_data():
    """Setup that needs to be fresh for each test."""
    return create_test_data()
```

#### 2. Error Testing
```python
def test_error_conditions():
    """Test all error paths."""
    with pytest.raises(ValueError):
        invalid_operation()
    
    with pytest.raises(FileNotFoundError):
        load_nonexistent_file()
```

#### 3. Numerical Accuracy
```python
def test_numerical_accuracy():
    """Test numerical computations."""
    computed = expensive_calculation()
    expected = reference_result()
    
    # Use appropriate tolerances
    np.testing.assert_allclose(computed, expected, rtol=1e-12, atol=1e-15)
```

## Integration with CI/CD

### GitHub Actions Integration
Tests are automatically run in CI/CD. The workflow typically includes:

```yaml
# Excerpt from .github/workflows/test.yml
- name: Run Python Tests
  run: |
    pip install -e .[test]
    pytest tests/ --cov=vmecpp --cov-report=xml

- name: Run C++ Tests  
  run: |
    bazel test //... --test_output=errors
```

## Debugging Test Failures

### C++ Test Debugging
```bash
# Run single test with detailed output
bazel test //path/to:test_target --test_output=all --test_arg=--gtest_filter="TestName.TestCase"

# Debug with GDB
bazel test //path/to:test_target --run_under="gdb --args"
```

### Python Test Debugging
```bash
# Run with debugging output
pytest tests/test_file.py -v -s --tb=long

# Drop into debugger on failure
pytest tests/test_file.py --pdb

# Run specific test with print statements
pytest tests/test_file.py::test_function -s
```

## Test Coverage Analysis

### Python Coverage
```bash
# Generate coverage report
pytest --cov=vmecpp --cov-report=html

# View coverage report
open htmlcov/index.html
```

### C++ Coverage (with gcov)
```bash
# Build with coverage flags
bazel test //... --collect_code_coverage

# Generate coverage report
genhtml bazel-out/_coverage/_coverage_report.dat -o coverage_html
```

## Custom Testing Utilities

### Numerical Comparison Library
**Location**: `src/vmecpp/cpp/util/testing/numerical_comparison_lib.h`

```cpp
// Custom tolerance-based comparison
bool IsCloseRelAbs(const std::vector<double>& a, 
                   const std::vector<double>& b,
                   double rtol, double atol);

// Handles NaN values appropriately  
bool IsCloseOrBothNaN(double a, double b, double tol);
```

### Test Data Management
```cpp
// Load test data from Bazel data dependencies
std::string LoadTestFile(const std::string& filename) {
  std::string test_data_dir = "vmecpp/test_data";
  return LoadFileContent(test_data_dir + "/" + filename);
}
```

This comprehensive testing framework ensures code quality and helps prevent regressions as VMECPP continues to evolve.