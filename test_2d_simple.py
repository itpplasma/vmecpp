#!/usr/bin/env python3
import vmecpp
import numpy as np

print("Testing simple 2D symmetric case first...")

# Test simple 2D symmetric first
input1 = vmecpp.VmecInput.default()
input1.lasym = False  # Start with symmetric
input1.nfp = 1
input1.mpol = 3
input1.ntor = 0  # 2D case
input1.ns_array = [5]
input1.ftol_array = [1e-6]
input1.niter_array = [10]

# Simple tokamak boundary
input1.rbc = np.array([
    [3.0],   # m=0, n=0: R0
    [0.5],   # m=1, n=0: minor radius
    [0.0],   # m=2, n=0
])
input1.zbs = np.array([
    [0.0],   # m=0, n=0
    [0.5],   # m=1, n=0: Z shaping 
    [0.0],   # m=2, n=0
])

input1.raxis_c = [3.0]
input1.zaxis_s = [0.0]
input1.pres_scale = 1000.0
input1.am = [1.0]
input1.curtor = 0.0

try:
    print(f"2D symmetric: ntor={input1.ntor}, lasym={input1.lasym}")
    output1 = vmecpp.run(input1, verbose=False)
    print(f"SUCCESS! 2D symmetric converged with FSQ = {output1.fsql:.2e}")
except Exception as e:
    print(f"FAILED: {e}")