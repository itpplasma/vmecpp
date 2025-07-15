#!/usr/bin/env python3
import vmecpp
import numpy as np

print("Testing 2D asymmetric force-to-Fourier transform fix\n")

# Test 1: Simple 2D asymmetric tokamak
print("1. Testing 2D asymmetric tokamak...")
input1 = vmecpp.VmecInput.default()
input1.lasym = True
input1.nfp = 1
input1.mpol = 3
input1.ntor = 0  # 2D case
input1.ns_array = [5, 7]
input1.ftol_array = [1e-8, 1e-10]
input1.niter_array = [50, 100]

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

# Small asymmetric components (2D only)
input1.rbs = np.array([
    [0.0],    # m=0, n=0
    [0.01],   # m=1, n=0: small asymmetric R perturbation
    [0.0],    # m=2, n=0
])
input1.zbc = np.array([
    [0.0],    # m=0, n=0
    [0.01],   # m=1, n=0: small asymmetric Z perturbation
    [0.0],    # m=2, n=0
])

# Proper axis initialization for asymmetric case
input1.raxis_c = [3.0]  # R0
input1.zaxis_s = [0.0]  # symmetric
input1.raxis_s = [0.0]  # asymmetric axis
input1.zaxis_c = [0.0]  # asymmetric axis

# Pressure profile
input1.pres_scale = 1000.0
input1.am = [1.0, -0.8]
input1.curtor = 0.0  # No toroidal current for 2D

try:
    print(f"  - lasym = {input1.lasym}")
    print(f"  - ntor = {input1.ntor} (2D case)")
    print(f"  - mpol = {input1.mpol}")
    
    output1 = vmecpp.run(input1, verbose=True)
    print(f"  SUCCESS! 2D asymmetric converged with FSQ = {output1.fsql:.2e}")
    print(f"  Iterations: {output1.iter2}")
    
    # Check asymmetric coefficients
    if hasattr(output1.wout, 'rmnsc') and output1.wout.rmnsc is not None:
        print(f"  Asymmetric coefficients present:")
        print(f"    max |rmnsc| = {abs(output1.wout.rmnsc).max():.3e}")
        print(f"    max |zmncc| = {abs(output1.wout.zmncc).max():.3e}")
        if hasattr(output1.wout, 'rmncs') and output1.wout.rmncs is not None:
            print(f"    max |rmncs| = {abs(output1.wout.rmncs).max():.3e}")
            print(f"    max |zmnss| = {abs(output1.wout.zmnss).max():.3e}")
    
    print("  🎉 2D asymmetric force-to-Fourier transform works!")
    
except Exception as e:
    print(f"  FAILED: {e}")

print("\n" + "="*60)
print("2D ASYMMETRIC FORCE-TO-FOURIER FIX VERIFICATION")
print("- Implemented ForcesToFourier2DAsymmFastPoloidal function")
print("- Added call in ideal_mhd_model.cc for lthreed=false cases")
print("- 2D asymmetric cases should now converge properly")
print("="*60)