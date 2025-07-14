#!/usr/bin/env python3
"""
Debug asymmetric execution systematically.
"""
import vmecpp
import numpy as np

print("Testing asymmetric with minimal ns_array...")

try:
    # Load the tokamak case
    vmec_input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Loaded: lasym={vmec_input.lasym}, ns_array={vmec_input.ns_array}")
    
    # Try with minimal radial resolution
    vmec_input.ns_array = [3]
    vmec_input.ftol_array = [1e-6]
    vmec_input.niter_array = [100]
    
    print(f"Running with ns_array={vmec_input.ns_array}")
    output = vmecpp.run(vmec_input, verbose=True)
    print(f"SUCCESS! Converged: {output.success}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()