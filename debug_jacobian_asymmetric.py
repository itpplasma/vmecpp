#!/usr/bin/env python3
"""Debug script to investigate BAD_JACOBIAN issues in asymmetric mode.

This script creates various asymmetric test cases with different perturbation levels to
understand where the geometry becomes invalid.
"""

import copy

import vmecpp


def create_minimal_asymmetric_case(base_input, perturbation_level=1e-6):
    """Create asymmetric case with minimal perturbations."""
    test_input = copy.deepcopy(base_input)
    test_input.lasym = True

    # Ensure asymmetric axis arrays exist
    if not hasattr(test_input, "raxis_s") or not test_input.raxis_s:
        test_input.raxis_s = [0.0] * (test_input.ntor + 1)
    if not hasattr(test_input, "zaxis_c") or not test_input.zaxis_c:
        test_input.zaxis_c = [0.0] * (test_input.ntor + 1)

    # Add minimal asymmetric boundary perturbations
    if not hasattr(test_input, "rbs") or not test_input.rbs:
        test_input.rbs = []
    if not hasattr(test_input, "zbc") or not test_input.zbc:
        test_input.zbc = []

    # Add tiny m=1 perturbations
    test_input.rbs.append({"n": 0, "m": 1, "value": perturbation_level})
    test_input.zbc.append({"n": 0, "m": 1, "value": perturbation_level})

    return test_input


def check_geometry_validity(input_config, name):
    """Check if geometry is valid and doesn't cause BAD_JACOBIAN."""
    print(f"\n=== Testing {name} ===")

    try:
        # Try single iteration
        test_input = copy.deepcopy(input_config)
        test_input.ns_array = [5]
        test_input.niter_array = [1]
        test_input.ftol_array = [1e-6]

        output = vmecpp.run(test_input)
        print(f"✓ {name}: Single iteration succeeded")

        # Try short run
        test_input.niter_array = [5]
        output = vmecpp.run(test_input)
        print(f"✓ {name}: Short run (5 iterations) succeeded")
        return True

    except Exception as e:
        error_str = str(e).lower()
        if "jacobian" in error_str:
            print(f"❌ {name}: BAD_JACOBIAN error - {e}")
            return False
        print(f"⚠️ {name}: Other error - {e}")
        return False


def analyze_boundary_coefficients(vmec_input):
    """Analyze boundary coefficients for potential issues."""
    print("\n=== Boundary Coefficient Analysis ===")
    print(f"lasym: {vmec_input.lasym}")
    print(f"nfp: {vmec_input.nfp}, mpol: {vmec_input.mpol}, ntor: {vmec_input.ntor}")

    # Symmetric coefficients
    if hasattr(vmec_input, "rbc") and len(vmec_input.rbc) > 0:
        print(f"RBC coefficients: {len(vmec_input.rbc)}")
        for i, coeff in enumerate(vmec_input.rbc[:5]):  # Show first 5
            print(f"  RBC(m={coeff['m']}, n={coeff['n']}) = {coeff['value']:.6f}")

    if hasattr(vmec_input, "zbs") and len(vmec_input.zbs) > 0:
        print(f"ZBS coefficients: {len(vmec_input.zbs)}")
        for i, coeff in enumerate(vmec_input.zbs[:5]):  # Show first 5
            print(f"  ZBS(m={coeff['m']}, n={coeff['n']}) = {coeff['value']:.6f}")

    # Asymmetric coefficients
    if hasattr(vmec_input, "rbs") and len(vmec_input.rbs) > 0:
        print(f"RBS coefficients: {len(vmec_input.rbs)}")
        for coeff in vmec_input.rbs:
            print(f"  RBS(m={coeff['m']}, n={coeff['n']}) = {coeff['value']:.6e}")

    if hasattr(vmec_input, "zbc") and len(vmec_input.zbc) > 0:
        print(f"ZBC coefficients: {len(vmec_input.zbc)}")
        for coeff in vmec_input.zbc:
            print(f"  ZBC(m={coeff['m']}, n={coeff['n']}) = {coeff['value']:.6e}")

    # Axis coefficients
    if hasattr(vmec_input, "raxis_c") and len(vmec_input.raxis_c) > 0:
        print(f"RAXIS_C: {list(vmec_input.raxis_c)}")
    if hasattr(vmec_input, "raxis_s") and len(vmec_input.raxis_s) > 0:
        print(f"RAXIS_S: {list(vmec_input.raxis_s)}")
    if hasattr(vmec_input, "zaxis_s") and len(vmec_input.zaxis_s) > 0:
        print(f"ZAXIS_S: {list(vmec_input.zaxis_s)}")
    if hasattr(vmec_input, "zaxis_c") and len(vmec_input.zaxis_c) > 0:
        print(f"ZAXIS_C: {list(vmec_input.zaxis_c)}")


def main():
    """Main debugging routine."""
    print("🔍 BAD_JACOBIAN Debugging for Asymmetric VMEC++")
    print("=" * 60)

    # Load base symmetric case that works
    base_symmetric = vmecpp.VmecInput.from_file(
        "src/vmecpp/cpp/vmecpp/test_data/solovev.json"
    )

    print("Testing baseline symmetric case...")
    analyze_boundary_coefficients(base_symmetric)
    symmetric_works = check_geometry_validity(base_symmetric, "Symmetric baseline")

    if not symmetric_works:
        print("❌ CRITICAL: Symmetric baseline case fails!")
        return

    # Test series of increasingly small asymmetric perturbations
    perturbation_levels = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]

    print(f"\n{'='*60}")
    print("Testing minimal asymmetric perturbations:")

    working_levels = []
    failing_levels = []

    for level in perturbation_levels:
        asym_case = create_minimal_asymmetric_case(base_symmetric, level)
        works = check_geometry_validity(asym_case, f"Perturbation {level:.0e}")

        if works:
            working_levels.append(level)
        else:
            failing_levels.append(level)

    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"Working perturbation levels: {working_levels}")
    print(f"Failing perturbation levels: {failing_levels}")

    if working_levels:
        print(f"✓ Smallest working perturbation: {min(working_levels):.0e}")
        # Analyze the geometry of the smallest working case
        best_case = create_minimal_asymmetric_case(base_symmetric, min(working_levels))
        print("\n=== Analysis of smallest working case ===")
        analyze_boundary_coefficients(best_case)
    else:
        print("❌ No asymmetric perturbations work!")

    # Test existing asymmetric cases
    print(f"\n{'='*60}")
    print("Testing existing asymmetric cases:")

    try:
        existing_asym = vmecpp.VmecInput.from_file(
            "src/vmecpp/cpp/vmecpp/test_data/solovev_asymmetric.json"
        )
        analyze_boundary_coefficients(existing_asym)
        check_geometry_validity(existing_asym, "solovev_asymmetric.json")
    except Exception as e:
        print(f"❌ Failed to load solovev_asymmetric.json: {e}")

    try:
        existing_up_down = vmecpp.VmecInput.from_file(
            "examples/data/input.up_down_asymmetric_tokamak"
        )
        analyze_boundary_coefficients(existing_up_down)
        check_geometry_validity(existing_up_down, "input.up_down_asymmetric_tokamak")
    except Exception as e:
        print(f"❌ Failed to load input.up_down_asymmetric_tokamak: {e}")


if __name__ == "__main__":
    main()
