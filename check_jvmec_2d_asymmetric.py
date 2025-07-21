#!/usr/bin/env python3
"""Check how jVMEC handles 2D asymmetric equilibria."""

import subprocess
import os

def check_jvmec_2d_asymmetric():
    print("=== CHECKING jVMEC 2D ASYMMETRIC HANDLING ===\n")
    
    # Create a test input file for 2D asymmetric
    test_input = """&INDATA
  LASYM = T
  NFP = 1
  MPOL = 5
  NTOR = 0
  NS_ARRAY = 17
  NITER_ARRAY = 50
  FTOL_ARRAY = 1.0E-8
  
  PHIEDGE = 6.0
  
  RBC(0,0) = 6.0
  RBC(1,0) = 0.6
  
  ! Asymmetric boundary coefficients
  RBS(1,0) = 0.6
  RBS(2,0) = 0.12
  ZBS(1,0) = 0.6
  
  AM = 0.0
  AI = 0.9, -0.65
  
  RAXIS = 6.0
  ZAXIS = 0.0
  
  BLOAT = 1.0
  DELT = 0.9
  TCON0 = 1.0
  
  LFREEB = F
  MGRID_FILE = 'NONE'
  LFORBAL = F
  NVACSKIP = 3
  NSTEP = 200
/
&END
"""
    
    # Write the test input
    with open("test_2d_asymmetric.input", "w") as f:
        f.write(test_input)
    
    print("Test configuration:")
    print("  NTOR = 0 (2D/axisymmetric)")
    print("  LASYM = T (asymmetric)")
    print("  RBS(1,0) = 0.6")
    print("  RBS(2,0) = 0.12")
    print("  ZBS(1,0) = 0.6")
    
    # Run jVMEC with verbose output
    try:
        cmd = ["java", "-cp", "jVMEC-1.0.0.jar", "de.labathome.jvmec.VmecMain", "test_2d_asymmetric.input"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("\n--- jVMEC Output ---")
        
        # Look for key information in output
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            # Check if lthreed is mentioned
            if 'lthreed' in line.lower():
                print(f"lthreed info: {line}")
            
            # Check for asymmetric coefficient handling
            if 'rbs' in line.lower() or 'zbs' in line.lower() or 'rmns' in line.lower():
                print(f"Asymmetric coeff: {line}")
                
            # Check for errors or warnings
            if 'error' in line.lower() or 'warning' in line.lower():
                print(f"Issue: {line}")
                
            # Check convergence
            if 'fsq' in line.lower() or 'converged' in line.lower():
                print(f"Convergence: {line}")
        
        # Also check stderr
        if result.stderr:
            print("\n--- jVMEC Errors ---")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error running jVMEC: {e}")
    finally:
        # Clean up
        if os.path.exists("test_2d_asymmetric.input"):
            os.remove("test_2d_asymmetric.input")

if __name__ == "__main__":
    check_jvmec_2d_asymmetric()