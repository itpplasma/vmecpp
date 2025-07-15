#!/usr/bin/env python3
"""Quantitative validation of asymmetric VMEC++ using SIMSOPT interface."""

import numpy as np
from pathlib import Path
import netCDF4
import pytest
import vmecpp.simsopt_compat as simsopt_compat

TEST_DATA_DIR = Path("/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data")
EXAMPLES_DIR = Path("/home/ert/code/vmecpp/examples/data")


def test_heliotron_asym_quantitative():
    """Test HELIOTRON asymmetric against reference using SIMSOPT interface."""
    print("\n=== Testing HELIOTRON Asymmetric with SIMSOPT Interface ===")
    
    # Use SIMSOPT interface like the working tests
    input_file = EXAMPLES_DIR / "HELIOTRON_asym.json"
    reference_file = TEST_DATA_DIR / "wout_HELIOTRON_asym.nc"
    
    # Run using SIMSOPT interface
    vmec = simsopt_compat.Vmec(str(input_file))
    vmec.run()
    
    # Check convergence
    assert vmec.wout is not None, "VMEC++ did not produce output"
    assert vmec.wout.ier_flag == 0, f"VMEC++ did not converge (ier_flag={vmec.wout.ier_flag})"
    
    # Load reference
    with netCDF4.Dataset(reference_file, "r") as ref_wout:
        # Volume validation
        volume = vmec.volume()
        expected_volume = ref_wout.variables["volume_p"][()]
        print(f"\nVolume: {volume:.6f} (expected: {expected_volume:.6f})")
        np.testing.assert_allclose(volume, expected_volume, rtol=1e-10, atol=0.0)
        
        # Aspect ratio validation
        aspect = vmec.aspect()
        expected_aspect = ref_wout.variables["aspect"][()]
        print(f"Aspect: {aspect:.6f} (expected: {expected_aspect:.6f})")
        np.testing.assert_allclose(aspect, expected_aspect, rtol=1e-10, atol=0.0)
        
        # Iota profile validation
        expected_iotaf = ref_wout.variables["iotaf"][()]
        print(f"Iota range: [{vmec.wout.iotaf[0]:.4f}, {vmec.wout.iotaf[-1]:.4f}]")
        np.testing.assert_allclose(vmec.wout.iotaf, expected_iotaf, rtol=1e-10, atol=1e-12)
        
        # Check asymmetric arrays
        print("\nAsymmetric array validation:")
        for attr in ["rmns", "zmnc", "lmnc", "gmns", "bmns"]:
            if hasattr(vmec.wout, attr) and attr in ref_wout.variables:
                computed = getattr(vmec.wout, attr)
                expected = ref_wout.variables[attr][()]
                max_diff = np.max(np.abs(computed - expected))
                print(f"  {attr}: max diff = {max_diff:.2e}")
                np.testing.assert_allclose(computed, expected, rtol=1e-10, atol=1e-12)
    
    print("\n✓ HELIOTRON asymmetric quantitative validation PASSED!")
    return True


def test_tok_asym_quantitative():
    """Test tok_asym against reference using SIMSOPT interface."""
    print("\n=== Testing Tokamak Asymmetric with SIMSOPT Interface ===")
    
    # Use SIMSOPT interface
    input_file = EXAMPLES_DIR / "tok_asym.json"
    reference_file = TEST_DATA_DIR / "wout_tok_asym.nc"
    
    # Run using SIMSOPT interface
    vmec = simsopt_compat.Vmec(str(input_file))
    vmec.run()
    
    # Check convergence
    assert vmec.wout is not None, "VMEC++ did not produce output"
    assert vmec.wout.ier_flag == 0, f"VMEC++ did not converge (ier_flag={vmec.wout.ier_flag})"
    
    # Load reference
    with netCDF4.Dataset(reference_file, "r") as ref_wout:
        # Volume validation
        volume = vmec.volume()
        expected_volume = ref_wout.variables["volume_p"][()]
        print(f"\nVolume: {volume:.6f} (expected: {expected_volume:.6f})")
        np.testing.assert_allclose(volume, expected_volume, rtol=1e-10, atol=0.0)
        
        # Aspect ratio validation
        aspect = vmec.aspect()
        expected_aspect = ref_wout.variables["aspect"][()]
        print(f"Aspect: {aspect:.6f} (expected: {expected_aspect:.6f})")
        np.testing.assert_allclose(aspect, expected_aspect, rtol=1e-10, atol=0.0)
        
        # Iota profile validation (2D tokamak)
        expected_iotaf = ref_wout.variables["iotaf"][()]
        print(f"Iota range: [{vmec.wout.iotaf[0]:.4f}, {vmec.wout.iotaf[-1]:.4f}]")
        np.testing.assert_allclose(vmec.wout.iotaf, expected_iotaf, rtol=1e-10, atol=1e-12)
    
    print("\n✓ Tokamak asymmetric quantitative validation PASSED!")
    return True


def main():
    """Run all quantitative validation tests."""
    print("="*70)
    print("VMEC++ Asymmetric Quantitative Validation (SIMSOPT Interface)")
    print("="*70)
    
    # Test both cases
    try:
        test_heliotron_asym_quantitative()
    except Exception as e:
        print(f"\n✗ HELIOTRON test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_tok_asym_quantitative()
    except Exception as e:
        print(f"\n✗ Tokamak test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()