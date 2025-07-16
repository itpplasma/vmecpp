# TODO: Fix Test Regressions

## Strategic Plan

### Problem Analysis
- **8/9 Python test failures** are LOCAL-ONLY regressions (not in upstream)
- **1/1 C++ test failure** is LOCAL-ONLY regression (not in upstream)
- All failures are related to **"cma" test case** numerical precision
- Failures involve small numerical differences that exceed tight tolerances

### Strategic Approach
1. **Assess whether regressions are actual errors or acceptable numerical changes**
2. **Identify root cause** of numerical differences in our branch
3. **Fix code** to restore passing tests while maintaining correctness
4. **Update test tolerances** only if changes are mathematically justified

## Detailed Tactics

### Phase 1: Assessment - Determine if Regressions are Real Errors

#### 1.1 Compare Numerical Differences
- [ ] **Extract exact numerical values** from both upstream and local test runs
- [ ] **Calculate relative differences** for each failing test
- [ ] **Assess magnitude** of differences (are they within machine precision?)
- [ ] **Check for systematic patterns** (all differences in same direction/magnitude?)

**Implementation:**
```bash
# Run upstream tests with detailed output
cd upstream-vmecpp-test && pytest tests/ -v --tb=short > ../upstream-test-details.log 2>&1

# Run local tests with detailed output
cd .. && pytest tests/ -v --tb=short > local-test-details.log 2>&1

# Compare specific failing test outputs
diff -u upstream-test-details.log local-test-details.log
```

#### 1.2 Analyze Physics Significance
- [ ] **Research expected values** from VMEC literature for "cma" test case
- [ ] **Validate against reference implementations** (original Fortran VMEC)
- [ ] **Check if differences affect physics conclusions** (equilibrium properties)
- [ ] **Assess convergence properties** (do differences compound over iterations?)

**Focus areas:**
- `iota_axis`, `iota_edge`, `mean_iota`, `mean_shear` (rotational transform)
- `avforce` array (force balance residuals)
- `bsubsmns` array (magnetic field components)

#### 1.3 Identify Potential Causes
- [ ] **Review recent commits** in our branch vs upstream
- [ ] **Check compiler/build differences** (optimization flags, libraries)
- [ ] **Examine numerical algorithm changes** (Fourier transforms, iterative solvers)
- [ ] **Verify test data consistency** (same input files, reference outputs)

### Phase 2: Root Cause Analysis

#### 2.1 Isolate the Source
- [x] **Binary search through commits** to find introduction point
- [ ] **Test individual components** (C++ vs Python, different algorithms)
- [ ] **Compare intermediate calculations** (not just final results)
- [ ] **Check for uninitialized variables** or memory issues

**CURRENT PHASE: Focused Python Test Bisect**
- [x] **Identified 9 specific failing tests** with fresh install validation
- [x] **Create targeted bisect script** for Python tests with pip reinstall
- [x] **Run git bisect** with the 9 specific failing tests
- [x] **Find exact commit** where numerical regressions were introduced

**BISECT RESULTS:**
- **First bad commit**: `ca2a58a75ca0bc0a4b071d7be0c90836afd9b536`
- **Commit message**: "feat: Implement robust polygon area method for jacobian sign check"
- **Date**: Tue Jul 15 14:10:29 2025 +0200
- **Finding**: The polygon area method implementation introduced numerical precision changes
- **Impact**: All 8 local-only Python test failures trace back to this commit
- **Status**: Root cause identified - need to analyze numerical changes in polygon area method

**Implementation:**
```bash
# Create test-python-failures.sh script that:
# 1. Uninstalls existing vmecpp
# 2. Installs fresh from current commit (pip install -e .)
# 3. Runs exactly the 9 failing tests
# 4. Returns 0 if tests pass, 1 if tests fail

# Git bisect to find regression introduction
git bisect start HEAD upstream/main
git bisect run ./test-python-failures.sh
```

**Specific failing tests to bisect:**
- tests/cpp/vmecpp/vmec/pybind11/test_pybind_vmec.py::test_output_quantities
- tests/test_init.py::test_vmecwout_io
- tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-str]
- tests/test_init.py::test_against_reference_wout[cma.json-wout_cma.nc-Path]
- tests/test_simsopt_compat.py::test_iota_axis[input.cma]
- tests/test_simsopt_compat.py::test_iota_edge[input.cma]
- tests/test_simsopt_compat.py::test_mean_iota[input.cma]
- tests/test_simsopt_compat.py::test_mean_shear[input.cma]
- tests/test_simsopt_compat.py::test_ensure_vmec2000_input_from_vmecpp_input (upstream issue)

#### 2.2 Analyze Specific Failures

##### Python Test Failures:
- [ ] **test_output_quantities**: Check `avforce` array computation
- [ ] **test_vmecwout_io**: Verify I/O consistency and data marshalling
- [ ] **test_against_reference_wout**: Compare against known good reference
- [ ] **test_iota_***: Analyze rotational transform calculations
- [ ] **test_mean_***: Check profile averaging algorithms

##### C++ Test Failure:
- [ ] **output_quantities_test**: Focus on `bsubsmns` array tolerance violations
- [ ] **Compare C++ vs Python outputs** for same inputs
- [ ] **Check Fourier transform implementations** (basis conversions)

#### 2.3 Examine Key Algorithms
- [ ] **Fourier basis conversions** (internal vs external representations)
- [ ] **Force balance calculations** (ideal MHD model)
- [ ] **Geometry computations** (flux surface parameterization)
- [ ] **Numerical integration** (quadrature rules, grid spacing)

### Phase 3: Fix Implementation

#### 3.1 Code Fixes (Preferred)
- [ ] **Fix algorithmic bugs** if found (incorrect formulas, logic errors)
- [ ] **Restore numerical stability** (better conditioning, precision)
- [ ] **Update to match upstream algorithms** if we diverged incorrectly
- [ ] **Improve convergence criteria** for iterative methods

#### 3.2 Test Updates (Only if Justified)
- [ ] **Update reference data** if our results are more accurate
- [ ] **Relax tolerances** only if mathematically justified
- [ ] **Add tolerance explanations** in test comments
- [ ] **Validate against multiple test cases** (not just "cma")

#### 3.3 Validation
- [ ] **Run full test suite** after each fix
- [ ] **Compare with upstream results** to ensure alignment
- [ ] **Test multiple configurations** (different input files)
- [ ] **Check performance impact** of fixes

### Phase 4: Implementation Priority

#### High Priority (Physics-Critical)
1. **Rotational transform tests** (`test_iota_*`, `test_mean_*`)
   - Critical for equilibrium characterization
   - Direct impact on plasma stability analysis

2. **Force balance test** (`test_output_quantities`)
   - Core of VMEC algorithm
   - Affects convergence and accuracy

#### Medium Priority (I/O and Consistency)
3. **Reference comparison tests** (`test_against_reference_wout`)
   - Ensures backward compatibility
   - Validates against known good states

4. **I/O tests** (`test_vmecwout_io`)
   - Data integrity and serialization
   - Cross-platform compatibility

#### Lower Priority (Infrastructure)
5. **C++ test failure** (`output_quantities_test`)
   - Likely related to Python failures
   - May be fixed by addressing Python issues

### Phase 5: Validation and Testing

#### 5.1 Comprehensive Testing
- [ ] **Run upstream comparison** after each fix
- [ ] **Test with multiple input files** (not just "cma")
- [ ] **Validate hot restart functionality** (numerical consistency)
- [ ] **Check SIMSOPT integration** (optimization workflows)

#### 5.2 Performance and Stability
- [ ] **Benchmark performance** vs upstream
- [ ] **Test numerical stability** (multiple runs, different seeds)
- [ ] **Validate convergence rates** (multigrid efficiency)
- [ ] **Check memory usage** (no leaks or excessive allocation)

#### 5.3 Documentation
- [ ] **Document any tolerance changes** with justification
- [ ] **Update FAIL.md** with resolution status
- [ ] **Add test comments** explaining expected behavior
- [ ] **Create regression test** to prevent future issues

## Success Criteria

### Immediate Goals
- [ ] **All Python tests pass** (9/9 → 8/9 upstream parity)
- [ ] **All C++ tests pass** (15/15 like upstream)
- [ ] **No performance degradation** vs upstream
- [ ] **Maintain numerical accuracy** within physics requirements

### Long-term Goals
- [ ] **Establish CI/CD** with upstream comparison
- [ ] **Implement regression detection** for future changes
- [ ] **Improve test coverage** for edge cases
- [ ] **Document numerical precision** requirements

## Implementation Notes

### Tools and Scripts
- Use `test-upstream.sh` for regular comparison
- Create `test-single-failure.sh` for focused debugging
- Use `git bisect` for regression hunting
- Implement numerical comparison utilities

### Testing Strategy
- **Test early and often** - run subset of tests during development
- **Use multiple test cases** - don't rely solely on "cma"
- **Compare intermediate results** - not just final outputs
- **Validate physics consistency** - ensure equilibrium properties are reasonable

### Risk Management
- **Backup current state** before major changes
- **Test incrementally** - small changes, immediate validation
- **Document assumptions** - record why changes were made
- **Maintain upstream compatibility** - don't break existing workflows
