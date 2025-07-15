#!/usr/bin/env python3
import vmecpp

print("Debug: Testing basic asymmetric run with force fix")

# Very simple test - just check if it crashes immediately
input1 = vmecpp.VmecInput.default()
input1.lasym = True
input1.nfp = 1
input1.mpol = 2
input1.ntor = 0
input1.ns_array = [3]
input1.ftol_array = [1e-6]
input1.niter_array = [5]  # Very few iterations

# Simple tokamak-like
input1.rbc = [[0, 0, 3.0], [1, 0, 0.5]]
input1.zbs = [[0, 0, 0.0], [1, 0, 0.5]]
input1.raxis_c = [3.0]
input1.zaxis_s = [0.0]
input1.raxis_s = [0.0]
input1.zaxis_c = [0.0]

# Small asymmetric  
input1.rbs = [[0, 0, 0.0], [1, 0, 0.01]]
input1.zbc = [[0, 0, 0.0], [1, 0, 0.01]]

# Very low pressure
input1.pres_scale = 10.0
input1.am = [1.0]

print("Starting run...")
try:
    output = vmecpp.run(input1, verbose=True)
    print("SUCCESS - no segfault!")
    print(f"FSQ = {output.fsql:.2e}")
except Exception as e:
    print(f"Error: {e}")