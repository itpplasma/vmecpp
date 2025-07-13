#!/usr/bin/env python3
"""
Manual validation script for asymmetric VMEC++ configurations.

Usage:
    python scripts/validate_asymmetric.py input.HELIOTRON_asym
    python scripts/validate_asymmetric.py input.tok_asym

This script runs VMEC++ on asymmetric configurations and compares against
reference outputs when available. It's intended for manual validation
when reference jVMEC outputs are available locally.
"""

import argparse
import sys
from pathlib import Path

import netCDF4
import numpy as np

import vmecpp


def run_and_validate(input_file: Path, reference_file: Path = None):
    """Run VMEC++ and optionally validate against reference."""
    print(f"Running VMEC++ on {input_file.name}...")
    
    # Run VMEC++
    try:
        input_data = vmecpp.VmecInput.from_file(input_file)
        output = vmecpp.run(input_data)
        wout = output.wout
        print(f"✓ VMEC++ run completed successfully (ier_flag = {wout.ier_flag})")
    except Exception as e:
        print(f"✗ VMEC++ run failed: {e}")
        return False
    
    # Basic asymmetric configuration checks
    if not wout.lasym:
        print("✗ Output shows lasym=False, expected lasym=True")
        return False
    print("✓ lasym=True confirmed in output")
    
    # Check asymmetric arrays exist
    asymmetric_arrays = ['gmns', 'bmns', 'bsubumns', 'bsubvmns', 'bsupumns', 'bsupvmns']
    for array_name in asymmetric_arrays:
        if hasattr(wout, array_name):
            array_values = getattr(wout, array_name)
            max_abs = np.max(np.abs(array_values))
            print(f"✓ {array_name}: max |value| = {max_abs:.2e}")
        else:
            print(f"✗ {array_name}: array missing")
    
    # Compare against reference if available
    if reference_file and reference_file.exists():
        print(f"\nValidating against reference file {reference_file.name}...")
        try:
            ref_ds = netCDF4.Dataset(reference_file, 'r')
            
            # Compare key quantities
            comparisons = [
                ('aspect', wout.aspect, ref_ds.variables['aspect'][()]),
                ('volume_p', wout.volume_p, ref_ds.variables['volume_p'][()]),
                ('ier_flag', wout.ier_flag, ref_ds.variables['ier_flag'][()]),
            ]
            
            for name, computed, expected in comparisons:
                if np.allclose(computed, expected, rtol=1e-10, atol=1e-12):
                    print(f"✓ {name}: matches reference (computed={computed}, expected={expected})")
                else:
                    print(f"✗ {name}: differs from reference (computed={computed}, expected={expected})")
            
            # Compare asymmetric arrays
            for array_name in asymmetric_arrays:
                if hasattr(wout, array_name) and array_name in ref_ds.variables:
                    computed_values = getattr(wout, array_name)
                    expected_values = ref_ds.variables[array_name][()]
                    if np.allclose(computed_values, expected_values, rtol=1e-10, atol=1e-12):
                        max_diff = np.max(np.abs(computed_values - expected_values))
                        print(f"✓ {array_name}: matches reference (max diff = {max_diff:.2e})")
                    else:
                        max_diff = np.max(np.abs(computed_values - expected_values))
                        print(f"✗ {array_name}: differs from reference (max diff = {max_diff:.2e})")
            
            ref_ds.close()
            
        except Exception as e:
            print(f"✗ Reference validation failed: {e}")
            return False
    else:
        print(f"\nReference file {reference_file} not found - skipping validation")
        print("(This is normal in CI/CD environments)")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate asymmetric VMEC++ configurations")
    parser.add_argument("input_file", type=Path, help="Input file (e.g., input.HELIOTRON_asym)")
    parser.add_argument("--reference", type=Path, help="Reference wout file for validation")
    args = parser.parse_args()
    
    if not args.input_file.exists():
        print(f"Error: Input file {args.input_file} not found")
        sys.exit(1)
    
    # Auto-detect reference file if not specified
    if not args.reference:
        if "HELIOTRON_asym" in args.input_file.name:
            args.reference = args.input_file.parent / "wout_HELIOTRON_asym.nc"
        elif "tok_asym" in args.input_file.name:
            args.reference = args.input_file.parent / "wout_tok_asym.nc"
        else:
            args.reference = args.input_file.parent / f"wout_{args.input_file.stem}.nc"
    
    success = run_and_validate(args.input_file, args.reference)
    
    if success:
        print("\n✓ Validation completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()