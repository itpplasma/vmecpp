#!/bin/bash
# Setup script for vmecpp - installs dependencies and builds the package

set -e  # Exit on error

echo "Setting up vmecpp"
echo "================="
echo ""

# Install Bazel 7.4.1 if not present or wrong version
echo "Checking Bazel installation..."
if ! command -v bazel &> /dev/null || [[ "$(bazel --version 2>/dev/null | grep -oP 'bazel \K[0-9]+\.[0-9]+\.[0-9]+')" != "7.4.1" ]]; then
    echo "Installing Bazel 7.4.1..."
    # Download Bazelisk which manages Bazel versions
    mkdir -p ~/.local/bin
    curl -L https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 -o ~/.local/bin/bazel
    chmod +x ~/.local/bin/bazel

    # Set specific Bazel version
    export USE_BAZEL_VERSION=7.4.1

    # Verify installation
    ~/.local/bin/bazel --version
    echo "Bazel 7.4.1 installed to ~/.local/bin/bazel"
    echo "Make sure ~/.local/bin is in your PATH"
else
    echo "Bazel 7.4.1 is already installed"
fi

# Clean previous build artifacts
echo ""
echo "Cleaning previous build artifacts..."
rm -rf build/ dist/ *.egg-info

# Install vmecpp with test dependencies
echo "Installing vmecpp in editable mode with test dependencies..."
pip install -e ".[test]"

# Install pre-commit hooks
echo ""
echo "Installing pre-commit hooks..."
pre-commit install

# Run pre-commit to ensure all hooks are set up
echo ""
echo "Running initial pre-commit setup..."
pre-commit run --all-files || echo "Note: Some pre-commit hooks may have auto-fixed files. This is normal on first run."

echo ""
echo "Setup complete!"
echo ""
echo "Summary:"
echo "- Bazel 7.4.1 installed/verified"
echo "- vmecpp installed in editable mode"
echo "- Test dependencies installed"
echo "- Pre-commit hooks installed"
echo ""
echo "You can now run ./test-vmecpp.sh to run all tests"
