# Failed Tests Summary

## Pre-commit Checks

### Pyright Type Errors (5 errors)

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

## Python Tests (9 failed, 114 passed, 1 skipped)

### Failed Tests:

1. **tests/cpp/vmecpp/vmec/pybind11/test_pybind_vmec.py::test_output_quantities**
   - Issue: Numerical differences in avforce array values
   - Multiple mismatches between actual and expected values

2. **tests/test_init.py::test_vmecwout_io**
   - AssertionError (details not shown in output)

3. **tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-str]**
   - AssertionError (details not shown in output)

4. **tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-Path]**
   - AssertionError (details not shown in output)

5. **tests/test_simsopt_compat.py::test_iota_axis[input.cma]**
   - AssertionError (details not shown in output)

6. **tests/test_simsopt_compat.py::test_iota_edge[input.cma]**
   - AssertionError (details not shown in output)

7. **tests/test_simsopt_compat.py::test_mean_iota[input.cma]**
   - AssertionError (details not shown in output)

8. **tests/test_simsopt_compat.py::test_mean_shear[input.cma]**
   - AssertionError (details not shown in output)

9. **tests/test_simsopt_compat.py::test_ensure_vmec2000_input_from_vmecpp_input**
   - ValueError: _vmec._vmec.f90wrap_vmec_input__array__rbc: failed to create array
   - Issue: 0-th dimension must be fixed to 2 but got 4

## Notes

- Most failures appear to be related to the "cma" test case
- The failures seem to be numerical differences rather than crashes
- VMEC2000 compatibility test shows a dimension mismatch issue
