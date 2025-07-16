#!/bin/bash
# Test script for bisect - checks if C++ test passes
# Returns 0 if test passes, 1 if test fails

set -e

cd src/vmecpp/cpp

# Try to build and run the test
if ! bazel build --config=opt -- //vmecpp/vmec/output_quantities:output_quantities_test 2>/dev/null; then
    echo "Build failed - skipping this commit"
    exit 125  # Special exit code for git bisect skip
fi

if bazel test --config=opt --test_output=errors -- //vmecpp/vmec/output_quantities:output_quantities_test 2>/dev/null; then
    echo "Test passed"
    exit 0  # Good commit
else
    echo "Test failed"
    exit 1  # Bad commit
fi
