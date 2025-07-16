#!/bin/bash
# Test script for Python test failures bisect
# Tests exactly the 8 LOCAL-ONLY failing tests (excluding upstream VMEC2000 issue)
# Returns 0 if tests pass, 1 if tests fail, 125 if unable to test

set -e

echo "Testing Python failures at commit: $(git rev-parse --short HEAD)"

# Uninstall existing vmecpp to ensure clean state
echo "Uninstalling existing vmecpp..."
pip uninstall -y vmecpp > /dev/null 2>&1 || echo "No existing vmecpp to uninstall"

# Install current commit
echo "Installing vmecpp from current commit..."
if ! pip install -e . > /dev/null 2>&1; then
    echo "Failed to install vmecpp - skipping this commit"
    exit 125  # Special exit code for git bisect skip
fi

# Run the 8 LOCAL-ONLY failing tests (excluding upstream VMEC2000 issue)
echo "Running 8 local-only failing tests..."
FAILED_TESTS=(
    "tests/cpp/vmecpp/vmec/pybind11/test_pybind_vmec.py::test_output_quantities"
    "tests/test_init.py::test_vmecwout_io"
    "tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-str]"
    "tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-Path]"
    "tests/test_simsopt_compat.py::test_iota_axis[input.cma]"
    "tests/test_simsopt_compat.py::test_iota_edge[input.cma]"
    "tests/test_simsopt_compat.py::test_mean_iota[input.cma]"
    "tests/test_simsopt_compat.py::test_mean_shear[input.cma]"
)

# Run the tests with timeout to avoid hanging
if timeout 300 pytest "${FAILED_TESTS[@]}" -v --tb=no -q > /dev/null 2>&1; then
    echo "Tests PASSED"
    exit 0  # Good commit
else
    echo "Tests FAILED"
    exit 1  # Bad commit
fi
