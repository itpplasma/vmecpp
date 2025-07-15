#!/usr/bin/env python3
"""Simple test to debug asymmetric issue."""

import vmecpp
from pathlib import Path

# Test HELIOTRON_asym
print("Testing HELIOTRON_asym...")
try:
    input_file = Path("/home/ert/code/vmecpp/examples/data/HELIOTRON_asym.json")
    vmec_input = vmecpp.VmecInput.from_file(input_file)
    vmec_input.return_outputs_even_if_not_converged = True
    
    # Reduce iterations to see if it crashes early
    vmec_input.niter_array = [10, 10]
    
    print(f"lasym = {vmec_input.lasym}")
    print(f"nfp = {vmec_input.nfp}")
    print(f"ns_array = {vmec_input.ns_array}")
    print(f"niter_array = {vmec_input.niter_array}")
    
    print("\nRunning VMEC++ with reduced iterations...")
    output = vmecpp.run(vmec_input, verbose=True)
    print("✓ Completed without crash!")
    
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")

# Test tok_asym
print("Testing tok_asym...")
try:
    input_file = Path("/home/ert/code/vmecpp/examples/data/tok_asym.json") 
    vmec_input = vmecpp.VmecInput.from_file(input_file)
    vmec_input.return_outputs_even_if_not_converged = True
    
    # Reduce iterations 
    vmec_input.niter_array = [10, 10]
    
    print(f"lasym = {vmec_input.lasym}")
    print(f"nfp = {vmec_input.nfp}")
    print(f"ns_array = {vmec_input.ns_array}")
    print(f"niter_array = {vmec_input.niter_array}")
    
    print("\nRunning VMEC++ with reduced iterations...")
    output = vmecpp.run(vmec_input, verbose=True)
    print("✓ Completed without crash!")
    
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()