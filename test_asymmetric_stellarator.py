#!/usr/bin/env python3
import vmecpp
import numpy as np

print("Testing asymmetric stellarator configurations\n")

# Test 1: Asymmetric stellarator with better boundary
print("1. Testing asymmetric stellarator...")
input1 = vmecpp.VmecInput.default()
input1.lasym = True
input1.nfp = 2
input1.mpol = 4
input1.ntor = 2
input1.ns_array = [11]
input1.ftol_array = [1e-10]
input1.niter_array = [200]

# Better shaped stellarator boundary
input1.rbc = np.array([
    [4.0, 0.0, 0.0],  # m=0
    [0.0, 0.4, 0.0],  # m=1  
    [0.0, 0.0, 0.1],  # m=2
    [0.0, 0.0, 0.0],  # m=3
])
input1.zbs = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 0.4, 0.0],
    [0.0, 0.0, 0.1],
    [0.0, 0.0, 0.0],
])

# Add small asymmetric components
input1.rbs = np.array([
    [0.0, 0.0, 0.0],  # m=0
    [0.0, 0.01, 0.0], # m=1
    [0.0, 0.0, 0.005], # m=2
    [0.0, 0.0, 0.0],  # m=3
])
input1.zbc = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 0.01, 0.0],
    [0.0, 0.0, 0.005],
    [0.0, 0.0, 0.0],
])

# Axis initialization
input1.raxis_c = [4.0, 0.0, 0.0]
input1.zaxis_s = [0.0, 0.0, 0.0]
input1.raxis_s = [0.0, 0.0, 0.0]
input1.zaxis_c = [0.0, 0.0, 0.0]

# Moderate pressure
input1.pres_scale = 1000.0
input1.am = [1.0, -1.0]
input1.curtor = 0.0

try:
    output1 = vmecpp.run(input1, verbose=False)
    print(f"SUCCESS! Converged with FSQ = {output1.fsql:.2e}")
    if hasattr(output1.wout, 'rmnsc') and output1.wout.rmnsc is not None:
        print(f"Has asymmetric arrays:")
        print(f"  max |rmnsc| = {abs(output1.wout.rmnsc).max():.3e}")
        print(f"  max |zmncc| = {abs(output1.wout.zmncc).max():.3e}")
        print(f"  max |rmncs| = {abs(output1.wout.rmncs).max():.3e}")
        print(f"  max |zmnss| = {abs(output1.wout.zmnss).max():.3e}")
except Exception as e:
    print(f"FAILED: {e}")

# Test 2: QAS-like configuration
print("\n2. Testing QAS-like configuration...")
input2 = vmecpp.VmecInput.default()
input2.lasym = True
input2.nfp = 4
input2.mpol = 3
input2.ntor = 1
input2.ns_array = [7]
input2.ftol_array = [1e-8]
input2.niter_array = [100]

# QAS boundary
input2.rbc = np.array([
    [3.0, 0.0],  # m=0
    [0.0, 0.3],  # m=1
    [0.0, 0.0],  # m=2
])
input2.zbs = np.array([
    [0.0, 0.0],
    [0.0, 0.3],
    [0.0, 0.0],
])

# QAS asymmetric components
input2.rbs = np.array([
    [0.0, 0.0],
    [0.0, 0.02],
    [0.0, 0.0],
])
input2.zbc = np.array([
    [0.0, 0.0],
    [0.0, 0.02],
    [0.0, 0.0],
])

# Axis
input2.raxis_c = [3.0, 0.0]
input2.zaxis_s = [0.0, 0.0]
input2.raxis_s = [0.0, 0.01]
input2.zaxis_c = [0.0, 0.01]

# Low pressure
input2.pres_scale = 100.0
input2.am = [1.0, -0.5]

try:
    output2 = vmecpp.run(input2, verbose=False)
    print(f"SUCCESS! Converged with FSQ = {output2.fsql:.2e}")
    if hasattr(output2.wout, 'rmnsc') and output2.wout.rmnsc is not None:
        print(f"QAS asymmetric components:")
        print(f"  max |rmnsc| = {abs(output2.wout.rmnsc).max():.3e}")
        print(f"  max |zmncc| = {abs(output2.wout.zmncc).max():.3e}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "="*60)
print("ASYMMETRIC STELLARATOR TESTS COMPLETE")
print("="*60)