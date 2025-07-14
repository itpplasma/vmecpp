#!/usr/bin/env python3
"""
Validation script to compare VMECPP asymmetric outputs against jVMEC reference.

This script runs VMECPP with asymmetric test cases and compares the outputs
against reference wout files from jVMEC.
"""
import os
import sys
import numpy as np
import netCDF4 as nc
from pathlib import Path

import vmecpp


def load_reference_wout(wout_path):
    """Load reference wout file and extract key quantities."""
    with nc.Dataset(wout_path, 'r') as ds:
        data = {}
        
        # Basic parameters
        data['nfp'] = int(ds.variables['nfp'][:])
        data['mpol'] = int(ds.variables['mpol'][:])
        data['ntor'] = int(ds.variables['ntor'][:])
        data['ns'] = int(ds.variables['ns'][:])
        data['lasym'] = bool(ds.variables['lasym__logical__'][:])
        
        # Convergence metrics
        data['fsqr'] = float(ds.variables['fsqr'][:])
        data['fsqz'] = float(ds.variables['fsqz'][:])
        data['fsql'] = float(ds.variables['fsql'][:])
        
        # Fourier coefficients (symmetric)
        data['rmnc'] = ds.variables['rmnc'][:]
        data['zmns'] = ds.variables['zmns'][:]
        data['lmns'] = ds.variables['lmns'][:]
        
        # Asymmetric Fourier coefficients (if present)
        if data['lasym']:
            data['rmns'] = ds.variables['rmns'][:]
            data['zmnc'] = ds.variables['zmnc'][:]
            data['lmnc'] = ds.variables['lmnc'][:]
        
        # Physical quantities
        data['volavgB'] = float(ds.variables['volavgB'][:])
        data['volume'] = float(ds.variables['volume'][:])
        data['beta_vol'] = float(ds.variables['beta_vol'][:])
        
        # Rotational transform
        data['iotaf'] = ds.variables['iotaf'][:]
        
        # Mode numbers
        data['xm'] = ds.variables['xm'][:]
        data['xn'] = ds.variables['xn'][:]
        
    return data


def compare_quantities(vmecpp_data, reference_data, quantity_name, 
                      rtol=1e-10, atol=1e-12):
    """Compare a specific quantity between VMECPP and reference."""
    vmecpp_val = vmecpp_data.get(quantity_name)
    ref_val = reference_data.get(quantity_name)
    
    if vmecpp_val is None or ref_val is None:
        return f"❌ {quantity_name}: Missing in one of the datasets"
    
    # Handle scalar vs array comparison
    if np.isscalar(vmecpp_val) and np.isscalar(ref_val):
        diff = abs(vmecpp_val - ref_val)
        rel_diff = diff / max(abs(ref_val), 1e-15)
        if diff < atol or rel_diff < rtol:
            return f"✅ {quantity_name}: {vmecpp_val:.6e} (diff: {diff:.2e})"
        else:
            return f"❌ {quantity_name}: {vmecpp_val:.6e} vs {ref_val:.6e} (diff: {diff:.2e}, rel: {rel_diff:.2e})"
    
    # Array comparison
    try:
        vmecpp_arr = np.asarray(vmecpp_val)
        ref_arr = np.asarray(ref_val)
        
        if vmecpp_arr.shape != ref_arr.shape:
            return f"❌ {quantity_name}: Shape mismatch {vmecpp_arr.shape} vs {ref_arr.shape}"
        
        max_abs_diff = np.max(np.abs(vmecpp_arr - ref_arr))
        max_rel_diff = np.max(np.abs(vmecpp_arr - ref_arr) / np.maximum(np.abs(ref_arr), 1e-15))
        
        if max_abs_diff < atol or max_rel_diff < rtol:
            return f"✅ {quantity_name}: Arrays match (max diff: {max_abs_diff:.2e}, max rel: {max_rel_diff:.2e})"
        else:
            return f"❌ {quantity_name}: Arrays differ (max diff: {max_abs_diff:.2e}, max rel: {max_rel_diff:.2e})"
    
    except Exception as e:
        return f"❌ {quantity_name}: Comparison failed - {e}"


def validate_asymmetric_case(input_json_path, reference_wout_path, case_name):
    """Validate a single asymmetric test case."""
    print(f"\n{'='*60}")
    print(f"Validating {case_name}")
    print(f"{'='*60}")
    
    # Check if reference file exists
    if not Path(reference_wout_path).exists():
        print(f"❌ Reference file not found: {reference_wout_path}")
        return False
    
    try:
        # Load VMECPP input and run
        print(f"Loading input: {input_json_path}")
        vmec_input = vmecpp.VmecInput.from_file(input_json_path)
        print(f"Running VMECPP with lasym={vmec_input.lasym}")
        
        vmec_output = vmecpp.run(vmec_input)
        
        # Extract VMECPP data
        wout = vmec_output.wout
        vmecpp_data = {
            'nfp': wout.nfp,
            'mpol': wout.mpol,
            'ntor': wout.ntor,
            'ns': wout.ns,
            'lasym': wout.lasym,
            'fsqr': wout.fsqr,
            'fsqz': wout.fsqz,
            'fsql': wout.fsql,
            'rmnc': wout.rmnc,
            'zmns': wout.zmns,
            'lmns': wout.lmns,
            'volavgB': wout.volavgB,
            'volume': wout.volume,
            'beta_vol': wout.beta_vol,
            'iotaf': wout.iotaf,
            'xm': wout.xm,
            'xn': wout.xn,
        }
        
        # Add asymmetric quantities if present
        if wout.lasym:
            vmecpp_data.update({
                'rmns': wout.rmns,
                'zmnc': wout.zmnc,
                'lmnc': wout.lmnc,
            })
        
        # Load reference data
        print(f"Loading reference: {reference_wout_path}")
        reference_data = load_reference_wout(reference_wout_path)
        
        # Compare key quantities
        print(f"\nComparison Results:")
        print(f"-" * 40)
        
        # Basic parameters
        results = []
        results.append(compare_quantities(vmecpp_data, reference_data, 'nfp'))
        results.append(compare_quantities(vmecpp_data, reference_data, 'mpol'))
        results.append(compare_quantities(vmecpp_data, reference_data, 'ntor'))
        results.append(compare_quantities(vmecpp_data, reference_data, 'ns'))
        results.append(compare_quantities(vmecpp_data, reference_data, 'lasym'))
        
        # Convergence metrics (more relaxed tolerances)
        results.append(compare_quantities(vmecpp_data, reference_data, 'fsqr', rtol=1e-6, atol=1e-10))
        results.append(compare_quantities(vmecpp_data, reference_data, 'fsqz', rtol=1e-6, atol=1e-10))
        results.append(compare_quantities(vmecpp_data, reference_data, 'fsql', rtol=1e-6, atol=1e-10))
        
        # Physical quantities
        results.append(compare_quantities(vmecpp_data, reference_data, 'volavgB', rtol=1e-8))
        results.append(compare_quantities(vmecpp_data, reference_data, 'volume', rtol=1e-8))
        results.append(compare_quantities(vmecpp_data, reference_data, 'beta_vol', rtol=1e-8))
        
        # Fourier coefficients (relaxed tolerances for numerical differences)
        results.append(compare_quantities(vmecpp_data, reference_data, 'rmnc', rtol=1e-6, atol=1e-10))
        results.append(compare_quantities(vmecpp_data, reference_data, 'zmns', rtol=1e-6, atol=1e-10))
        results.append(compare_quantities(vmecpp_data, reference_data, 'lmns', rtol=1e-6, atol=1e-10))
        
        # Asymmetric coefficients (if present)
        if vmecpp_data.get('lasym', False):
            results.append(compare_quantities(vmecpp_data, reference_data, 'rmns', rtol=1e-6, atol=1e-10))
            results.append(compare_quantities(vmecpp_data, reference_data, 'zmnc', rtol=1e-6, atol=1e-10))
            results.append(compare_quantities(vmecpp_data, reference_data, 'lmnc', rtol=1e-6, atol=1e-10))
        
        # Rotational transform
        results.append(compare_quantities(vmecpp_data, reference_data, 'iotaf', rtol=1e-8))
        
        # Print all results
        for result in results:
            print(result)
        
        # Summary
        passed = sum(1 for r in results if r.startswith('✅'))
        total = len(results)
        print(f"\nSummary: {passed}/{total} checks passed")
        
        if passed == total:
            print(f"🎉 {case_name}: ALL CHECKS PASSED")
            return True
        else:
            print(f"⚠️  {case_name}: {total-passed} checks failed")
            return False
            
    except Exception as e:
        print(f"❌ Error validating {case_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main validation routine."""
    print("VMECPP Asymmetric Output Validation")
    print("====================================")
    
    # Define test cases
    test_cases = [
        {
            'name': 'Asymmetric Tokamak',
            'input': 'examples/data/tok_asym.json',
            'reference': '../jVMEC/target/test-classes/wout_tok_asym.nc'
        },
        {
            'name': 'Asymmetric HELIOTRON',
            'input': 'examples/data/HELIOTRON_asym.json', 
            'reference': '../jVMEC/target/test-classes/wout_HELIOTRON_asym.nc'
        }
    ]
    
    # Run validation for each case
    all_passed = True
    for case in test_cases:
        success = validate_asymmetric_case(
            case['input'],
            case['reference'],
            case['name']
        )
        all_passed = all_passed and success
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    if all_passed:
        print("🎉 ALL ASYMMETRIC VALIDATION TESTS PASSED")
        print("VMECPP asymmetric implementation is validated against jVMEC reference")
        return 0
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
        print("Review the differences above for further investigation")
        return 1


if __name__ == "__main__":
    sys.exit(main())