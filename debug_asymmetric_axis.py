#!/usr/bin/env python3
"""
Debug script to isolate the asymmetric axis recomputation issue.
Compares intermediate quantities between tokamak asymmetric case and 
symmetric case to identify where the problem occurs.
"""

import vmecpp
import numpy as np
import sys
import os

def analyze_asymmetric_case():
    """Analyze the tokamak asymmetric case that's failing"""
    
    print("=== Analyzing Asymmetric Tokamak Case ===")
    
    # Load the failing asymmetric case
    indata_file = "/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/input.tok_asym"
    
    if not os.path.exists(indata_file):
        print(f"Error: Input file {indata_file} not found")
        return
    
    try:
        # Create input from INDATA file using the file format
        vmec_input = vmecpp.VmecInput.from_file(indata_file)
        
        print(f"Input parameters:")
        print(f"  lasym: {vmec_input.lasym}")
        print(f"  nfp: {vmec_input.nfp}")
        print(f"  mpol: {vmec_input.mpol}")
        print(f"  ntor: {vmec_input.ntor}")
        print(f"  ns_array: {vmec_input.ns_array}")
        
        # Print axis coefficients
        print(f"\nAxis coefficients:")
        print(f"  raxis_c: {vmec_input.raxis_c}")
        print(f"  zaxis_s: {vmec_input.zaxis_s}")
        if vmec_input.lasym:
            print(f"  raxis_s: {vmec_input.raxis_s}")
            print(f"  zaxis_c: {vmec_input.zaxis_c}")
        
        # Print some boundary coefficients
        print(f"\nBoundary coefficients (first few):")
        for m in range(min(3, len(vmec_input.rbc))):
            for n in range(min(3, len(vmec_input.rbc[m]))):
                if vmec_input.rbc[m][n] != 0.0:
                    print(f"  rbc[{m},{n}] = {vmec_input.rbc[m][n]}")
                if vmec_input.zbs[m][n] != 0.0:
                    print(f"  zbs[{m},{n}] = {vmec_input.zbs[m][n]}")
                if vmec_input.lasym:
                    if vmec_input.rbs[m][n] != 0.0:
                        print(f"  rbs[{m},{n}] = {vmec_input.rbs[m][n]}")
                    if vmec_input.zbc[m][n] != 0.0:
                        print(f"  zbc[{m},{n}] = {vmec_input.zbc[m][n]}")
        
        # Try to run VMEC++ with verbose output
        print(f"\nAttempting VMEC++ run...")
        try:
            output = vmecpp.run(vmec_input, verbose=True)
            print("SUCCESS: VMEC++ converged!")
            
        except Exception as e:
            print(f"FAILED: {e}")
            
            # Check if this is the jacobian sign error we expect
            if "INITIAL JACOBIAN CHANGED SIGN" in str(e):
                print("Confirmed: This is the jacobian sign error we're investigating")
            else:
                print("Unexpected error type")
            
    except Exception as e:
        print(f"Error loading input: {e}")
        return

def compare_with_symmetric():
    """Compare with a symmetric case that works"""
    
    print("\n=== Comparing with Symmetric Case ===")
    
    # Load a working symmetric case
    symmetric_file = "/home/ert/code/vmecpp/examples/data/input.w7x"
    
    if not os.path.exists(symmetric_file):
        print(f"Symmetric test file {symmetric_file} not found")
        return
    
    try:
        symmetric_input = vmecpp.VmecInput.from_file(symmetric_file)
        
        print(f"Symmetric input parameters:")
        print(f"  lasym: {symmetric_input.lasym}")
        print(f"  raxis_c: {symmetric_input.raxis_c}")
        print(f"  zaxis_s: {symmetric_input.zaxis_s}")
        
        print(f"\nAttempting symmetric VMEC++ run...")
        output = vmecpp.run(symmetric_input, verbose=True)
        print("SUCCESS: Symmetric case converged!")
        
    except Exception as e:
        print(f"FAILED: {e}")
        
        # If even symmetric case fails, there's a deeper issue
        if "INITIAL JACOBIAN CHANGED SIGN" in str(e):
            print("WARNING: Even symmetric case has jacobian sign issues")
        else:
            print("Different error in symmetric case")

if __name__ == "__main__":
    analyze_asymmetric_case()
    compare_with_symmetric()