#!/usr/bin/env python3

import vmecpp
import numpy as np

def test_asymmetric_with_axis_perturbation():
    """Test asymmetric with axis perturbation instead of boundary"""
    print("🔄 TESTING ASYMMETRIC WITH AXIS PERTURBATION")
    print("=" * 50)
    
    # Start with symmetric input
    input_data = vmecpp.VmecInput.from_file("examples/data/input.w7x")
    input_data.lasym = True
    
    # Initialize asymmetric arrays with zeros
    shape = (input_data.mpol, 2 * input_data.ntor + 1)
    input_data.rbs = np.zeros(shape)
    input_data.zbc = np.zeros(shape)
    
    # Initialize axis arrays (shape is ntor+1)
    input_data.raxis_s = np.zeros(input_data.ntor + 1)
    input_data.zaxis_c = np.zeros(input_data.ntor + 1)
    
    # Add small asymmetric perturbation to axis instead of boundary
    # This is less likely to cause Jacobian issues
    input_data.raxis_s[0] = 1e-4  # Small R asymmetric at n=0
    input_data.zaxis_c[0] = 1e-4  # Small Z asymmetric at n=0
    
    # Use more surfaces and iterations for stability
    input_data.ns_array = [5]
    input_data.niter_array = [20]
    input_data.ftol_array = [1e-2]
    
    print(f"✓ Setup asymmetric input with axis perturbation")
    print(f"  raxis_s[0] = {input_data.raxis_s[0]}")
    print(f"  zaxis_c[0] = {input_data.zaxis_c[0]}")
    
    try:
        output = vmecpp.run(input_data)
        if output.success:
            print("✅ Asymmetric run: SUCCESS")
            print(f"   Final fsqr: {output.wout.fsqr}")
            print(f"   Final fsqz: {output.wout.fsqz}")
            return True
        else:
            print("❌ Asymmetric run: FAILED")
            return False
    except Exception as e:
        print(f"💥 Asymmetric run: EXCEPTION - {e}")
        return False

def test_asymmetric_larger_boundary():
    """Test asymmetric with larger boundary perturbation"""
    print("\n🔄 TESTING ASYMMETRIC WITH LARGER BOUNDARY PERTURBATION")
    print("=" * 50)
    
    # Start with symmetric input
    input_data = vmecpp.VmecInput.from_file("examples/data/input.w7x")
    input_data.lasym = True
    
    # Initialize asymmetric arrays with zeros
    shape = (input_data.mpol, 2 * input_data.ntor + 1)
    input_data.rbs = np.zeros(shape)
    input_data.zbc = np.zeros(shape)
    
    # Add larger asymmetric perturbation (0.1% of minor radius)
    # Estimate minor radius from rbc[0,0] and rbc[1,0]
    major_radius = input_data.rbc[0, input_data.ntor]
    minor_radius = abs(input_data.rbc[1, input_data.ntor]) if input_data.mpol > 1 else 0.1
    perturbation = 1e-3 * minor_radius
    
    input_data.rbs[1, input_data.ntor] = perturbation
    input_data.zbc[1, input_data.ntor] = perturbation
    
    # Use gradual approach
    input_data.ns_array = [3, 5, 9]
    input_data.niter_array = [20, 30, 50]
    input_data.ftol_array = [1e-2, 1e-3, 1e-4]
    
    print(f"✓ Setup asymmetric input with scaled perturbation")
    print(f"  Perturbation size: {perturbation:.6f}")
    print(f"  Relative to minor radius: {perturbation/minor_radius:.1%}")
    
    try:
        output = vmecpp.run(input_data)
        if output.success:
            print("✅ Asymmetric run: SUCCESS")
            print(f"   Final fsqr: {output.wout.fsqr}")
            print(f"   Final fsqz: {output.wout.fsqz}")
            # Check that asymmetric arrays are populated
            if hasattr(output.wout, 'rmnsc') and output.wout.rmnsc is not None:
                print(f"   ✓ Asymmetric arrays populated")
                print(f"   Max |rmnsc|: {np.max(np.abs(output.wout.rmnsc))}")
                print(f"   Max |zmncc|: {np.max(np.abs(output.wout.zmncc))}")
            return True
        else:
            print("❌ Asymmetric run: FAILED")
            return False
    except Exception as e:
        print(f"💥 Asymmetric run: EXCEPTION - {e}")
        return False

def test_symmetric_baseline_better():
    """Test symmetric case with better parameters"""
    print("\n🔄 TESTING SYMMETRIC BASELINE (BETTER PARAMETERS)")
    print("=" * 50)
    
    input_data = vmecpp.VmecInput.from_file("examples/data/input.w7x")
    print(f"✓ Loaded symmetric input: lasym={input_data.lasym}")
    
    # Use gradual approach for better convergence
    input_data.ns_array = [3, 5, 9]
    input_data.niter_array = [20, 30, 50]
    input_data.ftol_array = [1e-2, 1e-3, 1e-4]
    
    try:
        output = vmecpp.run(input_data)
        if output.success:
            print("✅ Symmetric run: SUCCESS")
            print(f"   Final fsqr: {output.wout.fsqr}")
            print(f"   Final fsqz: {output.wout.fsqz}")
            return True
        else:
            print("❌ Symmetric run: FAILED")
            return False
    except Exception as e:
        print(f"💥 Symmetric run: EXCEPTION - {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING ASYMMETRIC CONVERGENCE")
    print("=" * 60)
    
    # Test symmetric baseline with better parameters
    sym_success = test_symmetric_baseline_better()
    
    # Test asymmetric with axis perturbation
    asym_axis_success = test_asymmetric_with_axis_perturbation()
    
    # Test asymmetric with larger boundary perturbation
    asym_boundary_success = test_asymmetric_larger_boundary()
    
    print(f"\n📊 RESULTS:")
    print(f"   Symmetric (better params): {'✅' if sym_success else '❌'}")
    print(f"   Asymmetric (axis perturb): {'✅' if asym_axis_success else '❌'}")
    print(f"   Asymmetric (boundary perturb): {'✅' if asym_boundary_success else '❌'}")