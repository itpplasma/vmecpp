#!/usr/bin/env python3
"""
Check dimensions in jVMEC wout files.
"""
import netCDF4 as nc
import numpy as np

def check_file(wout_file, name):
    """Check file dimensions and structure."""
    print(f"\n{'='*60}")
    print(f"Checking {name}: {wout_file}")
    print(f"{'='*60}")
    
    try:
        with nc.Dataset(wout_file, 'r') as ds:
            # List dimensions
            print("\nDimensions:")
            for dim_name, dim in ds.dimensions.items():
                print(f"  {dim_name}: {dim.size}")
                
            # Check specific variables
            print("\nKey variables:")
            
            # Get mpol, ntor from variables
            mpol = int(ds.variables['mpol'][()])
            ntor = int(ds.variables['ntor'][()])
            ns = int(ds.variables['ns'][()])
            print(f"  mpol = {mpol}")
            print(f"  ntor = {ntor}")
            print(f"  ns = {ns}")
            
            # Check Fourier arrays
            print("\nFourier coefficient arrays:")
            for var in ['rmnc', 'zmns', 'rmns', 'zmnc']:
                if var in ds.variables:
                    shape = ds.variables[var].shape
                    data = ds.variables[var][:]
                    non_zero = np.sum(np.abs(data) > 1e-12)
                    max_val = np.max(np.abs(data))
                    print(f"  {var}: shape={shape}, non-zero={non_zero}, |max|={max_val:.2e}")
                else:
                    print(f"  {var}: NOT FOUND")
                    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

# Check both files
reference_files = [
    ("/home/ert/code/jVMEC/target/test-classes/wout_tok_asym.nc", "tok_asym"),
    ("/home/ert/code/jVMEC/target/test-classes/wout_HELIOTRON_asym.nc", "HELIOTRON_asym")
]

for wout_file, name in reference_files:
    check_file(wout_file, name)