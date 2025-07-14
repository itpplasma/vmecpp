#!/usr/bin/env python3
"""Simple test to check if asymmetric implementation is working"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import vmecpp
    print("VMECPP import successful")
    
    # Test if we can create an asymmetric input
    print("Testing input creation...")
    
    # Create a minimal asymmetric input
    input_data = {
        'mgrid_file': 'none',
        'lfreeb': False,
        'delt': 0.9,
        'tcon0': 1.0,
        'lasym': True,
        'nfp': 1,
        'ncurr': 0,
        'mpol': 3,
        'ntor': 2,
        'ntheta': 20,
        'nzeta': 12,
        'ns_array': [5],
        'niter_array': [10],
        'ftol_array': [1e-10],
        'nstep': 20,
        'nvacskip': 6,
        'gamma': 0,
        'phiedge': 1.0,
        'bloat': 1,
        'curtor': 0,
        'spres_ped': 1,
        'pres_scale': 1,
        'pmass_type': 'power_series',
        'am': [0],
        'am_aux_s': [0],
        'am_aux_f': [0],
        'ai': [0],
        'ai_aux_s': [0],
        'ai_aux_f': [0],
        'ac': [0],
        'ac_aux_s': [0],
        'ac_aux_f': [0],
        'piota_type': 'power_series',
        'pcurr_type': 'power_series',
        'extcur': [0],
        'aphi': [0],
        'lforbal': True,
        'raxis_c': [6.0],
        'zaxis_s': [0.0],
        'rbc': [[6.0, 0.0], [0.5, 0.0], [0.0, 0.0]],
        'zbs': [[0.0, 0.0], [0.5, 0.0], [0.0, 0.0]],
        'rbs': [[0.0, 0.0], [0.01, 0.0], [0.0, 0.0]],  # Small asymmetric perturbation
        'zbc': [[0.0, 0.0], [0.01, 0.0], [0.0, 0.0]],  # Small asymmetric perturbation
        'raxis_s': [0.0],
        'zaxis_c': [0.0]
    }
    
    inp = vmecpp.VmecInput(**input_data)
    print(f"Input created successfully: lasym={inp.lasym}")
    
    # Try a very short run
    print("Testing short run...")
    try:
        result = vmecpp.run(inp, max_threads=1, verbose=False)
        print(f"SUCCESS: Run completed with {result.iter2} iterations")
        print(f"Final residual: {result.fsqr:.2e}")
        print("✓ Asymmetric implementation is working!")
    except Exception as e:
        print(f"Run failed: {e}")
        
        if "INITIAL JACOBIAN" in str(e):
            print("Status: Still failing at initial Jacobian check")
            print("The force symmetrization fix was implemented but more work is needed")
        else:
            print("Status: Different error - may indicate progress")
            
        print("✗ Asymmetric implementation needs more work")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()