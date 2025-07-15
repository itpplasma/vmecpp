#!/usr/bin/env python3
"""Debug script to understand the axis recomputation issue in asymmetric cases."""

import vmecpp.simsopt_compat as simsopt_compat
import numpy as np
from pathlib import Path

TEST_DATA_DIR = Path("/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data")

def test_axis_recomputation():
    """Test axis recomputation for tok_asym case."""
    
    input_file = TEST_DATA_DIR / "input.tok_asym"
    
    print("Testing axis recomputation for tok_asym...")
    print(f"Input file: {input_file}")
    
    # Try to run with minimal output
    try:
        vmec = simsopt_compat.Vmec(str(input_file))
        
        # Check initial boundary setup
        print(f"Initial setup:")
        print(f"  nfp = {vmec.indata.nfp}")
        print(f"  lasym = {vmec.indata.lasym}")
        print(f"  lthreed = {vmec.indata.lthreed}")
        print(f"  mpol = {vmec.indata.mpol}")
        print(f"  ntor = {vmec.indata.ntor}")
        print(f"  nzeta = {vmec.indata.nzeta}")
        print(f"  ntheta = {vmec.indata.ntheta}")
        
        # Check boundary coefficients
        print(f"  raxis_cc = {vmec.indata.raxis_cc}")
        print(f"  zaxis_cc = {vmec.indata.zaxis_cc}")
        
        # Print some boundary coefficients
        print(f"  rbc(0,0) = {vmec.indata.rbc[0, 0]}")
        if vmec.indata.rbc.shape[1] > 1:
            print(f"  rbc(0,1) = {vmec.indata.rbc[0, 1]}")
        if vmec.indata.zbs.shape[1] > 1:
            print(f"  zbs(0,1) = {vmec.indata.zbs[0, 1]}")
        
        # Try to run
        vmec.run()
        
    except Exception as e:
        print(f"Error during run: {e}")
        import traceback
        traceback.print_exc()
        
        # The error should be related to jacobian sign
        error_str = str(e)
        if "INITIAL JACOBIAN CHANGED SIGN" in error_str:
            print("\nDetected jacobian sign issue!")
            print("This suggests the axis recomputation is failing.")
            
        return False
    
    return True

if __name__ == "__main__":
    test_axis_recomputation()