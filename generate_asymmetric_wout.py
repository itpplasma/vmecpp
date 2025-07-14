#!/usr/bin/env python3
"""
Generate asymmetric wout files using pytest framework.
"""
import vmecpp
import os
import subprocess
import sys

# Run the asymmetric tests with pytest and save wout files
test_cmd = [
    sys.executable, "-m", "pytest", 
    "tests/test_vmec_runs.py::test_asymmetric_cases",
    "-v", "-s"
]

print("Running asymmetric tests via pytest...")
result = subprocess.run(test_cmd, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)

# Now try to generate wout files directly with minimal settings
print("\n\nAttempting direct run with minimal settings...")

for json_file, name in [
    ("examples/data/tok_asym.json", "tok_asym"),
    ("examples/data/HELIOTRON_asym.json", "HELIOTRON_asym")
]:
    print(f"\nProcessing {json_file}...")
    try:
        vmec_input = vmecpp.VmecInput.from_file(json_file)
        
        # Use absolute minimal settings
        vmec_input.ns_array = [3]
        vmec_input.ftol_array = [1e-6]
        vmec_input.niter_array = [10]
        vmec_input.nstep = 10
        vmec_input.return_outputs_even_if_not_converged = True
        
        print(f"  Running with ns={vmec_input.ns_array[0]}, niter={vmec_input.niter_array[0]}")
        
        output = vmecpp.run(vmec_input, verbose=False)
        
        wout_file = f"wout_{name}_vmecpp.nc"
        output.wout.save(wout_file)
        print(f"  Saved: {wout_file}")
        
    except Exception as e:
        print(f"  ERROR: {e}")