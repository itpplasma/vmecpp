# Failed Tests Summary

Last updated: 2025-07-16

## **✅ ALL REGRESSIONS FIXED**

### Current Test Results:
- **Python tests**: ✅ **122 tests passed** (all regressions fixed)
- **C++ tests**: ✅ **All tests pass** (all regressions fixed)
- **Overall**: ✅ **Same test status as upstream**

## **Remaining Test Failures (Pre-existing Upstream Issues)**

### Python Tests (1 failed, 122 passed, 1 skipped)

#### Failed Test (Same as upstream):

1. **tests/test_simsopt_compat.py::test_ensure_vmec2000_input_from_vmecpp_input**
   - ValueError: _vmec._vmec.f90wrap_vmec_input__array__rbc: failed to create array
   - Issue: 0-th dimension must be fixed to 2 but got 4
   - **Status**: ❌ **UPSTREAM ISSUE** (also fails in upstream repository)
   - **Cause**: VMEC2000 compatibility issue - dimension mismatch with rbc array

### Pre-commit Checks (Same as upstream)

#### Pyright Type Errors (5 errors):

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

**Status**: ❌ **UPSTREAM ISSUES** (same errors when using consistent configuration)

## **Summary**

### ✅ **ALL REGRESSION FIXES SUCCESSFUL**

The following 9 test failures were successfully resolved:

**Python Tests Fixed (8)**:
- tests/cpp/vmecpp/vmec/pybind11/test_pybind_vmec.py::test_output_quantities ✅
- tests/test_init.py::test_vmecwout_io ✅
- tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-str] ✅
- tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-Path] ✅
- tests/test_simsopt_compat.py::test_iota_axis[input.cma] ✅
- tests/test_simsopt_compat.py::test_iota_edge[input.cma] ✅
- tests/test_simsopt_compat.py::test_mean_iota[input.cma] ✅
- tests/test_simsopt_compat.py::test_mean_shear[input.cma] ✅

**C++ Tests Fixed (1)**:
- //vmecpp/vmec/output_quantities:output_quantities_test ✅

### **Root Cause and Solution**

**Problem**: PR #359 introduced enhanced magnetic axis recomputation algorithm that affected symmetric cases, causing test failures for symmetric configurations.

**Solution**: Limited enhanced algorithm to asymmetric cases only:
- Use original 61×61 grid resolution for symmetric cases (`!s.lasym`)
- Use enhanced 101×101 grid + multi-level fallback only for asymmetric cases (`s.lasym = true`)
- File modified: `src/vmecpp/cpp/vmecpp/vmec/boundaries/guess_magnetic_axis.cc`

**Result**: All test failures resolved, maintaining same test status as upstream repository.

## **Note for Future Development**

The remaining test failures are **pre-existing upstream issues** and should not be considered regressions. Any new failures beyond these should be investigated as potential regressions.
