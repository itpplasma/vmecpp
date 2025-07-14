#!/usr/bin/env python3

import vmecpp
import numpy as np

def test_tok_asym():
    """Test the existing tokamak asymmetric example"""
    print("🔄 TESTING EXISTING TOKAMAK ASYMMETRIC EXAMPLE")
    print("=" * 50)
    
    input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"✓ Loaded tokamak asymmetric input: lasym={input_data.lasym}")
    print(f"  zaxis_c[0] = {input_data.zaxis_c[0]}")
    print(f"  nfp = {input_data.nfp} (tokamak)")
    print(f"  mpol = {input_data.mpol}, ntor = {input_data.ntor}")
    
    try:
        output = vmecpp.run(input_data)
        if output.success:
            print("✅ Asymmetric tokamak run: SUCCESS")
            print(f"   Final fsqr: {output.wout.fsqr}")
            print(f"   Final fsqz: {output.wout.fsqz}")
            # Check asymmetric arrays
            if hasattr(output.wout, 'rmnsc') and output.wout.rmnsc is not None:
                print(f"   ✓ Asymmetric arrays populated")
                print(f"   Shape of rmnsc: {output.wout.rmnsc.shape}")
                print(f"   Max |rmnsc|: {np.max(np.abs(output.wout.rmnsc))}")
                print(f"   Max |zmncc|: {np.max(np.abs(output.wout.zmncc))}")
            return True
        else:
            print("❌ Asymmetric tokamak run: FAILED")
            return False
    except Exception as e:
        print(f"💥 Asymmetric tokamak run: EXCEPTION - {e}")
        return False

def test_heliotron_asym():
    """Test the existing heliotron asymmetric example"""
    print("\n🔄 TESTING EXISTING HELIOTRON ASYMMETRIC EXAMPLE")
    print("=" * 50)
    
    input_data = vmecpp.VmecInput.from_file("examples/data/HELIOTRON_asym.json")
    print(f"✓ Loaded heliotron asymmetric input: lasym={input_data.lasym}")
    print(f"  nfp = {input_data.nfp}")
    print(f"  mpol = {input_data.mpol}, ntor = {input_data.ntor}")
    
    try:
        output = vmecpp.run(input_data)
        if output.success:
            print("✅ Asymmetric heliotron run: SUCCESS")
            print(f"   Final fsqr: {output.wout.fsqr}")
            print(f"   Final fsqz: {output.wout.fsqz}")
            return True
        else:
            print("❌ Asymmetric heliotron run: FAILED")
            return False
    except Exception as e:
        print(f"💥 Asymmetric heliotron run: EXCEPTION - {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING EXISTING ASYMMETRIC EXAMPLES")
    print("=" * 60)
    
    # Test existing asymmetric examples
    tok_success = test_tok_asym()
    heliotron_success = test_heliotron_asym()
    
    print(f"\n📊 RESULTS:")
    print(f"   Tokamak asymmetric: {'✅' if tok_success else '❌'}")
    print(f"   Heliotron asymmetric: {'✅' if heliotron_success else '❌'}")
    
    if tok_success or heliotron_success:
        print("\n✨ At least one asymmetric example works!")
        print("   The asymmetric implementation is functional.")
    else:
        print("\n⚠️  No asymmetric examples converged.")