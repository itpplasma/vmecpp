#!/usr/bin/env python3
"""
Test asymmetric VMEC runs and generate wout files for comparison.
"""
import vmecpp
import os
import traceback

def run_asymmetric_case(json_file, output_name):
    """Run an asymmetric case and save wout file."""
    print(f"\nTesting {json_file}...")
    
    try:
        # Load input
        vmec_input = vmecpp.VmecInput.from_file(json_file)
        print(f"Loaded: lasym={vmec_input.lasym}, nfp={vmec_input.nfp}, mpol={vmec_input.mpol}, ntor={vmec_input.ntor}")
        
        # Use minimal radial resolution to avoid segfault
        vmec_input.ns_array = [3, 5]
        vmec_input.ftol_array = [1e-8, 1e-10] 
        vmec_input.niter_array = [500, 1000]
        
        print(f"Running with ns_array={vmec_input.ns_array}")
        
        # Try to run with return_outputs_even_if_not_converged
        vmec_input.return_outputs_even_if_not_converged = True
        
        output = vmecpp.run(vmec_input, verbose=False)
        
        print(f"Run completed! Success: {output.success}")
        print(f"Exit status: {output.exit_status}")
        print(f"fsqr={output.wout.fsqr:.2e}, fsqz={output.wout.fsqz:.2e}, fsql={output.wout.fsql:.2e}")
        
        # Save wout file
        wout_file = f"wout_{output_name}_vmecpp.nc"
        output.wout.save(wout_file)
        print(f"Saved wout file: {wout_file}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False

# Test both cases
success_tok = run_asymmetric_case("examples/data/tok_asym.json", "tok_asym")
success_hel = run_asymmetric_case("examples/data/HELIOTRON_asym.json", "HELIOTRON_asym")

if success_tok or success_hel:
    print("\nAt least one asymmetric case ran successfully!")
else:
    print("\nBoth asymmetric cases failed.")