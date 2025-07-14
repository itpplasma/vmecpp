#!/usr/bin/env python3
"""
Simple test to debug asymmetric loading issue.
"""
import vmecpp

print("Testing asymmetric input loading...")

try:
    print("Loading tokamak asymmetric...")
    vmec_input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Successfully loaded: lasym={vmec_input.lasym}, nfp={vmec_input.nfp}")
    print(f"rbs shape: {vmec_input.rbs.shape if vmec_input.rbs is not None else 'None'}")
    print(f"zbc shape: {vmec_input.zbc.shape if vmec_input.zbc is not None else 'None'}")
    
    print("Running VMECPP...")
    output = vmecpp.run(vmec_input)
    print(f"Converged: {output.success}")
    print("SUCCESS: Tokamak asymmetric case works!")
    
except Exception as e:
    print(f"ERROR with tokamak: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nLoading HELIOTRON asymmetric...")
    vmec_input = vmecpp.VmecInput.from_file("examples/data/HELIOTRON_asym.json")
    print(f"Successfully loaded: lasym={vmec_input.lasym}, nfp={vmec_input.nfp}")
    print(f"rbs shape: {vmec_input.rbs.shape if vmec_input.rbs is not None else 'None'}")
    print(f"zbc shape: {vmec_input.zbc.shape if vmec_input.zbc is not None else 'None'}")
    
    print("Running VMECPP...")
    output = vmecpp.run(vmec_input)
    print(f"Converged: {output.success}")
    print("SUCCESS: HELIOTRON asymmetric case works!")
    
except Exception as e:
    print(f"ERROR with HELIOTRON: {e}")
    import traceback
    traceback.print_exc()