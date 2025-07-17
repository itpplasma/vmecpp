#!/usr/bin/env python3
"""Simple debug script to investigate BAD_JACOBIAN issues."""

import copy

import vmecpp


def test_case(name, input_config):
    """Test a single case and report results."""
    print(f"\n=== Testing {name} ===")

    try:
        # Configure for minimal run
        test_input = copy.deepcopy(input_config)
        test_input.ns_array = [5]
        test_input.niter_array = [1]
        test_input.ftol_array = [1e-6]

        output = vmecpp.run(test_input)
        print(f"✓ {name}: SUCCESS - Single iteration completed")
        return True

    except Exception as e:
        error_str = str(e).lower()
        if "jacobian" in error_str:
            print(f"❌ {name}: BAD_JACOBIAN - {e}")
        else:
            print(f"⚠️ {name}: OTHER ERROR - {e}")
        return False


def main():
    """Simple BAD_JACOBIAN investigation."""
    print("🔍 Simple BAD_JACOBIAN Investigation")
    print("=" * 50)

    # Test 1: Symmetric baseline
    print("Loading symmetric baseline...")
    symmetric = vmecpp.VmecInput.from_file(
        "src/vmecpp/cpp/vmecpp/test_data/solovev.json"
    )
    print(f"Symmetric - lasym: {symmetric.lasym}")
    success_sym = test_case("Symmetric baseline", symmetric)

    # Test 2: Our existing asymmetric case
    print("\nLoading existing asymmetric case...")
    try:
        existing_asym = vmecpp.VmecInput.from_file(
            "src/vmecpp/cpp/vmecpp/test_data/solovev_asymmetric.json"
        )
        print(f"Existing asymmetric - lasym: {existing_asym.lasym}")
        success_asym = test_case("Existing asymmetric", existing_asym)
    except Exception as e:
        print(f"❌ Failed to load existing asymmetric case: {e}")
        success_asym = False

    # Test 3: Convert symmetric to asymmetric with zero coefficients
    print("\nCreating symmetric→asymmetric conversion...")
    sym_to_asym = copy.deepcopy(symmetric)
    sym_to_asym.lasym = True
    sym_to_asym.raxis_s = [0.0]
    sym_to_asym.zaxis_c = [0.0]
    sym_to_asym.rbs = []
    sym_to_asym.zbc = []
    print(f"Converted - lasym: {sym_to_asym.lasym}")
    success_convert = test_case("Symmetric→Asymmetric (zero coeffs)", sym_to_asym)

    # Test 4: Tiny asymmetric perturbation
    print("\nCreating tiny asymmetric perturbation...")
    tiny_asym = copy.deepcopy(symmetric)
    tiny_asym.lasym = True
    tiny_asym.raxis_s = [0.0]
    tiny_asym.zaxis_c = [0.0]
    tiny_asym.rbs = [{"n": 0, "m": 1, "value": 1e-8}]
    tiny_asym.zbc = [{"n": 0, "m": 1, "value": 1e-8}]
    print(f"Tiny perturbation - lasym: {tiny_asym.lasym}")
    success_tiny = test_case("Tiny asymmetric perturbation", tiny_asym)

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✓ Symmetric baseline: {'PASS' if success_sym else 'FAIL'}")
    print(f"✓ Existing asymmetric: {'PASS' if success_asym else 'FAIL'}")
    print(f"✓ Symmetric→Asymmetric: {'PASS' if success_convert else 'FAIL'}")
    print(f"✓ Tiny perturbation: {'PASS' if success_tiny else 'FAIL'}")

    if success_sym and not success_convert:
        print("\n🎯 KEY FINDING: Simply enabling lasym=true causes BAD_JACOBIAN!")
    elif success_convert and not success_asym:
        print("\n🎯 KEY FINDING: Issue is with specific asymmetric coefficients!")
    elif not success_sym:
        print("\n❌ CRITICAL: Even symmetric baseline fails!")
    else:
        print("\n✅ All cases work - no BAD_JACOBIAN issue found!")


if __name__ == "__main__":
    main()
