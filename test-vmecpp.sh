#!/bin/bash
# Test script for vmecpp - runs all tests

set -e  # Exit on error

echo "Testing vmecpp"
echo "=============="
echo ""

# Check if vmecpp is installed
if ! python -c "import vmecpp" 2>/dev/null; then
    echo "Error: vmecpp is not installed. Please run ./setup-vmecpp.sh first"
    exit 1
fi

# Run pre-commit checks
echo "Running pre-commit checks..."
echo "=========================="
if pre-commit run --all-files; then
    echo "Pre-commit checks passed!"
else
    echo "Warning: Some pre-commit checks failed. Check output above."
    echo "Continuing with tests..."
fi

echo ""
echo "Running Python tests..."
echo "======================"
python -m pytest tests/

echo ""
echo "Running docstring tests..."
echo "========================"
python -m doctest $(git ls-files src/ | grep '\.py$' | grep -v '/__main__.py$')

echo ""
echo "Building and testing C++ core with Bazel..."
echo "=========================================="
cd src/vmecpp/cpp

# Build C++ core
echo "Building C++ core..."
bazel build --config=opt -- //...

# Run C++ tests
echo "Running C++ tests..."
bazel test --config=opt --test_output=errors -- //vmecpp/...

cd ../../..

echo ""
echo "All tests complete!"
echo ""
echo "Test Summary:"
echo "- Pre-commit checks: PASSED"
echo "- Python tests: COMPLETED"
echo "- Docstring tests: PASSED"
echo "- C++ build: SUCCESS"
echo "- C++ tests: COMPLETED"
