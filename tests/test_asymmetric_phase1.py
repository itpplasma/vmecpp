"""
Phase 1 asymmetric tests: Validate symmetric cases with lasym=true.

This module tests that symmetric equilibria produce identical results
when run with lasym=true and zero asymmetric coefficients.
"""

import numpy as np
import pytest

import vmecpp


def run_symmetric_as_asymmetric(input_file: str) -> vmecpp.VmecOutput:
    """Run a symmetric input file with lasym=true and zero asymmetric coefficients.

    Args:
        input_file: Path to symmetric input file (JSON format)

    Returns:
        VmecOutput from asymmetric run
    """
    # Load symmetric input
    input_obj = vmecpp.VmecInput.from_file(input_file)

    # Create dictionary with all current fields
    input_dict = input_obj.model_dump()

    # Enable asymmetric mode
    input_dict["lasym"] = True

    # Set all asymmetric coefficients to zero
    # Boundary coefficients - same shape as symmetric counterparts
    input_dict["rbs"] = np.zeros_like(input_obj.rbc)
    input_dict["zbc"] = np.zeros_like(input_obj.zbs)

    # Asymmetric axis arrays
    input_dict["raxis_s"] = np.zeros(input_obj.ntor + 1)
    input_dict["zaxis_c"] = np.zeros(input_obj.ntor + 1)

    # Create new VmecInput object with asymmetric fields
    # This should trigger the model validators properly
    asym_input = vmecpp.VmecInput(**input_dict)

    # Run VMEC++
    output = vmecpp.run(asym_input)

    return output


def compare_symmetric_asymmetric_outputs(
    sym_output: vmecpp.VmecOutput,
    asym_output: vmecpp.VmecOutput,
    rtol: float = 1e-14,
    atol: float = 1e-14,
) -> None:
    """Compare symmetric and asymmetric outputs for identical results.

    Args:
        sym_output: Output from symmetric run (lasym=false)
        asym_output: Output from asymmetric run (lasym=true, zero asymmetric coeffs)
        rtol: Relative tolerance for comparison
        atol: Absolute tolerance for comparison
    """
    # Get wout objects for comparison
    sym_wout = sym_output.wout
    asym_wout = asym_output.wout

    # Check basic convergence properties
    assert sym_wout.ier_flag == asym_wout.ier_flag, "Different convergence flags"

    # Compare symmetric Fourier coefficients
    np.testing.assert_allclose(
        sym_wout.rmnc,
        asym_wout.rmnc,
        rtol=rtol,
        atol=atol,
        err_msg="rmnc arrays differ",
    )
    np.testing.assert_allclose(
        sym_wout.zmns,
        asym_wout.zmns,
        rtol=rtol,
        atol=atol,
        err_msg="zmns arrays differ",
    )

    # Compare other key quantities
    key_scalars = [
        "fsqr",
        "fsqz",
        "fsql",
        "volume",
        "aspect",
        "betatot",
        "betapol",
        "betator",
        "rbtor",
        "ctor",
        "Aminor_p",
        "Rmajor_p",
    ]

    for scalar in key_scalars:
        if hasattr(sym_wout, scalar) and hasattr(asym_wout, scalar):
            sym_val = getattr(sym_wout, scalar)
            asym_val = getattr(asym_wout, scalar)
            np.testing.assert_allclose(
                sym_val,
                asym_val,
                rtol=rtol,
                atol=atol,
                err_msg=f"{scalar} values differ",
            )

    # Compare profile arrays
    profile_arrays = [
        "iotaf",
        "presf",
        "phi",
        "chi",
        "mass",
        "pres",
        "beta_vol",
        "phip",
        "buco",
        "bvco",
        "vp",
        "overr",
        "specw",
        "jcuru",
        "jcurv",
    ]

    for array_name in profile_arrays:
        if hasattr(sym_wout, array_name) and hasattr(asym_wout, array_name):
            sym_arr = getattr(sym_wout, array_name)
            asym_arr = getattr(asym_wout, array_name)
            if sym_arr is not None and asym_arr is not None:
                np.testing.assert_allclose(
                    sym_arr,
                    asym_arr,
                    rtol=rtol,
                    atol=atol,
                    err_msg=f"{array_name} arrays differ",
                )

    # Check that asymmetric arrays are zero (if they exist)
    if hasattr(asym_wout, "rmns") and asym_wout.rmns is not None:
        np.testing.assert_allclose(
            asym_wout.rmns,
            0.0,
            rtol=rtol,
            atol=atol,
            err_msg="rmns should be zero for symmetric case",
        )

    if hasattr(asym_wout, "zmnc") and asym_wout.zmnc is not None:
        np.testing.assert_allclose(
            asym_wout.zmnc,
            0.0,
            rtol=rtol,
            atol=atol,
            err_msg="zmnc should be zero for symmetric case",
        )


class TestSymmetricWithLasymTrue:
    """Test that symmetric cases give identical results with lasym=true."""

    def test_solovev_symmetric_vs_asymmetric(self):
        """Test solovev.json with lasym=true gives identical results."""
        input_file = "examples/data/solovev.json"

        # Run symmetric case
        sym_input = vmecpp.VmecInput.from_file(input_file)
        sym_output = vmecpp.run(sym_input)

        # Run asymmetric case with zero asymmetric coefficients
        asym_output = run_symmetric_as_asymmetric(input_file)

        # Compare outputs
        compare_symmetric_asymmetric_outputs(sym_output, asym_output)

    def test_circular_tokamak_symmetric_vs_asymmetric(self):
        """Test circular_tokamak.json with lasym=true gives identical results."""
        input_file = "examples/data/circular_tokamak.json"

        # Run symmetric case
        sym_input = vmecpp.VmecInput.from_file(input_file)
        sym_output = vmecpp.run(sym_input)

        # Run asymmetric case with zero asymmetric coefficients
        asym_output = run_symmetric_as_asymmetric(input_file)

        # Compare outputs
        compare_symmetric_asymmetric_outputs(sym_output, asym_output)

    def test_cma_symmetric_vs_asymmetric(self):
        """Test cma.json with lasym=true gives identical results."""
        input_file = "examples/data/cma.json"

        # Run symmetric case
        sym_input = vmecpp.VmecInput.from_file(input_file)
        sym_output = vmecpp.run(sym_input)

        # Run asymmetric case with zero asymmetric coefficients
        asym_output = run_symmetric_as_asymmetric(input_file)

        # Compare outputs
        compare_symmetric_asymmetric_outputs(sym_output, asym_output)

    @pytest.mark.parametrize(
        "input_file",
        [
            "examples/data/solovev.json",
            "examples/data/circular_tokamak.json",
            "examples/data/cma.json",
        ],
    )
    def test_all_symmetric_cases_with_lasym_true(self, input_file):
        """Parameterized test for all symmetric cases with lasym=true."""
        # Run symmetric case
        sym_input = vmecpp.VmecInput.from_file(input_file)
        sym_output = vmecpp.run(sym_input)

        # Run asymmetric case with zero asymmetric coefficients
        asym_output = run_symmetric_as_asymmetric(input_file)

        # Compare outputs
        compare_symmetric_asymmetric_outputs(sym_output, asym_output)

    def test_asymmetric_mode_flags(self):
        """Test that asymmetric mode flags are set correctly."""
        input_file = "examples/data/solovev.json"

        # Run asymmetric case
        asym_output = run_symmetric_as_asymmetric(input_file)

        # Check that lasym flag is set
        assert asym_output.wout.lasym, "lasym flag should be True"

        # Check that basic convergence is achieved
        assert asym_output.wout.ier_flag == 0, "Should converge successfully"
        assert asym_output.wout.fsqr < 1e-6, "Should achieve good force balance"

    def test_asymmetric_cpp_initialization(self):
        """Test that asymmetric arrays are properly initialized in C++ wrapper."""
        # Load symmetric input
        input_obj = vmecpp.VmecInput.from_file("examples/data/solovev.json")

        # Create asymmetric input
        input_dict = input_obj.model_dump()
        input_dict["lasym"] = True
        input_dict["rbs"] = np.zeros_like(input_obj.rbc)
        input_dict["zbc"] = np.zeros_like(input_obj.zbs)
        input_dict["raxis_s"] = np.zeros(input_obj.ntor + 1)
        input_dict["zaxis_c"] = np.zeros(input_obj.ntor + 1)

        asym_input = vmecpp.VmecInput(**input_dict)

        # Convert to C++ object and verify arrays are initialized
        cpp_indata = asym_input._to_cpp_vmecindatapywrapper()

        assert cpp_indata.lasym is True
        assert cpp_indata.raxis_s is not None, "raxis_s should be initialized"
        assert cpp_indata.zaxis_c is not None, "zaxis_c should be initialized"
        assert cpp_indata.rbs is not None, "rbs should be initialized"
        assert cpp_indata.zbc is not None, "zbc should be initialized"
