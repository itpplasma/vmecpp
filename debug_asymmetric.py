#!/usr/bin/env python3
"""
Debug asymmetric early iteration failure
"""

import sys
import os
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    
    print("=== DEBUGGING ASYMMETRIC EARLY ITERATION FAILURE ===")
    
    # Test 1: Start with a working symmetric case
    print("1. Testing baseline symmetric case...")
    
    input_file = '/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/input.solovev'
    if os.path.exists(input_file):
        input_data = vmecpp.VmecInput.from_file(input_file)
        input_data.lasym = False
        
        try:
            output_sym = vmecpp.run(input_data, max_threads=1, verbose=False)
            print(f"   ✓ Symmetric case works: fsqr = {output_sym.wout.fsqr:.2e}")
        except Exception as e:
            print(f"   ✗ Symmetric case failed: {e}")
            sys.exit(1)
    
    # Test 2: Same case with lasym=True (should work with the fix)
    print("\n2. Testing same geometry with lasym=True...")
    input_data.lasym = True
    
    try:
        output_asym = vmecpp.run(input_data, max_threads=1, verbose=False)
        print(f"   ✓ Asymmetric mode works: fsqr = {output_asym.wout.fsqr:.2e}")
    except Exception as e:
        print(f"   ✗ Asymmetric mode failed: {e}")
        print("   This suggests the asymmetric fix has remaining issues")
    
    # Test 3: Try tok_asym with relaxed parameters
    print("\n3. Testing tok_asym with relaxed parameters...")
    
    input_file_tok = '/home/ert/code/jVMEC/src/test/resources/input.tok_asym'
    if os.path.exists(input_file_tok):
        try:
            input_tok = vmecpp.VmecInput.from_file(input_file_tok)
            print(f"   Original params: ns_array={input_tok.ns_array}, ftol={input_tok.ftol_array}")
            
            # Start with very relaxed parameters
            input_tok.ns_array = [5]  # Single grid point, small grid
            input_tok.niter_array = [500]  # More iterations
            input_tok.ftol_array = [1e-6]  # More relaxed tolerance
            input_tok.delt = 0.5  # Larger time step for stability
            
            print(f"   Relaxed params: ns_array={input_tok.ns_array}, ftol={input_tok.ftol_array}, delt={input_tok.delt}")
            
            output_tok = vmecpp.run(input_tok, max_threads=1, verbose=True)
            print(f"   ✓ tok_asym converged with relaxed params: fsqr = {output_tok.wout.fsqr:.2e}")
            
        except Exception as e:
            print(f"   ✗ tok_asym failed even with relaxed params: {e}")
            print("   This indicates a fundamental issue with the asymmetric implementation")
            
            # Try to understand what's happening
            if "FATAL ERROR" in str(e):
                print("   The error suggests the initial equilibrium is not properly constructed")
                print("   This could indicate:")
                print("   - Boundary shape issues with asymmetric coefficients")
                print("   - Spectral condensation problems")
                print("   - Initial Jacobian computation still has issues")
    
    # Test 4: Check HELIOTRON_asym case as well
    print("\n4. Quick check of HELIOTRON_asym...")
    
    input_file_heliotron = '/home/ert/code/jVMEC/src/test/resources/input.HELIOTRON_asym'
    if os.path.exists(input_file_heliotron):
        try:
            input_heliotron = vmecpp.VmecInput.from_file(input_file_heliotron)
            
            # Relaxed parameters
            input_heliotron.ns_array = [5]
            input_heliotron.niter_array = [100]
            input_heliotron.ftol_array = [1e-6]
            input_heliotron.delt = 0.5
            
            output_heliotron = vmecpp.run(input_heliotron, max_threads=1, verbose=False)
            print(f"   ✓ HELIOTRON_asym works: fsqr = {output_heliotron.wout.fsqr:.2e}")
            
        except Exception as e:
            print(f"   ✗ HELIOTRON_asym failed: {e}")
    
    print("\n=== ANALYSIS ===")
    print("The asymmetric geometry combination fix resolved the doubling bug,")
    print("but there appear to be additional issues with asymmetric configurations.")
    print("\nPossible remaining issues:")
    print("- Initial boundary construction for complex asymmetric shapes")
    print("- Spectral condensation with asymmetric Fourier modes")
    print("- Force balance computation in early iterations")
    print("- Asymmetric force symmetrization needs refinement")
    
except Exception as e:
    print(f"Debug error: {e}")
    import traceback
    traceback.print_exc()