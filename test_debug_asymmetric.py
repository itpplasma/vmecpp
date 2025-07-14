#!/usr/bin/env python3
"""
Debug script for asymmetric execution
"""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'build'))

try:
    import _vmecpp
    print("C++ binding imported successfully")
    
    import vmecpp
    print("Python wrapper imported successfully")
    
    # Test asymmetric input loading
    print("Loading asymmetric input...")
    input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Input loaded: lasym={input.lasym}")
    print(f"Original settings: ns_array={input.ns_array}, niter_array={input.niter_array}")
    
    # Use minimal settings
    input.ns_array = [3]
    input.niter_array = [1]
    input.ftol_array = [1e-3]
    
    print("Starting VMEC run with minimal settings...")
    try:
        output = vmecpp.run(input, verbose=True)
        print("SUCCESS: Asymmetric run completed!")
        print(f"Converged: {output.success}")
    except Exception as e:
        print(f"ERROR during VMEC run: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"ERROR during import/setup: {e}")
    import traceback
    traceback.print_exc()