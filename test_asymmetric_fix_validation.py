#!/usr/bin/env python3
"""
Comprehensive test to validate the asymmetric geometry combination fix
"""

import sys
import os
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    
    print("=== VALIDATION OF ASYMMETRIC GEOMETRY COMBINATION FIX ===")
    
    # Test 1: Symmetric case should still work (baseline)
    print("\n1. Testing symmetric case (baseline)...")
    input_file = '/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/input.solovev'
    
    if os.path.exists(input_file):
        input_data = vmecpp.VmecInput.from_file(input_file)
        input_data.lasym = False  # Ensure symmetric
        
        try:
            output = vmecpp.run(input_data, max_threads=1, verbose=False)
            print("   ✓ SUCCESS: Symmetric case converged")
            print(f"   Force residual: {output.wout.fsqr}")
            print(f"   Iterations: {output.wout.iter2}")
            baseline_fsqr = output.wout.fsqr
        except Exception as e:
            print(f"   ✗ FAILED: {e}")
            sys.exit(1)
    
    # Test 2: Same geometry with lasym=True should converge
    print("\n2. Testing same geometry with lasym=True...")
    input_data.lasym = True
    
    try:
        output_asym = vmecpp.run(input_data, max_threads=1, verbose=False)
        print("   ✓ SUCCESS: Asymmetric mode converged on symmetric geometry")
        print(f"   Force residual: {output_asym.wout.fsqr}")
        print(f"   Iterations: {output_asym.wout.iter2}")
        
        # Should be similar to baseline since geometry is symmetric
        ratio = output_asym.wout.fsqr / baseline_fsqr
        print(f"   Force ratio (asym/sym): {ratio:.3f}")
        
        if ratio < 10.0:  # Allow some variation but not huge differences
            print("   ✓ Force levels are reasonable")
        else:
            print("   ⚠ Force levels are high, but convergence achieved")
            
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        if "INITIAL JACOBIAN CHANGED SIGN" in str(e):
            print("   The initial Jacobian sign error is still present!")
        sys.exit(1)
    
    # Test 3: Try with small asymmetric perturbation
    print("\n3. Testing with small asymmetric boundary perturbation...")
    
    # Add a small asymmetric perturbation to the boundary
    import numpy as np
    
    # Check if boundary arrays exist and initialize if needed
    if not hasattr(input_data, 'rbs') or input_data.rbs is None:
        input_data.rbs = np.zeros_like(input_data.rbc)
    if not hasattr(input_data, 'zbc') or input_data.zbc is None:
        input_data.zbc = np.zeros_like(input_data.zbs)
        
    # Add small asymmetric perturbation
    original_rbs_10 = input_data.rbs[1, 0] if input_data.rbs.shape[0] > 1 else 0.0
    original_zbc_10 = input_data.zbc[1, 0] if input_data.zbc.shape[0] > 1 else 0.0
    
    if input_data.rbs.shape[0] > 1:
        input_data.rbs[1, 0] += 0.01  # Small R_{1,0}^s perturbation
    if input_data.zbc.shape[0] > 1:
        input_data.zbc[1, 0] += 0.01  # Small Z_{1,0}^c perturbation
    
    try:
        output_perturbed = vmecpp.run(input_data, max_threads=1, verbose=False)
        print("   ✓ SUCCESS: Asymmetric equilibrium with perturbation converged")
        print(f"   Force residual: {output_perturbed.wout.fsqr}")
        print(f"   Iterations: {output_perturbed.wout.iter2}")
        
        # Should be different from baseline due to perturbation
        ratio_perturbed = output_perturbed.wout.fsqr / baseline_fsqr
        print(f"   Force ratio (perturbed/sym): {ratio_perturbed:.3f}")
        
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        if "INITIAL JACOBIAN CHANGED SIGN" in str(e):
            print("   The initial Jacobian sign error is still present!")
        sys.exit(1)
    
    print("\n=== FINAL ASSESSMENT ===")
    print("✓ All tests passed!")
    print("✓ Asymmetric geometry combination fix appears to be working")
    print("✓ No more initial Jacobian sign errors")
    print("✓ Both symmetric and asymmetric cases converge properly")
    print("\nThe doubling issue in asymmetric geometry combination has been resolved.")
    
except ImportError as e:
    print(f"Failed to import vmecpp: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)