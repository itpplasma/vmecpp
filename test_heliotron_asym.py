#!/usr/bin/env python3
import vmecpp
import numpy as np

# Create HELIOTRON_asym input based on test case
input = vmecpp.VmecInput.default()

# Set asymmetric mode
input.lasym = True
input.nfp = 19
input.mpol = 5
input.ntor = 3

# Single grid for testing
input.ns_array = [7]
input.ftol_array = [1e-10]
input.niter_array = [500]

# Set boundary shape 
input.rbc = np.array([
    [10.0, 0.0, 0.0, 0.0],  # n=0
    [0.0, -0.3, 0.0, 0.0],  # n=-1  
    [0.0, -1.0, 0.0, 0.0],  # n=1
])

input.zbs = np.array([
    [0.0, 0.0, 0.0, 0.0],
    [0.0, -0.2, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
])

# Add small asymmetric boundary components
input.rbs = np.array([
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.05, 0.0, 0.0],  # Small asymmetric component
    [0.0, 0.03, 0.0, 0.0],
])

input.zbc = np.array([
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.02, 0.0, 0.0],  # Small asymmetric component
    [0.0, 0.01, 0.0, 0.0],
])

# Set a better initial axis guess with some shape
input.raxis_c = [10.0, 0.5, 0.0, 0.0]  
input.zaxis_s = [0.0, 0.5, 0.0, 0.0]
input.raxis_s = [0.0, 0.1, 0.0, 0.0]  # Small asymmetric axis
input.zaxis_c = [0.0, 0.1, 0.0, 0.0]  # Small asymmetric axis

# Set profiles
input.pmass_type = "power_series"
input.am = [1.0, -1.0]
input.pres_scale = 18000.0

input.piota_type = "power_series"
input.ai = [1.0, 1.5]

input.phiedge = 1.0

print("Running HELIOTRON_asym test with better axis guess...")
print(f"lasym = {input.lasym}")
print(f"nfp = {input.nfp}, mpol = {input.mpol}, ntor = {input.ntor}")
print(f"raxis_c = {input.raxis_c}")
print(f"zaxis_s = {input.zaxis_s}")

try:
    output = vmecpp.run(input, verbose=True)
    print(f"\nSUCCESS! Converged with FSQ = {output.fsql:.2e}")
    
    # Check asymmetric output
    if hasattr(output.wout, 'rmnsc') and output.wout.rmnsc is not None:
        print(f"\nAsymmetric arrays present:")
        print(f"- rmnsc shape: {output.wout.rmnsc.shape}")
        print(f"- Max |rmnsc|: {abs(output.wout.rmnsc).max():.3e}")
    else:
        print("\nWARNING: No asymmetric arrays in output")
        
except Exception as e:
    print(f"\nFAILED: {e}")
    import traceback
    traceback.print_exc()