#!/usr/bin/env python3
"""Test workarounds for the BAD_JACOBIAN issue in VMEC++ asymmetric mode."""

import copy

import vmecpp


def test_workaround(name, input_case, description):
    """Test a single workaround."""
    print(f"\n=== {name} ===")
    print(f"Description: {description}")

    try:
        # Try with reduced settings for faster testing
        test_input = copy.deepcopy(input_case)
        test_input.ns_array = [5]  # Much smaller for quick testing
        test_input.niter_array = [20]  # Fewer iterations
        test_input.ftol_array = [1e-6]  # Looser tolerance

        output = vmecpp.run(test_input)
        print(f"✅ SUCCESS: {name} works!")
        return True

    except Exception as e:
        error_str = str(e).lower()
        if "jacobian" in error_str or "initial jacobian changed sign" in error_str:
            print(f"❌ BAD_JACOBIAN: {name} still fails with Jacobian error")
        elif "fatal error" in error_str:
            print(f"❌ FATAL ERROR: {name} fails with multi-thread error")
        else:
            print(f"⚠️ OTHER ERROR: {name} fails with: {e}")
        return False


def main():
    """Test various workarounds for the asymmetric BAD_JACOBIAN issue."""
    print("🔍 Testing workarounds for VMEC++ asymmetric BAD_JACOBIAN")
    print("=" * 60)

    # Load the problematic case
    try:
        original_case = vmecpp.VmecInput.from_file(
            "examples/data/input.up_down_asymmetric_tokamak"
        )
        print("✓ Successfully loaded input.up_down_asymmetric_tokamak")

        # Display current axis initialization
        print("\nOriginal axis initialization:")
        print(f"  raxis_c: {getattr(original_case, 'raxis_c', 'None')}")
        print(f"  zaxis_s: {getattr(original_case, 'zaxis_s', 'None')}")

    except Exception as e:
        print(f"❌ Failed to load input file: {e}")
        return

    # Test 1: Explicit axis initialization
    workaround1 = copy.deepcopy(original_case)
    workaround1.raxis_c = [6.0]  # Set to RBC(0,0) value
    workaround1.zaxis_s = [0.0]
    success1 = test_workaround(
        "Explicit Axis", workaround1, "Set RAXIS_C=6.0 (matching RBC(0,0)), ZAXIS_S=0.0"
    )

    # Test 2: Reduced asymmetric perturbations
    workaround2 = copy.deepcopy(original_case)
    workaround2.raxis_c = [6.0]
    workaround2.zaxis_s = [0.0]
    # Manually set smaller RBS values
    if hasattr(workaround2, "rbs"):
        workaround2.rbs = [{"n": 0, "m": 1, "value": 0.06}]  # 10x smaller than 0.6
    success2 = test_workaround(
        "Reduced Perturbations",
        workaround2,
        "RAXIS_C=6.0 + RBS(0,1)=0.06 (10x smaller)",
    )

    # Test 3: Minimal asymmetric case
    workaround3 = copy.deepcopy(original_case)
    workaround3.raxis_c = [6.0]
    workaround3.zaxis_s = [0.0]
    if hasattr(workaround3, "rbs"):
        workaround3.rbs = [{"n": 0, "m": 1, "value": 0.006}]  # 100x smaller
    success3 = test_workaround(
        "Minimal Perturbations",
        workaround3,
        "RAXIS_C=6.0 + RBS(0,1)=0.006 (100x smaller)",
    )

    # Test 4: Only axis fix, no perturbation reduction
    workaround4 = copy.deepcopy(original_case)
    workaround4.raxis_c = [6.0]
    workaround4.zaxis_s = [0.0]
    # Keep original perturbations
    success4 = test_workaround(
        "Axis Only", workaround4, "Only fix axis (RAXIS_C=6.0), keep RBS(0,1)=0.6"
    )

    # Summary
    print("\n" + "=" * 60)
    print("WORKAROUND TEST RESULTS:")
    print(f"✓ Explicit Axis:         {'SUCCESS' if success1 else 'FAILED'}")
    print(f"✓ Reduced Perturbations: {'SUCCESS' if success2 else 'FAILED'}")
    print(f"✓ Minimal Perturbations: {'SUCCESS' if success3 else 'FAILED'}")
    print(f"✓ Axis Only:             {'SUCCESS' if success4 else 'FAILED'}")

    print("\nCONCLUSIONS:")
    if success1 or success2 or success3 or success4:
        print("✅ Found working workarounds!")
        if success4:
            print("💡 ROOT CAUSE: Poor magnetic axis initialization")
            print("   VMEC++ axis guessing algorithm fails for asymmetric cases")
        elif success1 and not success4:
            print("💡 ROOT CAUSE: Combined axis + unknown factor")
        elif success2 or success3:
            print("💡 ROOT CAUSE: Large asymmetric perturbations")
            print("   VMEC++ cannot handle RBS(0,1)=0.6 even with good axis")
    else:
        print("❌ No workarounds successful - fundamental VMEC++ asymmetric bug")
        print("🚨 CRITICAL: Need deep investigation of asymmetric implementation")


if __name__ == "__main__":
    main()
