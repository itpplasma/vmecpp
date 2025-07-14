#!/usr/bin/env python3
"""
Inspect reference wout files to see what variables they contain.
"""
import netCDF4 as nc

def inspect_wout(wout_file, name):
    """Inspect wout file structure."""
    print(f"\n{'='*60}")
    print(f"Inspecting {name}: {wout_file}")
    print(f"{'='*60}")
    
    try:
        with nc.Dataset(wout_file, 'r') as ds:
            # List all variables
            print("\nVariables in file:")
            var_names = sorted(ds.variables.keys())
            for var in var_names:
                v = ds.variables[var]
                print(f"  {var}: shape={v.shape}, dtype={v.dtype}")
                
            # Check for lasym-related variables
            print("\nSearching for lasym-related variables:")
            lasym_vars = [v for v in var_names if 'lasym' in v.lower()]
            if lasym_vars:
                for var in lasym_vars:
                    v = ds.variables[var]
                    print(f"  {var} = {v[()]}")
            else:
                print("  No variables with 'lasym' found")
                
            # Check for asymmetric coefficients
            print("\nSearching for asymmetric coefficient variables:")
            asym_patterns = ['sc', 'cc', 'cs', 'ss']
            asym_vars = []
            for var in var_names:
                for pattern in asym_patterns:
                    if var.endswith(pattern) and len(var) > 2:
                        asym_vars.append(var)
                        break
            
            if asym_vars:
                print(f"  Found {len(asym_vars)} potential asymmetric variables:")
                for var in sorted(asym_vars)[:10]:  # Show first 10
                    print(f"    {var}")
            else:
                print("  No asymmetric coefficient variables found")
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

# Inspect reference files
reference_files = [
    ("/home/ert/code/jVMEC/target/test-classes/wout_tok_asym.nc", "tok_asym"),
    ("/home/ert/code/jVMEC/target/test-classes/wout_HELIOTRON_asym.nc", "HELIOTRON_asym")
]

for wout_file, name in reference_files:
    inspect_wout(wout_file, name)