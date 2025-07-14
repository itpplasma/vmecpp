#!/usr/bin/env python3
"""
Test script to verify asymmetric force handling fix
"""

import sys
import os
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    
    # Test the tokamak asymmetric case
    print("Testing tokamak asymmetric case...")
    
    # Create input from known working symmetric case and enable asymmetric
    input_data = vmecpp.VmecInput.from_file('/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/input.solovev')
    input_data.lasym = True
    input_data.ns_array = [5]  # Small grid for quick test
    input_data.niter_array = [100]  # Reduced iterations
    input_data.ftol_array = [1e-12]  # Convergence tolerance
    
    # Initialize boundary coefficients if needed
    if input_data.rbc is None:
        import numpy as np
        input_data.rbc = np.zeros((input_data.mpol, input_data.ntor + 1))
        input_data.rbs = np.zeros((input_data.mpol, input_data.ntor + 1))
        input_data.zbc = np.zeros((input_data.mpol, input_data.ntor + 1))
        input_data.zbs = np.zeros((input_data.mpol, input_data.ntor + 1))
    
    # Add small asymmetric perturbation
    input_data.rbc[0, 0] = 6.0  # R00 coefficient
    input_data.rbc[1, 0] = 0.1  # R10 coefficient  
    input_data.rbs[1, 0] = 0.05  # R10 sin component (asymmetric)
    input_data.zbc[1, 0] = 0.05  # Z10 cos component (asymmetric)
    
    print("Input configuration:")
    print(f"  lasym = {input_data.lasym}")
    print(f"  ns_array = {input_data.ns_array}")
    print(f"  niter_array = {input_data.niter_array}")
    print(f"  R00 = {input_data.rbc[0, 0]}")
    print(f"  R10 = {input_data.rbc[1, 0]}")
    print(f"  R10s = {input_data.rbs[1, 0]}")
    print(f"  Z10c = {input_data.zbc[1, 0]}")
    
    # Try to run the equilibrium
    print("\nAttempting to run asymmetric equilibrium...")
    try:
        output = vmecpp.run(input_data, max_threads=1, verbose=True)
        print("SUCCESS: Asymmetric equilibrium converged!")
        print(f"Final force residual: {output.fsqr}")
        print(f"Iterations: {output.iter2}")
        print(f"Beta: {output.beta_vol}")
    except Exception as e:
        print(f"FAILED: {e}")
        print("\nThis indicates the asymmetric force handling fix needs more work")
        
except ImportError as e:
    print(f"Failed to import vmecpp: {e}")
    print("Try: pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)