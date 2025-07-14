#!/usr/bin/env python3
"""
Test just loading asymmetric inputs without running.
"""
import vmecpp

print("Testing asymmetric input loading (loading only)...")

try:
    print("Loading tokamak asymmetric...")
    vmec_input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Successfully loaded: lasym={vmec_input.lasym}, nfp={vmec_input.nfp}")
    print(f"mpol={vmec_input.mpol}, ntor={vmec_input.ntor}")
    print(f"rbs shape: {vmec_input.rbs.shape if vmec_input.rbs is not None else 'None'}")
    print(f"zbc shape: {vmec_input.zbc.shape if vmec_input.zbc is not None else 'None'}")
    print("SUCCESS: Tokamak loading works!")
    
except Exception as e:
    print(f"ERROR with tokamak loading: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nLoading HELIOTRON asymmetric...")
    vmec_input = vmecpp.VmecInput.from_file("examples/data/HELIOTRON_asym.json")
    print(f"Successfully loaded: lasym={vmec_input.lasym}, nfp={vmec_input.nfp}")
    print(f"mpol={vmec_input.mpol}, ntor={vmec_input.ntor}")
    print(f"rbs shape: {vmec_input.rbs.shape if vmec_input.rbs is not None else 'None'}")
    print(f"zbc shape: {vmec_input.zbc.shape if vmec_input.zbc is not None else 'None'}")
    print("SUCCESS: HELIOTRON loading works!")
    
except Exception as e:
    print(f"ERROR with HELIOTRON loading: {e}")
    import traceback
    traceback.print_exc()

print("All loading tests completed.")