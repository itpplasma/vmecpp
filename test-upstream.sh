#!/bin/bash
# Test upstream vmecpp by cloning and running tests

set -e  # Exit on error

UPSTREAM_DIR="upstream-vmecpp-test"
UPSTREAM_REPO="https://github.com/itpplasma/vmecpp.git"

echo "Testing upstream vmecpp"
echo "======================"
echo ""

# Clean up any existing upstream directory
if [ -d "$UPSTREAM_DIR" ]; then
    echo "Removing existing $UPSTREAM_DIR directory..."
    rm -rf "$UPSTREAM_DIR"
fi

# Clone the upstream repository
echo "Cloning upstream repository..."
git clone "$UPSTREAM_REPO" "$UPSTREAM_DIR"

# Change to the cloned directory
cd "$UPSTREAM_DIR"

# Checkout main branch (should be default, but being explicit)
echo ""
echo "Checking out main branch..."
git checkout main

# Show the current commit for reference
echo ""
echo "Current upstream commit:"
git log --oneline -1

# Uninstall any existing vmecpp to ensure we test upstream
echo ""
echo "Uninstalling any existing vmecpp..."
pip uninstall -y vmecpp || echo "No existing vmecpp to uninstall"

# Run setup script
echo ""
echo "Running setup script..."
if [ -f "setup-vmecpp.sh" ]; then
    ./setup-vmecpp.sh
else
    echo "ERROR: setup-vmecpp.sh not found in upstream!"
    exit 1
fi

# Verify we're using the upstream version
echo ""
echo "Verifying vmecpp installation..."
python -c "import vmecpp; print(f'vmecpp location: {vmecpp.__file__}')"
echo ""

# Copy our pyright configuration to upstream to get consistent results
echo "Copying pyright configuration from local to upstream..."
if [ -f "../pyrightconfig.json" ]; then
    cp ../pyrightconfig.json .
    echo "Copied pyrightconfig.json to upstream"
fi
echo ""

# Run test script with debugging
echo ""
echo "Running test script..."
if [ -f "test-vmecpp.sh" ]; then
    # Run with explicit output to see where it might hang
    echo "Starting test script at $(date)"

    # Run the test script with unbuffered output
    stdbuf -o0 -e0 ./test-vmecpp.sh

    echo "Test script completed at $(date)"
else
    echo "ERROR: test-vmecpp.sh not found in upstream!"
    exit 1
fi

# Return to parent directory
cd ..

echo ""
echo "Upstream testing complete!"
echo ""
echo "Results are in $UPSTREAM_DIR/"
echo "To clean up, run: rm -rf $UPSTREAM_DIR"
