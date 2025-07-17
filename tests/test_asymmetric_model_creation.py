"""Step 1: Basic Asymmetric Model Creation Tests.

This module tests that VmecInput objects can be created successfully from
asymmetric input files with proper field validation and initialization.

Success Criteria:
- No validation errors during VmecInput creation
- All asymmetric fields are properly set with correct values
- Model validation passes for asymmetric configurations
"""

import numpy as np
import pytest

import vmecpp


def test_asymmetric_vmec_input_creation():
    """Test that VmecInput can be created from asymmetric tokamak input."""
    input_file = "examples/data/input.up_down_asymmetric_tokamak"

    # This should succeed without any validation errors
    vmec_input = vmecpp.VmecInput.from_file(input_file)

    # Verify it's recognized as asymmetric
    assert vmec_input.lasym is True

    # Verify basic parameters are set correctly
    assert vmec_input.nfp == 1
    assert vmec_input.mpol == 5
    assert vmec_input.ntor == 0

    # Verify asymmetric mode is properly enabled
    assert vmec_input.lasym is True


def test_asymmetric_fields_properly_initialized():
    """Test that all asymmetric fields are properly initialized."""
    input_file = "examples/data/input.up_down_asymmetric_tokamak"
    vmec_input = vmecpp.VmecInput.from_file(input_file)

    # All asymmetric arrays should be non-None for asymmetric runs
    assert vmec_input.rbs is not None
    assert vmec_input.zbc is not None
    assert vmec_input.raxis_s is not None
    assert vmec_input.zaxis_c is not None

    # Verify array types are correct
    assert isinstance(vmec_input.rbs, np.ndarray)
    assert isinstance(vmec_input.zbc, np.ndarray)
    assert isinstance(vmec_input.raxis_s, np.ndarray)
    assert isinstance(vmec_input.zaxis_c, np.ndarray)

    # Verify data types are floating point
    assert vmec_input.rbs.dtype == np.float64
    assert vmec_input.zbc.dtype == np.float64
    assert vmec_input.raxis_s.dtype == np.float64
    assert vmec_input.zaxis_c.dtype == np.float64


def test_asymmetric_boundary_coefficients():
    """Test that asymmetric boundary coefficients are set correctly."""
    input_file = "examples/data/input.up_down_asymmetric_tokamak"
    vmec_input = vmecpp.VmecInput.from_file(input_file)

    # Verify shapes match expected dimensions (mpol=5, ntor=0 → 2*ntor+1=1)
    expected_shape = (5, 1)
    assert vmec_input.rbs is not None
    assert vmec_input.zbc is not None
    assert vmec_input.rbs.shape == expected_shape
    assert vmec_input.zbc.shape == expected_shape

    # Verify key asymmetric coefficients from input file
    # RBS(0,1) = 0.6 → rbs[1, 0] = 0.6
    # RBS(0,2) = 0.12 → rbs[2, 0] = 0.12
    assert vmec_input.rbs[1, 0] == pytest.approx(0.6)
    assert vmec_input.rbs[2, 0] == pytest.approx(0.12)

    # Other RBS coefficients should be zero (initialized)
    assert vmec_input.rbs[0, 0] == pytest.approx(0.0)
    assert vmec_input.rbs[3, 0] == pytest.approx(0.0)
    assert vmec_input.rbs[4, 0] == pytest.approx(0.0)

    # ZBC coefficients should all be zero (not specified in input)
    assert np.all(vmec_input.zbc == 0.0)


def test_asymmetric_axis_coefficients():
    """Test that asymmetric axis coefficients are properly initialized."""
    input_file = "examples/data/input.up_down_asymmetric_tokamak"
    vmec_input = vmecpp.VmecInput.from_file(input_file)

    # Verify shapes for axis arrays (ntor=0 → ntor+1=1)
    expected_shape = (1,)
    assert vmec_input.raxis_s is not None
    assert vmec_input.zaxis_c is not None
    assert vmec_input.raxis_s.shape == expected_shape
    assert vmec_input.zaxis_c.shape == expected_shape

    # Axis coefficients should be zero (not specified in input, auto-initialized)
    assert vmec_input.raxis_s[0] == pytest.approx(0.0)
    assert vmec_input.zaxis_c[0] == pytest.approx(0.0)


def test_model_validation_passes():
    """Test that Pydantic model validation passes for asymmetric input."""
    input_file = "examples/data/input.up_down_asymmetric_tokamak"

    # This implicitly tests model validation - if validation fails,
    # from_file() would raise a ValidationError
    vmec_input = vmecpp.VmecInput.from_file(input_file)

    # Test that the model was created successfully
    assert vmec_input is not None
    assert isinstance(vmec_input, vmecpp.VmecInput)

    # Verify key fields are accessible and have expected values
    assert vmec_input.lasym is True
    assert vmec_input.mpol == 5
    assert vmec_input.ntor == 0
    assert vmec_input.nfp == 1

    # Note: Round-trip validation through model_dump() is skipped due to
    # known serialization issues with zero arrays being converted to empty lists


def test_asymmetric_vs_symmetric_field_differences():
    """Test differences between asymmetric and symmetric field requirements."""
    # Load asymmetric case
    asym_input = vmecpp.VmecInput.from_file(
        "examples/data/input.up_down_asymmetric_tokamak"
    )

    # Load a symmetric case for comparison
    sym_input = vmecpp.VmecInput.from_file("examples/data/solovev.json")

    # Asymmetric case should have lasym=True, symmetric should have lasym=False
    assert asym_input.lasym is True
    assert sym_input.lasym is False

    # Asymmetric case should have non-None asymmetric arrays
    assert asym_input.rbs is not None
    assert asym_input.zbc is not None
    assert asym_input.raxis_s is not None
    assert asym_input.zaxis_c is not None

    # Symmetric case should have None asymmetric arrays
    assert sym_input.rbs is None
    assert sym_input.zbc is None
    assert sym_input.raxis_s is None
    assert sym_input.zaxis_c is None

    # Both should have symmetric arrays
    assert asym_input.rbc is not None
    assert asym_input.zbs is not None
    assert sym_input.rbc is not None
    assert sym_input.zbs is not None


def test_asymmetric_field_access_and_manipulation():
    """Test that asymmetric fields can be accessed and manipulated correctly."""
    input_file = "examples/data/input.up_down_asymmetric_tokamak"
    vmec_input = vmecpp.VmecInput.from_file(input_file)

    # Test that we can access individual elements
    assert vmec_input.rbs is not None
    assert vmec_input.rbs[1, 0] == pytest.approx(0.6)
    assert vmec_input.rbs[2, 0] == pytest.approx(0.12)

    # Test that we can modify elements (for future programmatic use)
    original_value = vmec_input.rbs[1, 0]
    vmec_input.rbs[1, 0] = 0.7
    assert vmec_input.rbs[1, 0] == pytest.approx(0.7)

    # Restore original value
    vmec_input.rbs[1, 0] = original_value
    assert vmec_input.rbs[1, 0] == pytest.approx(0.6)

    # Test array operations work
    total_rbs = np.sum(vmec_input.rbs)
    expected_total = 0.6 + 0.12  # Only non-zero coefficients
    assert total_rbs == pytest.approx(expected_total)

    # Note: Full round-trip serialization tests are in separate module
    # due to known issues with zero array serialization
