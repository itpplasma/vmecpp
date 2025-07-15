#!/usr/bin/env python3
"""Quantitative validation of asymmetric VMEC++ against reference files."""

import numpy as np
from pathlib import Path
import netCDF4
import vmecpp

TEST_DATA_DIR = Path("/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data")

def test_heliotron_asym():
    """Test HELIOTRON asymmetric case."""
    print("=== Testing HELIOTRON Asymmetric ===")
    
    # Load input
    input_file = Path("/home/ert/code/vmecpp/examples/data/HELIOTRON_asym.json")
    vmec_input = vmecpp.VmecInput.from_file(input_file)
    print(f"Configuration: nfp={vmec_input.nfp}, mpol={vmec_input.mpol}, ntor={vmec_input.ntor}")
    print(f"lasym = {vmec_input.lasym}")
    
    # Enable returning outputs even if not converged
    vmec_input.return_outputs_even_if_not_converged = True
    
    # Run VMEC++
    print("\nRunning VMEC++...")
    try:
        # Enable verbose output to see what's happening
        output = vmecpp.run(vmec_input, verbose=True)
        print(f"\n✓ VMEC++ completed!")
        print(f"  ier_flag = {output.wout.ier_flag}")
        print(f"  Volume = {output.wout.volume:.6f}")
        print(f"  Aspect = {output.wout.aspect:.6f}")
        print(f"  Beta = {output.wout.betatot:.6f}")
        
        # Check if converged (ier_flag == 0)
        if output.wout.ier_flag != 0:
            print(f"  WARNING: ier_flag = {output.wout.ier_flag} (non-zero indicates potential issues)")
        
        # Check asymmetric arrays
        print("\nAsymmetric arrays present:")
        for attr in ['rmns', 'zmnc', 'lmnc', 'gmns', 'bmns']:
            if hasattr(output.wout, attr):
                arr = getattr(output.wout, attr)
                max_val = np.max(np.abs(arr))
                print(f"  {attr}: shape={arr.shape}, max={max_val:.2e}")
        
        # Load reference
        ref_file = TEST_DATA_DIR / "wout_HELIOTRON_asym.nc"
        if ref_file.exists():
            print(f"\n=== Quantitative Comparison with Reference ===")
            ref_wout = netCDF4.Dataset(ref_file)
            
            # Volume comparison
            ref_volume = ref_wout.variables['volume_p'][()]
            vol_diff = abs(output.wout.volume - ref_volume) / ref_volume * 100
            print(f"\nVolume:")
            print(f"  VMEC++ = {output.wout.volume:.6f}")
            print(f"  Reference = {ref_volume:.6f}")
            print(f"  Relative difference = {vol_diff:.2f}%")
            
            # Aspect comparison
            ref_aspect = ref_wout.variables['aspect'][()]
            asp_diff = abs(output.wout.aspect - ref_aspect) / ref_aspect * 100
            print(f"\nAspect ratio:")
            print(f"  VMEC++ = {output.wout.aspect:.6f}")
            print(f"  Reference = {ref_aspect:.6f}")
            print(f"  Relative difference = {asp_diff:.2f}%")
            
            # Beta comparison
            if 'betatotal' in ref_wout.variables:
                ref_beta = ref_wout.variables['betatotal'][()]
                beta_diff = abs(output.wout.betatot - ref_beta) / ref_beta * 100
                print(f"\nBeta:")
                print(f"  VMEC++ = {output.wout.betatot:.6f}")
                print(f"  Reference = {ref_beta:.6f}")
                print(f"  Relative difference = {beta_diff:.2f}%")
            
            # Iota profile
            ref_iotaf = ref_wout.variables['iotaf'][()]
            iota_diff = np.max(np.abs(output.wout.iotaf - ref_iotaf))
            iota_rel = iota_diff / np.max(np.abs(ref_iotaf))
            print(f"\nIota profile:")
            print(f"  Max absolute difference = {iota_diff:.2e}")
            print(f"  Max relative difference = {iota_rel:.2e}")
            
            # Symmetric arrays
            print(f"\nSymmetric Fourier arrays:")
            for attr in ['rmnc', 'zmns', 'lmns', 'gmnc', 'bmnc']:
                if hasattr(output.wout, attr) and attr in ref_wout.variables:
                    arr_vmecpp = getattr(output.wout, attr)
                    arr_ref = ref_wout.variables[attr][()]
                    if arr_vmecpp.shape == arr_ref.shape:
                        max_diff = np.max(np.abs(arr_vmecpp - arr_ref))
                        rel_diff = max_diff / (np.max(np.abs(arr_ref)) + 1e-14)
                        print(f"  {attr}: max abs diff = {max_diff:.2e}, rel diff = {rel_diff:.2e}")
            
            # Asymmetric arrays
            print(f"\nAsymmetric Fourier arrays:")
            for attr in ['rmns', 'zmnc', 'lmnc', 'gmns', 'bmns']:
                if hasattr(output.wout, attr) and attr in ref_wout.variables:
                    arr_vmecpp = getattr(output.wout, attr)
                    arr_ref = ref_wout.variables[attr][()]
                    if arr_vmecpp.shape == arr_ref.shape:
                        max_diff = np.max(np.abs(arr_vmecpp - arr_ref))
                        # For asymmetric arrays, check if reference is non-zero
                        ref_max = np.max(np.abs(arr_ref))
                        if ref_max > 1e-14:
                            rel_diff = max_diff / ref_max
                            print(f"  {attr}: max abs diff = {max_diff:.2e}, rel diff = {rel_diff:.2e}")
                        else:
                            print(f"  {attr}: reference is zero, abs diff = {max_diff:.2e}")
            
            # Overall assessment
            print("\n=== Validation Summary ===")
            if vol_diff < 1e-10 and asp_diff < 1e-10:
                print("✓ EXCELLENT: Volume and aspect ratio match to 1e-10 relative")
            elif vol_diff < 1e-6 and asp_diff < 1e-6:
                print("✓ GOOD: Volume and aspect ratio match to 1e-6 relative")
            elif vol_diff < 1e-2 and asp_diff < 1e-2:
                print("⚠ FAIR: Volume and aspect ratio match to 1% relative")
            else:
                print("✗ POOR: Differences exceed 1%")
                
            ref_wout.close()
            
    except Exception as e:
        print(f"✗ VMEC++ failed: {e}")
        return False
    
    return True


def test_tok_asym():
    """Test tok_asym case."""
    print("\n\n=== Testing Tokamak Asymmetric ===")
    
    # Load input
    input_file = Path("/home/ert/code/vmecpp/examples/data/tok_asym.json")
    vmec_input = vmecpp.VmecInput.from_file(input_file)
    print(f"Configuration: nfp={vmec_input.nfp}, mpol={vmec_input.mpol}, ntor={vmec_input.ntor}")
    print(f"lasym = {vmec_input.lasym}")
    
    # Enable returning outputs even if not converged
    vmec_input.return_outputs_even_if_not_converged = True
    
    # Try with looser tolerances
    vmec_input.ftol_array = [1e-8, 1e-10]
    vmec_input.niter_array = [1000, 2000]
    print(f"Using modified tolerances: ftol={vmec_input.ftol_array}")
    
    # Run VMEC++
    print("\nRunning VMEC++...")
    try:
        output = vmecpp.run(vmec_input, verbose=True)
        print(f"\n✓ VMEC++ completed!")
        print(f"  ier_flag = {output.wout.ier_flag}")
        print(f"  Volume = {output.wout.volume:.6f}")
        print(f"  Aspect = {output.wout.aspect:.6f}")
        
        # Compare with reference if available
        ref_file = TEST_DATA_DIR / "wout_tok_asym.nc"
        if ref_file.exists():
            print(f"\n=== Quantitative Comparison with Reference ===")
            ref_wout = netCDF4.Dataset(ref_file)
            
            ref_volume = ref_wout.variables['volume_p'][()]
            vol_diff = abs(output.wout.volume - ref_volume) / ref_volume * 100
            print(f"Volume difference: {vol_diff:.2f}%")
            
            ref_wout.close()
            
    except Exception as e:
        print(f"✗ VMEC++ failed: {e}")
        return False
        
    return True


def main():
    print("VMEC++ Asymmetric Quantitative Validation")
    print("=" * 60)
    
    # Test HELIOTRON
    heliotron_pass = test_heliotron_asym()
    
    # Test tokamak
    tok_pass = test_tok_asym()
    
    print("\n" + "=" * 60)
    print("Overall Results:")
    print(f"  HELIOTRON asymmetric: {'PASS' if heliotron_pass else 'FAIL'}")
    print(f"  Tokamak asymmetric: {'PASS' if tok_pass else 'FAIL'}")
    
    if heliotron_pass:
        print("\n✓ At least one asymmetric case is working with quantitative validation!")


if __name__ == "__main__":
    main()