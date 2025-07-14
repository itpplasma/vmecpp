#!/usr/bin/env python3
"""
Debug asymmetric execution with iteration-level monitoring
"""
import vmecpp
import time
import signal
import sys

def timeout_handler(signum, frame):
    print("TIMEOUT: Execution took too long, killing process")
    sys.exit(1)

def test_asymmetric_iteration():
    try:
        print("Loading asymmetric input...")
        input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
        print(f"✓ Input loaded: lasym={input_data.lasym}")
        
        # Use very minimal settings for quick execution
        input_data.ns_array = [3, 5]  # Very small grid
        input_data.niter_array = [5, 10]  # Very few iterations
        input_data.ftol_array = [1e-2, 1e-3]  # Relaxed tolerance
        
        print(f"Test parameters:")
        print(f"  mpol={input_data.mpol}, ntor={input_data.ntor}")
        print(f"  ns_array={input_data.ns_array}")
        print(f"  niter_array={input_data.niter_array}")
        print(f"  ftol_array={input_data.ftol_array}")
        
        # Set a timeout to prevent hanging
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout
        
        print("\nStarting asymmetric VMEC run...")
        start_time = time.time()
        
        try:
            output = vmecpp.run(input_data, verbose=True)
            end_time = time.time()
            
            signal.alarm(0)  # Cancel timeout
            print(f"\n✓ SUCCESS: Asymmetric run completed in {end_time - start_time:.2f} seconds!")
            print(f"  Converged: {output.success}")
            print(f"  Final iteration: {output.wout.ier_flag}")
            
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            end_time = time.time()
            print(f"\n✗ EXECUTION FAILED after {end_time - start_time:.2f} seconds: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"✗ SETUP FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_asymmetric_iteration()