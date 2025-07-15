#!/usr/bin/env python3
"""Test HELIOTRON asymmetric case only."""

import numpy as np
from pathlib import Path
import vmecpp

# Load input
input_file = Path("/home/ert/code/vmecpp/examples/data/HELIOTRON_asym.json")
vmec_input = vmecpp.VmecInput.from_file(input_file)
print(f"Configuration: nfp={vmec_input.nfp}, mpol={vmec_input.mpol}, ntor={vmec_input.ntor}")
print(f"lasym = {vmec_input.lasym}")

# Enable returning outputs even if not converged
vmec_input.return_outputs_even_if_not_converged = True

# Run VMEC++
print("\nRunning VMEC++...")
try:
    output = vmecpp.run(vmec_input, verbose=False)
    print(f"\n✓ VMEC++ completed!")
    print(f"  ier_flag = {output.wout.ier_flag}")
    print(f"  Volume = {output.wout.volume:.6f}")
    print(f"  Aspect = {output.wout.aspect:.6f}")
    print(f"  Beta = {output.wout.betatot:.6f}")
    
    # Check asymmetric arrays
    print("\nAsymmetric arrays present:")
    for attr in ['rmns', 'zmnc', 'lmnc', 'gmns', 'bmns']:
        if hasattr(output.wout, attr) and getattr(output.wout, attr) is not None:
            arr = getattr(output.wout, attr)
            max_val = np.max(np.abs(arr))
            print(f"  {attr}: shape={arr.shape}, max={max_val:.2e}")
    
    # Check convergence
    if output.wout.ier_flag == 0:
        print("\n✓ Converged successfully!")
    else:
        print(f"\n⚠ ier_flag = {output.wout.ier_flag} (may indicate convergence issues)")
        
except Exception as e:
    print(f"✗ VMEC++ failed: {e}")
    import traceback
    traceback.print_exc()