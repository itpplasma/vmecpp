#!/usr/bin/env python3
"""Test symmetric cases to verify the setup works."""

import numpy as np
from pathlib import Path
import netCDF4
import vmecpp.simsopt_compat as simsopt_compat

TEST_DATA_DIR = Path("/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data")


def test_solovev_symmetric():
    """Test solovev symmetric case (known to work)."""
    print("\n=== Testing Solovev Symmetric ===")
    
    # Use SIMSOPT interface
    input_file = TEST_DATA_DIR / "solovev.json"
    reference_file = TEST_DATA_DIR / "wout_solovev.nc"
    
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
        np.testing.assert_allclose(volume, expected_volume, rtol=1e-11, atol=0.0)
        
        # Aspect ratio validation
        aspect = vmec.aspect()
        expected_aspect = ref_wout.variables["aspect"][()]
        print(f"Aspect: {aspect:.6f} (expected: {expected_aspect:.6f})")
        np.testing.assert_allclose(aspect, expected_aspect, rtol=1e-11, atol=0.0)
    
    print("\n✓ Solovev symmetric quantitative validation PASSED!")
    return True


def test_cma_symmetric():
    """Test CMA symmetric case (known to work)."""
    print("\n=== Testing CMA Symmetric ===")
    
    # Use SIMSOPT interface
    input_file = TEST_DATA_DIR / "cma.json"
    reference_file = TEST_DATA_DIR / "wout_cma.nc"
    
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
        np.testing.assert_allclose(volume, expected_volume, rtol=1e-11, atol=0.0)
        
        # Aspect ratio validation
        aspect = vmec.aspect()
        expected_aspect = ref_wout.variables["aspect"][()]
        print(f"Aspect: {aspect:.6f} (expected: {expected_aspect:.6f})")
        np.testing.assert_allclose(aspect, expected_aspect, rtol=1e-11, atol=0.0)
    
    print("\n✓ CMA symmetric quantitative validation PASSED!")
    return True


def main():
    """Run symmetric tests to verify setup."""
    print("="*70)
    print("VMEC++ Symmetric Baseline Tests")
    print("="*70)
    
    try:
        test_solovev_symmetric()
    except Exception as e:
        print(f"\n✗ Solovev test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_cma_symmetric()
    except Exception as e:
        print(f"\n✗ CMA test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()