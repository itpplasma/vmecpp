#!/usr/bin/env python3
import vmecpp

# Create a simple test for tok_asym just input loading
try:
    print("Loading tok_asym input...")
    input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"✅ Input loaded: lasym={input_data.lasym}, nfp={input_data.nfp}")
    
    # Test just initialization
    print("Testing minimal run...")
    input_data.niter_array = [1]
    input_data.ftol_array = [1e-6]
    
    output = vmecpp.run(input_data, verbose=False)
    print("✅ SUCCESS!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()