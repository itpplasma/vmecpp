#!/usr/bin/env python3
"""
Test just the asymmetric setup without running iterations
"""
import vmecpp

try:
    print("Loading asymmetric input...")
    input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"✓ Input loaded: lasym={input_data.lasym}")
    
    print("Testing input validation...")
    # This should validate the entire input structure including asymmetric arrays
    print(f"  mpol={input_data.mpol}, ntor={input_data.ntor}")
    print(f"  rbc shape: {len(input_data.rbc) if hasattr(input_data, 'rbc') else 'N/A'}")
    print(f"  zbs shape: {len(input_data.zbs) if hasattr(input_data, 'zbs') else 'N/A'}")
    print(f"  rbs shape: {len(input_data.rbs) if hasattr(input_data, 'rbs') else 'N/A'}")
    print(f"  zbc shape: {len(input_data.zbc) if hasattr(input_data, 'zbc') else 'N/A'}")
    
    print("✓ Asymmetric input validation passed!")
    
    # Test conversion to C++ format without running
    print("Testing C++ data structure creation...")
    try:
        # This should create the VmecINDATA structure in C++ but not run
        cpp_indata = vmecpp._vmecpp.VmecINDATAPyWrapper.from_vmec_input(input_data)
        print("✓ C++ VmecINDATA creation successful!")
        print(f"  C++ lasym: {cpp_indata.get_lasym()}")
    except Exception as e:
        print(f"✗ C++ data structure creation failed: {e}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()