#!/usr/bin/env python3
"""
Simple test of the asymmetric geometry combination fix
"""

import sys
import os
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    import numpy as np
    
    print("Testing asymmetric geometry combination fix...")
    
    # Create a simple asymmetric tokamak input
    input_data = vmecpp.VmecInput()
    input_data.lasym = True
    input_data.nfp = 1
    input_data.mpol = 5
    input_data.ntor = 0
    input_data.ntheta = 17
    input_data.nzeta = 1
    input_data.ns_array = [5]
    input_data.niter_array = [100]
    input_data.ftol_array = [1e-8]
    input_data.nstep = 100
    input_data.delt = 0.25
    input_data.ncurr = 0
    
    # Pressure profile
    input_data.am = [1.0, -2.0, 1.0]
    input_data.pres_scale = 100000.0
    
    # Current profile
    input_data.ai = [0.6, -0.45]
    input_data.curtor = 0.0
    input_data.gamma = 0.0
    input_data.phiedge = 119.15
    
    # Magnetic axis
    input_data.raxis_cc = [6.676]
    input_data.zaxis_cc = [0.47]
    
    # Boundary coefficients (including asymmetric terms)
    input_data.rbc = np.zeros((input_data.mpol, input_data.ntor + 1))
    input_data.rbs = np.zeros((input_data.mpol, input_data.ntor + 1))
    input_data.zbc = np.zeros((input_data.mpol, input_data.ntor + 1))
    input_data.zbs = np.zeros((input_data.mpol, input_data.ntor + 1))
    
    # Symmetric components
    input_data.rbc[0, 0] = 5.91630000E+00
    input_data.rbc[1, 0] = 1.91960000E+00
    input_data.rbc[2, 0] = 3.37360000E-01
    input_data.rbc[3, 0] = 4.15040000E-02
    input_data.rbc[4, 0] = -5.82560000E-03
    
    input_data.zbs[1, 0] = 3.62230000E+00
    input_data.zbs[2, 0] = -1.85110000E-01
    input_data.zbs[3, 0] = -4.85680000E-03
    input_data.zbs[4, 0] = 5.92680000E-02
    
    # Asymmetric components (these should trigger the fix)
    input_data.rbs[1, 0] = 2.76100000E-02
    input_data.rbs[2, 0] = 1.00380000E-01
    input_data.rbs[3, 0] = -7.18430000E-02
    input_data.rbs[4, 0] = -1.14230000E-02
    
    input_data.zbc[0, 0] = 4.10500000E-01
    input_data.zbc[1, 0] = 5.73020000E-02
    input_data.zbc[2, 0] = 4.66970000E-03
    input_data.zbc[3, 0] = -3.91550000E-02
    input_data.zbc[4, 0] = -8.78480000E-03
    
    print("Input configuration:")
    print(f"  lasym = {input_data.lasym}")
    print(f"  nfp = {input_data.nfp}")
    print(f"  mpol = {input_data.mpol}")
    print(f"  ntor = {input_data.ntor}")
    print(f"  ns_array = {input_data.ns_array}")
    print(f"  Major radius R00 = {input_data.rbc[0, 0]}")
    print(f"  R10 cos = {input_data.rbc[1, 0]}")
    print(f"  R10 sin = {input_data.rbs[1, 0]}")
    print(f"  Z00 cos = {input_data.zbc[0, 0]}")
    print(f"  Z10 sin = {input_data.zbs[1, 0]}")
    print(f"  Z10 cos = {input_data.zbc[1, 0]}")
    
    print("\nTesting if the initial Jacobian sign error is fixed...")
    
    # Try to run the equilibrium
    try:
        output = vmecpp.run(input_data, max_threads=1, verbose=False)
        print("SUCCESS: Asymmetric equilibrium converged!")
        print(f"Final force residual: {output.fsqr}")
        print(f"Iterations: {output.iter2}")
        print(f"Beta: {output.beta_vol}")
        
    except Exception as e:
        print(f"FAILED: {e}")
        if "INITIAL JACOBIAN CHANGED SIGN" in str(e):
            print("The initial Jacobian sign error is still present.")
            print("The geometry combination fix needs further work.")
        else:
            print("Different error - may indicate progress.")
        
except ImportError as e:
    print(f"Failed to import vmecpp: {e}")
    print("Try: pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)