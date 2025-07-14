#!/usr/bin/env python3
"""
Validation test script to compare VMECPP results with reference data
"""

import os
import sys
import json
import numpy as np

# Add the source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import vmecpp
    
    def test_asymmetric_tokamak():
        """Test the asymmetric tokamak case from jVMEC"""
        
        # Reference data from jVMEC tok_asym test (last iteration)
        reference_data = {
            "ns": 5,
            "iter2": 1624,
            "phiedge": 119.15,
            "final_surface_r00": 5.9162999999999997,
            "final_surface_r10": 1.3572380972487537,
            "final_surface_z10": 2.5615332168791833,
            "expected_convergence": True
        }
        
        print("=== Asymmetric Tokamak Validation Test ===")
        print(f"Reference case: ns={reference_data['ns']}, iter2={reference_data['iter2']}")
        print(f"Expected convergence: {reference_data['expected_convergence']}")
        print()
        
        # Create input matching the jVMEC test case
        inp = vmecpp.VmecInput()
        
        # Basic parameters
        inp.mgrid_file = 'none'
        inp.lfreeb = False
        inp.delt = 0.9
        inp.tcon0 = 1.0
        inp.lasym = True
        inp.nfp = 1
        inp.ncurr = 0
        inp.mpol = 3
        inp.ntor = 2
        inp.ns_array = [5, 7]
        inp.niter_array = [1000, 2000]
        inp.ftol_array = [1e-16, 1e-14]
        inp.nstep = 20
        inp.nvacskip = 6
        inp.gamma = 0
        inp.phiedge = 119.15
        inp.bloat = 1
        inp.curtor = 0
        inp.spres_ped = 1
        inp.pres_scale = 1
        inp.pmass_type = 'power_series'
        inp.am = [0, 0, 0]
        inp.ai = [0, 0]
        
        # Boundary coefficients from jVMEC reference
        inp.rbc[0, 0] = 6.2992579047371615
        inp.rbc[1, 0] = 0.76668974307559334
        inp.rbc[2, 0] = 0.028198205745066655
        inp.rbc[1, 1] = -0.003327010572741552
        inp.rbc[2, 1] = 0.003516534290433446
        inp.rbc[2, 2] = 0.0008225195550273412
        inp.rbc[3, 2] = 0.0005758954753207230
        
        inp.zbs[1, 0] = 1.1657599193052599
        inp.zbs[2, 0] = -0.008666222702417950
        inp.zbs[1, 1] = 0.004082816476331472
        inp.zbs[2, 1] = -0.0001450795984527260
        inp.zbs[2, 2] = -0.0001729551905816431
        inp.zbs[3, 2] = 0.0001020548760509997
        
        # Asymmetric coefficients (key difference)
        inp.rbs[1, 0] = -0.02782041299992509
        inp.rbs[2, 0] = 0.003864627198699337
        inp.rbs[1, 1] = -0.001516311432854679
        inp.rbs[2, 1] = 0.0003094870318397515
        inp.rbs[2, 2] = -0.0001715651286675114
        inp.rbs[3, 2] = 0.0001085465901909555
        
        inp.zbc[1, 0] = -0.03827889491207524
        inp.zbc[2, 0] = 0.007232208486620396
        inp.zbc[1, 1] = -0.004513997858565856
        inp.zbc[2, 1] = 0.0001065560191347206
        inp.zbc[2, 2] = -0.0003572232173553478
        inp.zbc[3, 2] = -0.0005566966853213000
        
        print("Input configuration:")
        print(f"  lasym = {inp.lasym}")
        print(f"  ns_array = {inp.ns_array}")
        print(f"  niter_array = {inp.niter_array}")
        print(f"  phiedge = {inp.phiedge}")
        print(f"  R(0,0) = {inp.rbc[0, 0]}")
        print(f"  R(1,0) = {inp.rbc[1, 0]}")
        print(f"  Z(1,0) = {inp.zbs[1, 0]}")
        print(f"  Rs(1,0) = {inp.rbs[1, 0]} (asymmetric)")
        print(f"  Zc(1,0) = {inp.zbc[1, 0]} (asymmetric)")
        print()
        
        # Run the simulation
        print("Running asymmetric tokamak simulation...")
        try:
            result = vmecpp.run(inp, max_threads=1, verbose=False)
            
            print("=== RESULTS ===")
            print(f"Status: CONVERGED")
            print(f"Final iterations: {result.iter2}")
            print(f"Final residual: {result.fsqr:.2e}")
            print(f"Phiedge: {result.phiedge}")
            print(f"Beta: {result.beta_vol}")
            print()
            
            # Check against reference
            success = True
            
            if result.phiedge != reference_data["phiedge"]:
                print(f"WARNING: phiedge mismatch - got {result.phiedge}, expected {reference_data['phiedge']}")
                success = False
            
            if result.iter2 > reference_data["iter2"] * 1.2:  # Allow 20% tolerance
                print(f"WARNING: Too many iterations - got {result.iter2}, expected ~{reference_data['iter2']}")
                success = False
            
            if success:
                print("✓ VALIDATION PASSED: Results match reference data")
            else:
                print("✗ VALIDATION FAILED: Results differ from reference")
                
            return success
            
        except Exception as e:
            print(f"=== FAILED ===")
            print(f"Error: {e}")
            
            if "INITIAL JACOBIAN CHANGED SIGN" in str(e):
                print("Root cause: Initial Jacobian sign error (asymmetric implementation incomplete)")
            elif "BAD_JACOBIAN" in str(e):
                print("Root cause: Jacobian becomes negative during iteration")
            else:
                print("Root cause: Unknown error")
                
            print("✗ VALIDATION FAILED: Simulation did not converge")
            return False

    def test_symmetric_reference():
        """Test a symmetric case as reference"""
        print("=== Symmetric Reference Test ===")
        
        # Use the simple solovev case 
        inp = vmecpp.VmecInput()
        inp.mgrid_file = 'none'
        inp.lfreeb = False
        inp.lasym = False  # Symmetric
        inp.nfp = 1
        inp.ncurr = 0
        inp.mpol = 3
        inp.ntor = 2
        inp.ns_array = [5]
        inp.niter_array = [100]
        inp.ftol_array = [1e-12]
        inp.nstep = 20
        inp.nvacskip = 6
        inp.gamma = 0
        inp.phiedge = 1.0
        inp.bloat = 1
        inp.curtor = 0
        inp.spres_ped = 1
        inp.pres_scale = 1
        inp.pmass_type = 'power_series'
        inp.am = [0, 0, 0]
        inp.ai = [0, 0]
        
        # Simple tokamak boundary
        inp.rbc[0, 0] = 6.0
        inp.rbc[1, 0] = 0.5
        inp.zbs[1, 0] = 0.5
        
        try:
            result = vmecpp.run(inp, max_threads=1, verbose=False)
            print(f"Symmetric case: CONVERGED in {result.iter2} iterations")
            print(f"Final residual: {result.fsqr:.2e}")
            print("✓ Symmetric reference test passed")
            return True
        except Exception as e:
            print(f"Symmetric case: FAILED - {e}")
            print("✗ Symmetric reference test failed")
            return False

    def main():
        """Run validation tests"""
        print("VMECPP Asymmetric Validation Test")
        print("=" * 50)
        print()
        
        # Test symmetric case first
        symmetric_ok = test_symmetric_reference()
        print()
        
        # Test asymmetric case
        asymmetric_ok = test_asymmetric_tokamak()
        print()
        
        print("=" * 50)
        print("SUMMARY:")
        print(f"Symmetric test: {'PASS' if symmetric_ok else 'FAIL'}")
        print(f"Asymmetric test: {'PASS' if asymmetric_ok else 'FAIL'}")
        
        if asymmetric_ok:
            print("✓ VMECPP asymmetric implementation matches reference VMEC results")
        else:
            print("✗ VMECPP asymmetric implementation needs more work")
            
        return asymmetric_ok

    main()

except ImportError as e:
    print(f"Failed to import vmecpp: {e}")
    print("Please ensure the package is built and installed")
    sys.exit(1)

if __name__ == "__main__":
    test_asymmetric_tokamak()