#!/usr/bin/env python3
"""Debug script to understand why input.up_down_asymmetric_tokamak works in
educational_VMEC/jVMEC but fails in VMEC++."""

import copy

import vmecpp


def debug_asymmetric_initialization():
    """Debug the asymmetric initialization in detail."""
    print("🔍 Debugging VMEC++ asymmetric initialization vs reference implementations")
    print("=" * 80)

    # Load the problematic case
    try:
        input_case = vmecpp.VmecInput.from_file(
            "examples/data/input.up_down_asymmetric_tokamak"
        )
        print("✓ Successfully loaded input.up_down_asymmetric_tokamak")

        # Print the key parameters
        print("\nInput parameters:")
        print(f"  lasym: {input_case.lasym}")
        print(f"  nfp: {input_case.nfp}")
        print(f"  mpol: {input_case.mpol}")
        print(f"  ntor: {input_case.ntor}")
        print(f"  ns_array: {input_case.ns_array}")
        print(f"  ftol_array: {input_case.ftol_array}")
        print(f"  niter_array: {input_case.niter_array}")

        # Print asymmetric boundary coefficients
        print("\nAsymmetric boundary coefficients:")
        if (
            hasattr(input_case, "rbs")
            and input_case.rbs is not None
            and len(input_case.rbs) > 0
        ):
            for i, coeff in enumerate(input_case.rbs):
                if isinstance(coeff, dict):
                    print(f"  RBS(n={coeff['n']}, m={coeff['m']}) = {coeff['value']}")
                else:
                    print(f"  RBS[{i}] = {coeff}")
        else:
            print("  No RBS coefficients")

        if (
            hasattr(input_case, "zbc")
            and input_case.zbc is not None
            and len(input_case.zbc) > 0
        ):
            for i, coeff in enumerate(input_case.zbc):
                if isinstance(coeff, dict):
                    print(f"  ZBC(n={coeff['n']}, m={coeff['m']}) = {coeff['value']}")
                else:
                    print(f"  ZBC[{i}] = {coeff}")
        else:
            print("  No ZBC coefficients")

        # Print symmetric boundary coefficients for comparison
        print("\nSymmetric boundary coefficients:")
        if (
            hasattr(input_case, "rbc")
            and input_case.rbc is not None
            and len(input_case.rbc) > 0
        ):
            for i, coeff in enumerate(input_case.rbc[:3]):  # First 3
                if isinstance(coeff, dict):
                    print(f"  RBC(n={coeff['n']}, m={coeff['m']}) = {coeff['value']}")
                else:
                    print(f"  RBC[{i}] = {coeff}")

        if (
            hasattr(input_case, "zbs")
            and input_case.zbs is not None
            and len(input_case.zbs) > 0
        ):
            for i, coeff in enumerate(input_case.zbs[:3]):  # First 3
                if isinstance(coeff, dict):
                    print(f"  ZBS(n={coeff['n']}, m={coeff['m']}) = {coeff['value']}")
                else:
                    print(f"  ZBS[{i}] = {coeff}")

        # Print axis coefficients
        print("\nAxis coefficients:")
        if hasattr(input_case, "raxis_c") and len(input_case.raxis_c) > 0:
            print(f"  RAXIS_C: {list(input_case.raxis_c)}")
        if hasattr(input_case, "raxis_s") and len(input_case.raxis_s) > 0:
            print(f"  RAXIS_S: {list(input_case.raxis_s)}")
        if hasattr(input_case, "zaxis_s") and len(input_case.zaxis_s) > 0:
            print(f"  ZAXIS_S: {list(input_case.zaxis_s)}")
        if hasattr(input_case, "zaxis_c") and len(input_case.zaxis_c) > 0:
            print(f"  ZAXIS_C: {list(input_case.zaxis_c)}")

        # Try running with minimal settings first
        print("\n" + "=" * 80)
        print("Testing with minimal settings...")

        # Test 1: Use the exact original settings but reduce resolution for faster debug
        test_case = copy.deepcopy(input_case)
        test_case.ns_array = [5]  # Much smaller for debugging
        test_case.niter_array = [10]
        test_case.ftol_array = [1e-6]

        try:
            print("Attempting run with reduced resolution...")
            output = vmecpp.run(test_case)
            print("✓ SUCCESS: Reduced resolution works!")
            return True

        except Exception as e:
            error_str = str(e)
            print(f"❌ FAILED with reduced resolution: {e}")

            if "INITIAL JACOBIAN CHANGED SIGN" in error_str:
                print("\n🎯 BAD_JACOBIAN confirmed in VMEC++")
                print("This suggests an issue with:")
                print("  1. Asymmetric axis initialization algorithm")
                print("  2. Asymmetric geometry computation")
                print("  3. Asymmetric Fourier transform implementation")

                # Test 2: Try with better axis guess
                print("\n" + "-" * 60)
                print("Testing with improved axis guess...")

                test_case2 = copy.deepcopy(input_case)
                test_case2.ns_array = [5]
                test_case2.niter_array = [10]
                test_case2.ftol_array = [1e-6]

                # Try setting a reasonable axis guess instead of zero
                test_case2.raxis_c = [6.0]  # Close to RBC(0,0)
                test_case2.zaxis_s = [0.0]

                try:
                    print("Attempting run with better axis guess...")
                    output = vmecpp.run(test_case2)
                    print("✓ SUCCESS: Better axis guess works!")
                    print(
                        "💡 Issue is likely with automatic axis guessing in asymmetric mode"
                    )
                    return True

                except Exception as e2:
                    print(f"❌ FAILED even with better axis guess: {e2}")

                    # Test 3: Try removing some asymmetric perturbations
                    print("\n" + "-" * 60)
                    print("Testing with reduced asymmetric perturbations...")

                    test_case3 = copy.deepcopy(input_case)
                    test_case3.ns_array = [5]
                    test_case3.niter_array = [10]
                    test_case3.ftol_array = [1e-6]
                    test_case3.raxis_c = [6.0]
                    test_case3.zaxis_s = [0.0]

                    # Reduce asymmetric perturbations
                    if hasattr(test_case3, "rbs") and len(test_case3.rbs) > 0:
                        for coeff in test_case3.rbs:
                            coeff["value"] *= 0.1  # Reduce by factor of 10

                    try:
                        print("Attempting run with reduced asymmetric perturbations...")
                        output = vmecpp.run(test_case3)
                        print("✓ SUCCESS: Reduced perturbations work!")
                        print(
                            "💡 Issue is likely with large asymmetric perturbation handling"
                        )
                        return True

                    except Exception as e3:
                        print(f"❌ FAILED even with reduced perturbations: {e3}")
                        print(
                            "💥 This indicates a fundamental issue in VMEC++ asymmetric implementation"
                        )
                        return False
            else:
                print(f"❌ Different error type: {error_str}")
                return False

    except Exception as e:
        print(f"❌ Failed to load input file: {e}")
        return False


def compare_with_working_case():
    """Compare the failing case with our working asymmetric case."""
    print("\n" + "=" * 80)
    print("Comparing with working solovev_asymmetric.json...")

    try:
        working_case = vmecpp.VmecInput.from_file(
            "src/vmecpp/cpp/vmecpp/test_data/solovev_asymmetric.json"
        )
        failing_case = vmecpp.VmecInput.from_file(
            "examples/data/input.up_down_asymmetric_tokamak"
        )

        print("\nWorking case (solovev_asymmetric.json):")
        print(
            f"  RBC(0,0): {working_case.rbc[0]['value'] if working_case.rbc and len(working_case.rbc) > 0 else 'N/A'}"
        )
        print(
            f"  RAXIS_C: {working_case.raxis_c[0] if working_case.raxis_c and len(working_case.raxis_c) > 0 else 'N/A'}"
        )
        print(
            f"  RBS(0,1): {working_case.rbs[0]['value'] if working_case.rbs and len(working_case.rbs) > 0 else 'N/A'}"
        )
        print(
            f"  NS: {working_case.ns_array[0] if working_case.ns_array and len(working_case.ns_array) > 0 else 'N/A'}"
        )

        print("\nFailing case (up_down_asymmetric_tokamak):")
        print(
            f"  RBC(0,0): {failing_case.rbc[0]['value'] if failing_case.rbc and len(failing_case.rbc) > 0 else 'N/A'}"
        )
        print(
            f"  RAXIS_C: {failing_case.raxis_c[0] if failing_case.raxis_c and len(failing_case.raxis_c) > 0 else 'N/A'}"
        )
        print(
            f"  RBS(0,1): {failing_case.rbs[0] if failing_case.rbs and len(failing_case.rbs) > 0 else 'N/A'}"
        )
        print(
            f"  NS: {failing_case.ns_array[0] if failing_case.ns_array and len(failing_case.ns_array) > 0 else 'N/A'}"
        )

        # Calculate the relative size of asymmetric perturbations (simplified)
        print("\nRelative asymmetric perturbation sizes:")
        try:
            working_rbs = (
                working_case.rbs[0]["value"]
                if working_case.rbs and len(working_case.rbs) > 0
                else 0
            )
            working_rbc = (
                working_case.rbc[0]["value"]
                if working_case.rbc and len(working_case.rbc) > 0
                else 1
            )

            failing_rbs = 0.6  # From the INDATA file
            failing_rbc = 6.0  # From the INDATA file

            print(f"  Working case: RBS/RBC = {working_rbs/working_rbc:.6f}")
            print(f"  Failing case: RBS/RBC = {failing_rbs/failing_rbc:.6f}")
            print(
                f"  Ratio: {(failing_rbs/failing_rbc)/(working_rbs/working_rbc):.1f}x larger"
            )
        except Exception as e:
            print(f"  Could not calculate ratio: {e}")

    except Exception as e:
        print(f"❌ Failed comparison: {e}")


def main():
    """Main debugging routine."""
    success = debug_asymmetric_initialization()
    compare_with_working_case()

    print("\n" + "=" * 80)
    print("CONCLUSIONS:")
    print("=" * 80)

    if success:
        print("✓ Found workaround for VMEC++ asymmetric issue")
        print("💡 Likely issues:")
        print("  - Asymmetric magnetic axis guessing algorithm")
        print("  - Large asymmetric perturbation handling")
        print("  - Need to compare with educational_VMEC/jVMEC implementation")
    else:
        print("❌ VMEC++ asymmetric mode has fundamental issues")
        print("🚨 CRITICAL: Need to debug asymmetric implementation")
        print("📋 Next steps:")
        print("  1. Compare asymmetric Fourier transform implementations")
        print("  2. Compare asymmetric geometry calculations")
        print("  3. Compare asymmetric axis initialization algorithms")
        print("  4. Run same input in educational_VMEC for reference")


if __name__ == "__main__":
    main()
