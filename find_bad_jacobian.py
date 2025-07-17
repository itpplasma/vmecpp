#!/usr/bin/env python3
"""Script to specifically trigger BAD_JACOBIAN errors in asymmetric cases."""

import copy

import vmecpp


def test_multiple_iterations(name, input_config, max_iterations=20):
    """Test with multiple iterations to see if BAD_JACOBIAN appears."""
    print(f"\n=== Testing {name} with {max_iterations} iterations ===")

    try:
        test_input = copy.deepcopy(input_config)
        test_input.ns_array = [5]
        test_input.niter_array = [max_iterations]
        test_input.ftol_array = [1e-8]  # Stricter tolerance

        output = vmecpp.run(test_input)
        print(f"✓ {name}: SUCCESS after {max_iterations} iterations")
        return True

    except Exception as e:
        error_str = str(e).lower()
        if "jacobian" in error_str or "initial jacobian changed sign" in error_str:
            print(f"🎯 {name}: BAD_JACOBIAN FOUND! - {e}")
            return "BAD_JACOBIAN"
        if "did not converge" in error_str:
            print(f"⚠️ {name}: Convergence failure (not BAD_JACOBIAN) - {e}")
            return "NO_CONVERGE"
        print(f"❌ {name}: Other error - {e}")
        return "OTHER_ERROR"


def main():
    """Search for BAD_JACOBIAN errors."""
    print("🔍 Searching for BAD_JACOBIAN errors in asymmetric cases")
    print("=" * 60)

    # Test the existing asymmetric case
    try:
        asym_case = vmecpp.VmecInput.from_file(
            "src/vmecpp/cpp/vmecpp/test_data/solovev_asymmetric.json"
        )
        print("Testing existing asymmetric case with different iteration counts...")

        for iterations in [5, 10, 20, 50]:
            result = test_multiple_iterations(
                f"solovev_asymmetric ({iterations}it)", asym_case, iterations
            )
            if result == "BAD_JACOBIAN":
                print(f"🎯 Found BAD_JACOBIAN at {iterations} iterations!")
                break
            if result == True:
                print(f"✓ Converged successfully at {iterations} iterations")
                break

    except Exception as e:
        print(f"❌ Failed to load asymmetric case: {e}")

    # Test the original asymmetric input file
    try:
        original_asym = vmecpp.VmecInput.from_file(
            "examples/data/input.up_down_asymmetric_tokamak"
        )
        print("\nTesting original asymmetric case...")

        for iterations in [5, 10, 20, 50]:
            result = test_multiple_iterations(
                f"up_down_asymmetric ({iterations}it)", original_asym, iterations
            )
            if result == "BAD_JACOBIAN":
                print(f"🎯 Found BAD_JACOBIAN at {iterations} iterations!")
                break
            if result == True:
                print(f"✓ Converged successfully at {iterations} iterations")
                break

    except Exception as e:
        print(f"❌ Failed to load original asymmetric case: {e}")

    # Test symmetric case with lasym=true
    try:
        symmetric = vmecpp.VmecInput.from_file(
            "src/vmecpp/cpp/vmecpp/test_data/solovev.json"
        )
        sym_to_asym = copy.deepcopy(symmetric)
        sym_to_asym.lasym = True
        sym_to_asym.raxis_s = [0.0]
        sym_to_asym.zaxis_c = [0.0]

        print("\nTesting symmetric→asymmetric conversion...")
        for iterations in [5, 10, 20, 50]:
            result = test_multiple_iterations(
                f"symmetric→asymmetric ({iterations}it)", sym_to_asym, iterations
            )
            if result == "BAD_JACOBIAN":
                print(f"🎯 Found BAD_JACOBIAN at {iterations} iterations!")
                break
            if result == True:
                print(f"✓ Converged successfully at {iterations} iterations")
                break

    except Exception as e:
        print(f"❌ Failed to test symmetric→asymmetric: {e}")

    print("\n" + "=" * 60)
    print("CONCLUSION: Search for BAD_JACOBIAN complete")


if __name__ == "__main__":
    main()
