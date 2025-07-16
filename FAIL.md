# Failed Tests Summary

Last updated: 2025-07-16

## Upstream Comparison

Tests were run on upstream main branch (commit d6f35d2) for comparison.
- **Python tests**: Same failures as local branch (9 failed, 114 passed, 1 skipped)
- **C++ tests**: Unable to complete due to timeout
- **Pre-commit checks**: Same pyright errors as local branch

**Conclusion**: All test failures are present in upstream and not introduced by local changes.

## Pre-commit Checks

### Pyright Type Errors (5 errors) - Also present in upstream

1. **examples/mpi_finite_difference.py:68**
   - Error: No overloads for "vstack" match the provided arguments
   - Issue: Argument of type "list[Any] | None" cannot be assigned to parameter "tup"

2. **examples/plot_plasma_boundary.py:75**
   - Error: Cannot access attribute "plot_surface" for class "Axes"
   - Issue: Attribute "plot_surface" is unknown

3. **examples/simsopt_qh_fixed_resolution.py:47**
   - Error: Argument type mismatch in from_tuples
   - Issue: Literal types not assignable to Real

4. **tests/test_util.py:77**
   - Error: Argument type mismatch in dense_to_sparse_coefficients
   - Issue: "list[list[int]]" is not assignable to "ndarray[Unknown, Unknown]"

## Python Tests (9 failed, 114 passed, 1 skipped) - All failures also in upstream

### Failed Tests:

1. **tests/cpp/vmecpp/vmec/pybind11/test_pybind_vmec.py::test_output_quantities**
   - Issue: Numerical differences in avforce array values
   - Multiple assertion failures comparing actual vs expected values in the avforce[3,48] test

2. **tests/test_init.py::test_vmecwout_io**
   - Issue: Multiple numerical mismatches in various output quantities
   - Failures in: lmns_from_wout, cvdrift0, gbdrift0, and other arrays

3. **tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-str]**
   - Issue: Numerical differences when comparing against reference wout file
   - Similar failures to test_vmecwout_io

4. **tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-Path]**
   - Issue: Same as above but with Path input type

5. **tests/test_simsopt_compat.py::test_iota_axis[input.cma]**
   - Actual: 0.43906603
   - Expected: 0.437699
   - Max absolute difference: 0.00136703
   - Max relative difference: 0.00312229

6. **tests/test_simsopt_compat.py::test_iota_edge[input.cma]**
   - Actual: 0.62151
   - Expected: 0.622457
   - Max absolute difference: 0.00094762
   - Max relative difference: 0.00152238

7. **tests/test_simsopt_compat.py::test_mean_iota[input.cma]**
   - Actual: 0.595672
   - Expected: 0.595568
   - Max absolute difference: 0.00010397
   - Max relative difference: 0.00017457

8. **tests/test_simsopt_compat.py::test_mean_shear[input.cma]**
   - Actual: 0.053502
   - Expected: 0.054697
   - Max absolute difference: 0.00119535
   - Max relative difference: 0.02185397

9. **tests/test_simsopt_compat.py::test_ensure_vmec2000_input_from_vmecpp_input**
   - ValueError: _vmec._vmec.f90wrap_vmec_input__array__rbc: failed to create array
   - Issue: 0-th dimension must be fixed to 2 but got 4

## C++ Tests (14 passed, 1 failed out of 15 tests) - Local results only

### Failed Test:

1. **//vmecpp/vmec/output_quantities:output_quantities_test**
   - Test case: CheckWOutFileContents/4 (cma test case)
   - Issue: Multiple numerical tolerance failures in bsubsmns array
   - Tolerance: 1.000e-06
   - Example failures:
     - out-of-tolerance: |-4.240e-06| > 1.000e-06
     - out-of-tolerance: | 3.822e-06| > 1.000e-06
     - out-of-tolerance: | 1.398e-06| > 1.000e-06
   - Total of 9 tolerance violations in the bsubsmns array comparison

### Passed Tests:
- //vmecpp/common/composed_types_lib:composed_types_lib_test
- //vmecpp/common/fourier_basis_fast_poloidal:fourier_basis_fast_poloidal_test
- //vmecpp/common/fourier_basis_fast_toroidal:fourier_basis_fast_toroidal_test
- //vmecpp/common/magnetic_configuration_lib:magnetic_configuration_lib_test
- //vmecpp/common/magnetic_field_provider:magnetic_field_provider_lib_test
- //vmecpp/common/makegrid_lib:makegrid_lib_test
- //vmecpp/common/util:util_test
- //vmecpp/common/vmec_indata:vmec_indata_test
- //vmecpp/free_boundary/singular_integrals:singular_integrals_test
- //vmecpp/vmec/pybind11:vmec_indata_pywrapper_test
- //vmecpp/vmec/radial_partitioning:radial_partitioning_test
- //vmecpp/vmec/vmec:vmec_in_memory_mgrid_test
- //vmecpp/vmec/vmec:vmec_test
- //vmecpp/vmec/output_quantities:output_quantities_io_test

## Notes

- **All Python test failures are present in upstream** - not introduced by local changes
- Most failures appear to be related to the "cma" test case
- The numerical differences are small but exceed the tight tolerances (rtol=1e-11 for Python, 1e-06 for C++)
- VMEC2000 compatibility test shows a dimension mismatch issue with rbc array
- Both Python and C++ tests show similar numerical accuracy issues with the cma case
- The failures suggest small algorithmic differences between expected and actual calculations
- C++ tests could not be compared with upstream due to timeout, but the single local failure is also in the cma test case
