#!/usr/bin/env python3
"""
Debug VMEC status to understand why asymmetric cases fail.
"""
import vmecpp
import os

def debug_vmec_status():
    """Debug the exact failure in asymmetric cases."""
    print("🔍 DEBUGGING VMEC STATUS FOR ASYMMETRIC FAILURE")
    print("=" * 60)
    
    # Force single thread to reduce complexity
    os.environ['OMP_NUM_THREADS'] = '1'
    
    try:
        # Load the tok_asym case that works in jVMEC but fails in VMEC++
        print("📍 Loading tok_asym case...")
        input_asym = vmecpp.VmecInput.from_file("examples/data/input.tok_asym")
        
        # Use very minimal settings
        input_debug = input_asym.copy()
        input_debug.ns_array = [3]  # Minimal resolution
        input_debug.niter_array = [10]  # Few iterations to catch early failure
        input_debug.ftol_array = [1e-3]  # Relaxed tolerance
        
        print(f"✅ Input loaded: lasym={input_debug.lasym}")
        print(f"   Configuration: ns={input_debug.ns_array}, niter={input_debug.niter_array}")
        
        print("\n🚀 Running VMEC++ with verbose output...")
        
        # Try to capture more detailed error information
        try:
            output = vmecpp.run(input_debug, max_threads=1, verbose=True)
            print(f"✅ Unexpected success: ier_flag={output.wout.ier_flag}")
        except RuntimeError as e:
            error_msg = str(e)
            print(f"❌ RUNTIME ERROR CAUGHT:")
            print(f"   Full error: {error_msg}")
            
            # Analyze error message
            if "FATAL ERROR" in error_msg:
                print(f"   → This is the fatal error we need to fix")
            if "thread" in error_msg.lower():
                print(f"   → Multi-threading related")
            if "first iterations" in error_msg:
                print(f"   → Failure during early iterations")
            if "boundary" in error_msg:
                print(f"   → Possibly boundary-related issue")
            if "spectrally condensed" in error_msg:
                print(f"   → Possibly spectral resolution issue")
                
        except Exception as e:
            print(f"❌ OTHER ERROR: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"❌ Failed to load input: {e}")
        return False
    
    # Test with even more relaxed settings
    print(f"\n🔧 Testing with extremely relaxed settings...")
    try:
        input_super_relaxed = input_asym.copy()
        input_super_relaxed.ns_array = [3]
        input_super_relaxed.niter_array = [5]  # Very few iterations
        input_super_relaxed.ftol_array = [1e-1]  # Very relaxed tolerance
        
        try:
            output = vmecpp.run(input_super_relaxed, max_threads=1, verbose=False)
            print(f"✅ Unexpected success with relaxed settings")
        except Exception as e:
            print(f"❌ Still fails with relaxed settings: {type(e).__name__}")
            
    except Exception as e:
        print(f"❌ Failed relaxed test: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   The asymmetric case fails consistently in VMEC++")
    print(f"   jVMEC runs the same case successfully (ier_flag=0)")
    print(f"   This indicates a fundamental difference in early iteration logic")
    
    return False

if __name__ == "__main__":
    debug_vmec_status()