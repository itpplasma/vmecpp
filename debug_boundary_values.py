#!/usr/bin/env python3
"""
Debug script to extract and examine boundary coefficient values
during the jacobian sign check for the asymmetric tokamak case.
"""

import vmecpp
import numpy as np
import os

def debug_boundary_processing():
    """Debug the boundary processing and jacobian sign check"""
    
    # Load the failing asymmetric case
    indata_file = "/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/input.tok_asym"
    
    try:
        vmec_input = vmecpp.VmecInput.from_file(indata_file)
        print("=== Input Parameters ===")
        print(f"lasym: {vmec_input.lasym}")
        print(f"nfp: {vmec_input.nfp}")
        print(f"ntor: {vmec_input.ntor}")
        print(f"mpol: {vmec_input.mpol}")
        
        # Print raw input coefficients
        print("\n=== Raw Input Coefficients ===")
        print("rbc (first few):")
        for m in range(min(3, len(vmec_input.rbc))):
            for n in range(min(3, len(vmec_input.rbc[m]))):
                if vmec_input.rbc[m][n] != 0:
                    print(f"  rbc[{m},{n}] = {vmec_input.rbc[m][n]}")
        
        print("zbs (first few):")
        for m in range(min(3, len(vmec_input.zbs))):
            for n in range(min(3, len(vmec_input.zbs[m]))):
                if vmec_input.zbs[m][n] != 0:
                    print(f"  zbs[{m},{n}] = {vmec_input.zbs[m][n]}")
        
        if vmec_input.lasym:
            print("rbs (first few):")
            for m in range(min(3, len(vmec_input.rbs))):
                for n in range(min(3, len(vmec_input.rbs[m]))):
                    if vmec_input.rbs[m][n] != 0:
                        print(f"  rbs[{m},{n}] = {vmec_input.rbs[m][n]}")
            
            print("zbc (first few):")
            for m in range(min(3, len(vmec_input.zbc))):
                for n in range(min(3, len(vmec_input.zbc[m]))):
                    if vmec_input.zbc[m][n] != 0:
                        print(f"  zbc[{m},{n}] = {vmec_input.zbc[m][n]}")
        
        # Calculate theta shift delta manually
        print("\n=== Theta Shift Calculation ===")
        if vmec_input.lasym:
            m, n = 1, 0
            rbc = vmec_input.rbc[m][n]
            zbs = vmec_input.zbs[m][n]
            rbs = vmec_input.rbs[m][n]
            zbc = vmec_input.zbc[m][n]
            
            delta = np.arctan2(rbs - zbc, rbc + zbs)
            print(f"For m=1, n=0:")
            print(f"  rbc = {rbc}")
            print(f"  zbs = {zbs}")
            print(f"  rbs = {rbs}")
            print(f"  zbc = {zbc}")
            print(f"  delta = arctan2({rbs} - {zbc}, {rbc} + {zbs}) = {delta}")
        
        # Manually compute what rTest and zTest should be
        print("\n=== Expected rTest and zTest Values ===")
        
        # For this case, we need to simulate the boundary processing
        # This is complex, so let's at least show what we expect
        print("After processing (theta shift, m=1 constraint):")
        print("rTest should be sum of rbcc[m=1, n=0 to ntor] coefficients")
        print("zTest should be sum of zbsc[m=1, n=0 to ntor] coefficients")
        
        # Show the flip condition
        print("\n=== Flip Condition ===")
        print("sign_of_jacobian = -1")
        print("Flip when: rTest * zTest * sign_of_jacobian > 0")
        print("Which simplifies to: rTest * zTest < 0")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_boundary_processing()