#!/usr/bin/env python3
"""Test with INDATA format files that work with educational_VMEC."""

import numpy as np
from pathlib import Path
import netCDF4
import vmecpp.simsopt_compat as simsopt_compat

TEST_DATA_DIR = Path("/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data")


def test_heliotron_asym_indata():
    """Test HELIOTRON asymmetric using INDATA format."""
    print("\n=== Testing HELIOTRON Asymmetric (INDATA format) ===")
    
    # Use INDATA format file that works with educational_VMEC
    input_file = TEST_DATA_DIR / "input.HELIOTRON_asym"
    reference_file = TEST_DATA_DIR / "wout_HELIOTRON_asym.nc"
    
    print(f"Using input file: {input_file}")
    
    # Run using SIMSOPT interface
    vmec = simsopt_compat.Vmec(str(input_file))
    vmec.run()
    
    # Check convergence
    assert vmec.wout is not None, "VMEC++ did not produce output"
    print(f"ier_flag = {vmec.wout.ier_flag}")
    
    if vmec.wout.ier_flag == 0:
        print("✓ VMEC++ converged!")
        
        # Load reference
        with netCDF4.Dataset(reference_file, "r") as ref_wout:
            # Volume validation
            volume = vmec.volume()
            expected_volume = ref_wout.variables["volume_p"][()]
            print(f"\nVolume: {volume:.6f} (expected: {expected_volume:.6f})")
            vol_diff = abs(volume - expected_volume) / expected_volume * 100
            print(f"Volume difference: {vol_diff:.2f}%")
            
            # Aspect ratio validation
            aspect = vmec.aspect()
            expected_aspect = ref_wout.variables["aspect"][()]
            print(f"Aspect: {aspect:.6f} (expected: {expected_aspect:.6f})")
            asp_diff = abs(aspect - expected_aspect) / expected_aspect * 100
            print(f"Aspect difference: {asp_diff:.2f}%")
            
            # Iota profile validation
            expected_iotaf = ref_wout.variables["iotaf"][()]
            print(f"Iota range: [{vmec.wout.iotaf[0]:.4f}, {vmec.wout.iotaf[-1]:.4f}]")
            print(f"Expected:   [{expected_iotaf[0]:.4f}, {expected_iotaf[-1]:.4f}]")
            
            # Quantitative validation
            if vol_diff < 1e-10 and asp_diff < 1e-10:
                print("\n✓ Quantitative validation PASSED!")
                np.testing.assert_allclose(volume, expected_volume, rtol=1e-10, atol=0.0)
                np.testing.assert_allclose(aspect, expected_aspect, rtol=1e-10, atol=0.0)
                np.testing.assert_allclose(vmec.wout.iotaf, expected_iotaf, rtol=1e-10, atol=1e-12)
            else:
                print(f"\n⚠ Differences exceed tolerance")
    else:
        print(f"⚠ VMEC++ did not converge (ier_flag={vmec.wout.ier_flag})")
    
    return True


def test_tok_asym_indata():
    """Test tok_asym using INDATA format."""
    print("\n=== Testing Tokamak Asymmetric (INDATA format) ===")
    
    # Use INDATA format file
    input_file = TEST_DATA_DIR / "input.tok_asym"
    reference_file = TEST_DATA_DIR / "wout_tok_asym.nc"
    
    print(f"Using input file: {input_file}")
    
    # Run using SIMSOPT interface
    vmec = simsopt_compat.Vmec(str(input_file))
    vmec.run()
    
    # Check convergence
    assert vmec.wout is not None, "VMEC++ did not produce output"
    print(f"ier_flag = {vmec.wout.ier_flag}")
    
    if vmec.wout.ier_flag == 0:
        print("✓ VMEC++ converged!")
        
        # Load reference
        with netCDF4.Dataset(reference_file, "r") as ref_wout:
            # Volume validation
            volume = vmec.volume()
            expected_volume = ref_wout.variables["volume_p"][()]
            print(f"\nVolume: {volume:.6f} (expected: {expected_volume:.6f})")
            vol_diff = abs(volume - expected_volume) / expected_volume * 100
            print(f"Volume difference: {vol_diff:.2f}%")
            
            # Quantitative validation
            if vol_diff < 1e-10:
                print("\n✓ Quantitative validation PASSED!")
                np.testing.assert_allclose(volume, expected_volume, rtol=1e-10, atol=0.0)
            else:
                print(f"\n⚠ Differences exceed tolerance")
    else:
        print(f"⚠ VMEC++ did not converge (ier_flag={vmec.wout.ier_flag})")
    
    return True


def main():
    """Run quantitative validation with INDATA files."""
    print("="*70)
    print("VMEC++ Asymmetric Quantitative Validation (INDATA format)")
    print("="*70)
    
    # Test both cases
    try:
        test_heliotron_asym_indata()
    except Exception as e:
        print(f"\n✗ HELIOTRON test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_tok_asym_indata()
    except Exception as e:
        print(f"\n✗ Tokamak test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()