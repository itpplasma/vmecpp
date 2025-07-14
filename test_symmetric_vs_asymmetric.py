#!/usr/bin/env python3

import vmecpp
import numpy as np

def test_symmetric_baseline():
    """Test symmetric case as baseline"""
    print("🔄 TESTING SYMMETRIC BASELINE")
    print("=" * 40)
    
    # Load symmetric input
    input_data = vmecpp.VmecInput.from_file("examples/data/input.w7x")
    print(f"✓ Loaded symmetric input: lasym={input_data.lasym}")
    
    # Simplify parameters
    input_data.ns_array = [3]
    input_data.niter_array = [5]
    input_data.ftol_array = [0.1]
    
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

def test_asymmetric_minimal():
    """Test asymmetric with minimal setup"""
    print("\n🔄 TESTING ASYMMETRIC MINIMAL")
    print("=" * 40)
    
    # Start with symmetric input and enable asymmetric
    input_data = vmecpp.VmecInput.from_file("examples/data/input.w7x")
    input_data.lasym = True
    
    # Initialize asymmetric arrays with zeros
    # Shape should be (mpol, 2*ntor+1)
    shape = (input_data.mpol, 2 * input_data.ntor + 1)
    input_data.rbs = np.zeros(shape)
    input_data.zbc = np.zeros(shape)
    
    # Add tiny asymmetric perturbation to avoid pure symmetric case
    # Place small perturbation at m=1, n=0 location
    input_data.rbs[1, input_data.ntor] = 1e-6  # Small perturbation
    input_data.zbc[1, input_data.ntor] = 1e-6
    
    # Simplify parameters
    input_data.ns_array = [3]
    input_data.niter_array = [5]
    input_data.ftol_array = [0.1]
    
    print(f"✓ Setup asymmetric input with tiny perturbation")
    
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

if __name__ == "__main__":
    print("🧪 COMPARING SYMMETRIC VS ASYMMETRIC EXECUTION")
    print("=" * 60)
    
    # Test symmetric baseline
    sym_success = test_symmetric_baseline()
    
    # Test asymmetric
    asym_success = test_asymmetric_minimal()
    
    print(f"\n📊 RESULTS:")
    print(f"   Symmetric: {'✅' if sym_success else '❌'}")
    print(f"   Asymmetric: {'✅' if asym_success else '❌'}")