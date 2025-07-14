#!/usr/bin/env python3

import vmecpp
import numpy as np
import traceback

def investigate_nan_asymmetric():
    """
    Investigate why asymmetric execution produces NaN values
    """
    print("🔍 INVESTIGATING NaN VALUES IN ASYMMETRIC EXECUTION")
    print("=" * 60)
    
    # Load minimal asymmetric input
    input_data = vmecpp.VmecInput.from_file("examples/data/input.tok_asym")
    print(f"✓ Loaded asymmetric input: lasym={input_data.lasym}")
    print(f"  Parameters: mpol={input_data.mpol}, ntor={input_data.ntor}")
    print(f"  ns_array: {input_data.ns_array}")
    print(f"  niter_array: {input_data.niter_array}")
    print(f"  ftol_array: {input_data.ftol_array}")
    
    # Check boundary coefficients
    print(f"\n📊 BOUNDARY COEFFICIENTS:")
    print(f"  rbc shape: {np.array(input_data.rbc).shape}")
    print(f"  zbs shape: {np.array(input_data.zbs).shape}")
    print(f"  rbs shape: {np.array(input_data.rbs).shape}")
    print(f"  zbc shape: {np.array(input_data.zbc).shape}")
    
    # Check for non-zero asymmetric coefficients
    rbs_array = np.array(input_data.rbs).reshape(input_data.mpol, 2*input_data.ntor+1)
    zbc_array = np.array(input_data.zbc).reshape(input_data.mpol, 2*input_data.ntor+1)
    
    print(f"  rbs non-zero count: {np.count_nonzero(rbs_array)}")
    print(f"  zbc non-zero count: {np.count_nonzero(zbc_array)}")
    
    if np.count_nonzero(rbs_array) == 0 and np.count_nonzero(zbc_array) == 0:
        print("  ⚠️  WARNING: All asymmetric boundary coefficients are zero!")
        print("  This may be causing degenerate geometry leading to NaN values")
    
    # Try very simple parameters to avoid early convergence issues
    print(f"\n🧪 TESTING WITH SIMPLIFIED PARAMETERS:")
    input_data.ns_array = [3]  # Single multigrid step
    input_data.niter_array = [2]  # Just 2 iterations
    input_data.ftol_array = [1.0]  # Very loose tolerance
    
    try:
        print("\n🚀 Starting simplified asymmetric run...")
        output = vmecpp.run(input_data)
        
        if output.success:
            print("✅ SUCCESS: Asymmetric run completed!")
            print(f"   Iterations: {output.wout.iter2}")
            print(f"   Final fsqr: {output.wout.fsqr}")
            print(f"   Final fsqz: {output.wout.fsqz}")
        else:
            print("❌ FAILED: Run did not converge")
            print(f"   Error: {output.error_message}")
            
    except Exception as e:
        print(f"💥 EXCEPTION during execution:")
        print(f"   {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    investigate_nan_asymmetric()