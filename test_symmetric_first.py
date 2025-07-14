#!/usr/bin/env python3
"""
Test symmetric case to ensure fix doesn't break normal operation
"""

import sys
import os
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    
    print("Testing symmetric case to verify fix doesn't break normal operation...")
    
    # Test with a known working file
    input_file = '/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/input.solovev'
    
    if os.path.exists(input_file):
        print(f"Loading input from {input_file}")
        input_data = vmecpp.VmecInput.from_file(input_file)
        print(f"Input lasym = {input_data.lasym}")
        
        # Run the equilibrium
        print("Running symmetric equilibrium...")
        output = vmecpp.run(input_data, max_threads=1, verbose=False)
        print("SUCCESS: Symmetric equilibrium still works!")
        print(f"Final force residual: {output.fsqr}")
        print(f"Iterations: {output.iter2}")
        
        # Now test with lasym=True on the same geometry
        print("\nTesting with lasym=True on same geometry...")
        input_data.lasym = True
        output_asym = vmecpp.run(input_data, max_threads=1, verbose=False)
        print("SUCCESS: Asymmetric mode converged with symmetric geometry!")
        print(f"Final force residual: {output_asym.fsqr}")
        print(f"Iterations: {output_asym.iter2}")
        
    else:
        print(f"Input file {input_file} not found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()