#!/usr/bin/env python3
"""
Test asymmetric with simplest possible setup.
"""
import vmecpp

# First test symmetric case to ensure basic functionality works
print("Testing symmetric case...")
try:
    vmec_input = vmecpp.VmecInput.from_file("examples/data/cma.json")
    vmec_input.ns_array = [3]
    vmec_input.ftol_array = [1e-6]
    vmec_input.niter_array = [10]
    
    output = vmecpp.run(vmec_input, verbose=False)
    print(f"Symmetric case SUCCESS! Converged: {output.success}")
except Exception as e:
    print(f"Symmetric case ERROR: {e}")

# Now test asymmetric
print("\nTesting asymmetric case...")
try:
    vmec_input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Loaded: lasym={vmec_input.lasym}")
    
    # Use minimal settings
    vmec_input.ns_array = [3]
    vmec_input.ftol_array = [1e-6]
    vmec_input.niter_array = [5]
    
    print("Running...")
    output = vmecpp.run(vmec_input, verbose=False)
    print(f"Asymmetric case SUCCESS! Converged: {output.success}")
except Exception as e:
    print(f"Asymmetric case ERROR: {e}")
    import traceback
    traceback.print_exc()