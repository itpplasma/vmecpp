#!/usr/bin/env python3

import vmecpp
import numpy as np
import traceback

def check_for_nan_in_output(output):
    """Check all numeric fields in output for NaN values"""
    nan_fields = []
    
    # Check wout fields
    wout = output.wout
    for field_name in dir(wout):
        if field_name.startswith('_'):
            continue
        try:
            field_value = getattr(wout, field_name)
            if isinstance(field_value, (int, float)):
                if np.isnan(field_value):
                    nan_fields.append(f"wout.{field_name}")
            elif hasattr(field_value, '__iter__') and not isinstance(field_value, str):
                arr = np.array(field_value)
                if arr.dtype.kind in 'fc' and np.any(np.isnan(arr)):
                    nan_fields.append(f"wout.{field_name}")
        except:
            pass
    
    return nan_fields

def test_asymmetric_with_nan_tracking():
    """Test asymmetric case and track where NaN appears"""
    print("🔍 TRACKING NaN IN ASYMMETRIC EXECUTION")
    print("=" * 60)
    
    # Load minimal asymmetric input
    input_data = vmecpp.VmecInput.from_file("examples/data/input.tok_asym")
    
    # Even simpler parameters - single iteration
    input_data.ns_array = [3]
    input_data.niter_array = [1]  # Just one iteration
    input_data.ftol_array = [10.0]  # Very loose tolerance
    
    print(f"✓ Setup minimal asymmetric test:")
    print(f"  lasym={input_data.lasym}")
    print(f"  ns_array={input_data.ns_array}")
    print(f"  niter_array={input_data.niter_array}")
    
    # Check input arrays
    print(f"\n📊 INPUT BOUNDARY COEFFICIENTS:")
    rbc_arr = np.array(input_data.rbc).reshape(input_data.mpol, 2*input_data.ntor+1)
    zbs_arr = np.array(input_data.zbs).reshape(input_data.mpol, 2*input_data.ntor+1)
    rbs_arr = np.array(input_data.rbs).reshape(input_data.mpol, 2*input_data.ntor+1)
    zbc_arr = np.array(input_data.zbc).reshape(input_data.mpol, 2*input_data.ntor+1)
    
    print(f"  rbc has NaN: {np.any(np.isnan(rbc_arr))}")
    print(f"  zbs has NaN: {np.any(np.isnan(zbs_arr))}")
    print(f"  rbs has NaN: {np.any(np.isnan(rbs_arr))}")
    print(f"  zbc has NaN: {np.any(np.isnan(zbc_arr))}")
    
    # Check non-zero modes
    print(f"\n  Non-zero symmetric modes:")
    for m in range(input_data.mpol):
        for n in range(2*input_data.ntor+1):
            if rbc_arr[m,n] != 0:
                print(f"    rbc[{m},{n}] = {rbc_arr[m,n]}")
            if zbs_arr[m,n] != 0:
                print(f"    zbs[{m},{n}] = {zbs_arr[m,n]}")
    
    print(f"\n  Non-zero asymmetric modes:")
    for m in range(input_data.mpol):
        for n in range(2*input_data.ntor+1):
            if rbs_arr[m,n] != 0:
                print(f"    rbs[{m},{n}] = {rbs_arr[m,n]}")
            if zbc_arr[m,n] != 0:
                print(f"    zbc[{m},{n}] = {zbc_arr[m,n]}")
    
    try:
        print(f"\n🚀 Running asymmetric VMEC...")
        output = vmecpp.run(input_data)
        
        # Check for NaN in output
        nan_fields = check_for_nan_in_output(output)
        
        if nan_fields:
            print(f"\n❌ Found NaN in output fields:")
            for field in nan_fields:
                print(f"   - {field}")
        else:
            print(f"\n✅ No NaN found in output!")
            print(f"   fsqr: {output.wout.fsqr}")
            print(f"   fsqz: {output.wout.fsqz}")
            print(f"   fsql: {output.wout.fsql}")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_asymmetric_with_nan_tracking()