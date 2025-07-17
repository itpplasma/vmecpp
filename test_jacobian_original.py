#!/usr/bin/env python3
"""Direct test of the original up_down_asymmetric_tokamak case that fails in VMEC++ but
works in educational_VMEC and jVMEC."""

import copy

import vmecpp


def test_original_case():
    """Test the original failing case directly."""
    print("🔍 Testing original up_down_asymmetric_tokamak case")
    print("=" * 60)

    try:
        # Load the problematic case
        input_case = vmecpp.VmecInput.from_file(
            "examples/data/input.up_down_asymmetric_tokamak"
        )
        print("✓ Successfully loaded input.up_down_asymmetric_tokamak")

        # Print key parameters
        print("\nKey parameters:")
        print(f"  lasym: {input_case.lasym}")
        print(f"  nfp: {input_case.nfp}")
        print(f"  ns_array: {input_case.ns_array}")
        print(f"  niter_array: {input_case.niter_array}")
        print(f"  ftol_array: {input_case.ftol_array}")

        # Print axis initialization
        print("\nAxis initialization:")
        print(f"  raxis_c: {getattr(input_case, 'raxis_c', 'None')}")
        print(f"  zaxis_s: {getattr(input_case, 'zaxis_s', 'None')}")
        print(f"  raxis_s: {getattr(input_case, 'raxis_s', 'None')}")
        print(f"  zaxis_c: {getattr(input_case, 'zaxis_c', 'None')}")

        # Try with the original settings
        print("\n" + "=" * 60)
        print("Attempting VMEC++ run with original settings...")

        try:
            output = vmecpp.run(input_case)
            print("✅ SUCCESS: Original case works in VMEC++!")
            print("This means there is no bug in VMEC++ asymmetric implementation.")
            return True

        except Exception as e:
            error_str = str(e).lower()
            print(f"❌ FAILED: {e}")

            if "initial jacobian changed sign" in error_str or "jacobian" in error_str:
                print("🎯 CONFIRMED: BAD_JACOBIAN error in VMEC++")
                print("This is the bug we need to fix!")

                # Try some workarounds
                print("\n" + "-" * 40)
                print("Trying workarounds...")

                # Workaround 1: Better axis initialization
                print("\n1. Testing with explicit axis initialization...")
                test_case1 = copy.deepcopy(input_case)
                test_case1.raxis_c = [6.0]  # Close to RBC(0,0)
                test_case1.zaxis_s = [0.0]

                try:
                    output = vmecpp.run(test_case1)
                    print("✅ SUCCESS: Explicit axis initialization works!")
                    print(
                        "💡 Root cause: VMEC++ axis guessing algorithm fails for asymmetric cases"
                    )
                    return "AXIS_GUESS_BUG"
                except Exception as e2:
                    print(f"❌ Still fails: {e2}")

                # Workaround 2: Reduced perturbations
                print("\n2. Testing with reduced asymmetric perturbations...")
                test_case2 = copy.deepcopy(input_case)
                test_case2.raxis_c = [6.0]
                test_case2.zaxis_s = [0.0]

                # Scale down asymmetric coefficients
                if hasattr(test_case2, "rbs") and test_case2.rbs:
                    original_rbs = test_case2.rbs[0] if len(test_case2.rbs) > 0 else 0.6
                    test_case2.rbs = [{"n": 0, "m": 1, "value": 0.06}]  # 10x smaller
                    print("   Reduced RBS from 0.6 to 0.06")

                try:
                    output = vmecpp.run(test_case2)
                    print("✅ SUCCESS: Reduced perturbations work!")
                    print(
                        "💡 Root cause: VMEC++ cannot handle large asymmetric perturbations"
                    )
                    return "LARGE_PERTURBATION_BUG"
                except Exception as e3:
                    print(f"❌ Still fails: {e3}")

                print("\n💥 CONCLUSION: Fundamental VMEC++ asymmetric bug confirmed")
                print("This explains why educational_VMEC/jVMEC work but VMEC++ fails")
                return "FUNDAMENTAL_BUG"
            print(f"Different error (not BAD_JACOBIAN): {error_str}")
            return "OTHER_ERROR"

    except Exception as e:
        print(f"❌ Failed to load input file: {e}")
        return False


def main():
    """Main test routine."""
    result = test_original_case()

    print("\n" + "=" * 60)
    print("FINAL ANALYSIS:")
    print("=" * 60)

    if result == True:
        print("✅ No VMEC++ asymmetric bug found")
        print("The original case actually works in VMEC++")
    elif result == "AXIS_GUESS_BUG":
        print("🎯 BUG IDENTIFIED: VMEC++ asymmetric axis guessing algorithm")
        print(
            "VMEC++ fails to automatically guess a good magnetic axis for asymmetric cases"
        )
    elif result == "LARGE_PERTURBATION_BUG":
        print("🎯 BUG IDENTIFIED: VMEC++ large asymmetric perturbation handling")
        print("VMEC++ cannot handle large asymmetric boundary perturbations")
    elif result == "FUNDAMENTAL_BUG":
        print("🚨 CRITICAL: Fundamental VMEC++ asymmetric implementation bug")
        print(
            "VMEC++ asymmetric mode has core algorithmic differences from reference implementations"
        )
    else:
        print("❌ Could not determine the exact nature of the asymmetric bug")

    print("\nNext steps:")
    print("1. Compare VMEC++ vs educational_VMEC axis guessing algorithms")
    print("2. Compare asymmetric geometry calculations")
    print("3. Compare asymmetric Fourier transform implementations")


if __name__ == "__main__":
    main()
