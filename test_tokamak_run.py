#!/usr/bin/env python3
"""
Test running just the tokamak case to isolate segfault.
"""
import vmecpp

print("Testing tokamak asymmetric run...")

try:
    print("Loading tokamak asymmetric...")
    vmec_input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Successfully loaded: lasym={vmec_input.lasym}, nfp={vmec_input.nfp}")
    
    print("Running VMECPP...")
    output = vmecpp.run(vmec_input)
    print(f"Converged: {output.success}")
    print("SUCCESS: Tokamak asymmetric execution works!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()