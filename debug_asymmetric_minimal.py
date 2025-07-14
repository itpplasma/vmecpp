#!/usr/bin/env python3
"""
Minimal test to isolate asymmetric segmentation fault
"""
import vmecpp
import signal
import sys

def signal_handler(sig, frame):
    print(f"Received signal {sig}")
    sys.exit(1)

signal.signal(signal.SIGSEGV, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)

try:
    print("Loading asymmetric input...")
    input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"Input loaded successfully: lasym={input_data.lasym}")
    
    # Use absolutely minimal settings to reduce execution time
    input_data.ns_array = [3]
    input_data.niter_array = [2]  # Just 2 iterations
    input_data.ftol_array = [1e-3]
    
    print("Starting minimal VMEC run...")
    print("Input parameters:")
    print(f"  mpol={input_data.mpol}, ntor={input_data.ntor}")
    print(f"  ns_array={input_data.ns_array}")
    print(f"  niter_array={input_data.niter_array}")
    
    # Try to run with minimal iterations
    output = vmecpp.run(input_data, verbose=True)
    print("SUCCESS: Asymmetric run completed!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()