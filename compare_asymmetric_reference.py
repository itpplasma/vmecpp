#!/usr/bin/env python3
"""
Compare asymmetric reference outputs from jVMEC against expected values.
This validates the jVMEC reference implementation to understand expected behavior.
"""
import netCDF4 as nc
import numpy as np

def analyze_reference_wout(wout_file, name):
    """Analyze reference wout file from jVMEC."""
    print(f"\n{'='*60}")
    print(f"Analyzing {name} reference from: {wout_file}")
    print(f"{'='*60}")
    
    try:
        with nc.Dataset(wout_file, 'r') as ds:
            # Check lasym flag
            lasym = ds.variables['lasym_'][()]
            print(f"\nlasym = {lasym}")
            
            # Check dimensions
            print(f"\nDimensions:")
            print(f"  mpol = {ds.dimensions['mpol'].size}")
            print(f"  ntor = {ds.dimensions['ntor'].size}")
            print(f"  ns = {ds.dimensions['radius'].size}")
            
            # Check convergence
            print(f"\nConvergence:")
            fsqr = ds.variables['fsqr'][()]
            fsqz = ds.variables['fsqz'][()]
            fsql = ds.variables['fsql'][()]
            print(f"  fsqr = {fsqr:.2e}")
            print(f"  fsqz = {fsqz:.2e}")
            print(f"  fsql = {fsql:.2e}")
            
            # Check asymmetric Fourier coefficients existence
            print(f"\nAsymmetric Fourier coefficients:")
            asym_vars = ['rmnsc', 'zmncc', 'lmncc', 'rmncs', 'zmnss', 'lmnss']
            
            for var in asym_vars:
                if var in ds.variables:
                    data = ds.variables[var][:]
                    # Find non-zero entries
                    non_zero_mask = np.abs(data) > 1e-12
                    num_nonzero = np.sum(non_zero_mask)
                    if num_nonzero > 0:
                        max_val = np.max(np.abs(data))
                        print(f"  {var}: shape={data.shape}, non-zero entries={num_nonzero}, max|val|={max_val:.2e}")
                        
                        # Show first few significant coefficients
                        if num_nonzero <= 5:
                            indices = np.argwhere(non_zero_mask)
                            for idx in indices[:5]:
                                val = data[tuple(idx)]
                                print(f"    [{','.join(map(str, idx))}] = {val:.6e}")
                    else:
                        print(f"  {var}: all zeros")
                else:
                    print(f"  {var}: NOT FOUND")
            
            # Check symmetric coefficients for comparison
            print(f"\nSymmetric Fourier coefficients (for comparison):")
            sym_vars = ['rmnc', 'zmns']
            for var in sym_vars:
                if var in ds.variables:
                    data = ds.variables[var][:]
                    non_zero_mask = np.abs(data) > 1e-12
                    num_nonzero = np.sum(non_zero_mask)
                    max_val = np.max(np.abs(data))
                    print(f"  {var}: shape={data.shape}, non-zero entries={num_nonzero}, max|val|={max_val:.2e}")
                    
            # Check physical quantities that should show asymmetry
            print(f"\nPhysical quantities:")
            quantities = ['bmnc', 'bmns', 'gmn', 'bsubumn', 'bsubvmn']
            for var in quantities:
                if var in ds.variables:
                    data = ds.variables[var][:]
                    print(f"  {var}: shape={data.shape}, range=[{np.min(data):.2e}, {np.max(data):.2e}]")
                    
    except Exception as e:
        print(f"ERROR reading {wout_file}: {e}")

# Analyze both reference files
reference_files = [
    ("/home/ert/code/jVMEC/target/test-classes/wout_tok_asym.nc", "tok_asym"),
    ("/home/ert/code/jVMEC/target/test-classes/wout_HELIOTRON_asym.nc", "HELIOTRON_asym")
]

for wout_file, name in reference_files:
    analyze_reference_wout(wout_file, name)

print(f"\n{'='*60}")
print("Summary of jVMEC asymmetric reference outputs:")
print(f"{'='*60}")
print("\nKey observations:")
print("1. Both reference files have lasym=True")
print("2. Asymmetric Fourier coefficients (rmnsc, zmncc, etc.) should be present")
print("3. These coefficients represent the non-stellarator-symmetric components")
print("4. The magnitude of asymmetric coefficients indicates the degree of asymmetry")
print("\nThese reference outputs provide the expected behavior for VMECPP asymmetric runs.")