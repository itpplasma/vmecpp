# TODO: Asymmetric VMEC++ Validation and Testing

## Strategic Goal

**Primary Objective**: Ensure that `lasym=true` mode produces correct results by implementing comprehensive validation against upstream VMEC2000 for asymmetric equilibria.

**Success Criteria**:
- All symmetric test cases pass with `lasym=true` and zero asymmetric coefficients
- Results match symmetric mode up to floating-point precision
- True asymmetric test cases match upstream VMEC2000 reference solutions
- Complete test coverage for asymmetric functionality

## Phase 1: Symmetric Test Validation with lasym=true

### 1.1 Analyze Current Test Infrastructure

**Current Status Analysis:**
- [x] **Review existing test structure** - Found 124 passing tests with symmetric inputs
- [x] **Identify symmetric test cases** - Key candidates: `solovev.json`, `cma.json`, `circular_tokamak.json`
- [x] **Check asymmetric infrastructure** - Basic tests exist but no physics validation
- [x] **Document current state** - Tests only verify code doesn't crash with lasym=true

**Key Findings:**
- Tests exist: `vmec_asymmetric_test.cc` (3 tests) and `test_init.py` (2 validation tests)
- No actual physics validation - only input creation and convergence checking
- No reference data for asymmetric cases with non-zero asymmetric coefficients

### 1.2 Create Symmetric-with-lasym=true Test Suite

**Implementation Plan:**
- [ ] **Create test utility function** `run_symmetric_as_asymmetric(input_file)`
  - Load symmetric input file (JSON format)
  - Set `lasym=true`
  - Set all asymmetric coefficients to zero: `rbs=0`, `zbc=0`, `raxis_s=0`, `zaxis_c=0`
  - Run VMEC++ and return output
- [ ] **Implement comparison utility** `compare_symmetric_asymmetric_outputs(sym_output, asym_output)`
  - Compare all output quantities with strict floating-point tolerance
  - Focus on: `rmnc`, `zmns`, `lmns`, `bmnc`, `iotaf`, `presf`, `phi`, `chi`
  - Use `np.testing.assert_allclose` with `rtol=1e-14, atol=1e-14`

**Test Cases to Validate:**
- [ ] **`solovev.json`** - Analytical tokamak (simplest case)
- [ ] **`circular_tokamak.json`** - Minimal tokamak boundary
- [ ] **`cma.json`** - Standard tokamak case
- [ ] **`cth_like_free_bdy.json`** - Free boundary stellarator
- [ ] **`li383_low_res.json`** - Low-resolution stellarator

**Expected Outcome:** All symmetric results should be identical when run with `lasym=true` and zero asymmetric coefficients.

### 1.3 Debug and Fix Asymmetric Infrastructure Issues

**Known Issues to Address:**
- [ ] **C++ binding issues** - Current asymmetric tests may have pybind11 problems
- [ ] **Memory initialization** - Ensure all asymmetric arrays are properly initialized
- [ ] **Fourier transform validation** - Verify `fourier_asymmetric.cc` implementations
- [ ] **Geometry extension** - Check `SymmetrizeRealSpaceGeometry` function

**Debugging Strategy:**
1. **Start with C++ tests** - Run `bazel test //vmecpp/vmec/vmec:vmec_asymmetric_test`
2. **Add diagnostic output** - Print intermediate values in asymmetric Fourier transforms
3. **Compare step-by-step** - Validate each stage of asymmetric computation
4. **Test individual components** - Isolate `fourier_asymmetric.cc` functions

## Phase 2: True Asymmetric Test Case Development

### 2.1 Create Reference Asymmetric Test Cases

**Generate Upstream Reference Data:**
- [ ] **Create simple asymmetric tokamak** - Based on `solovev.json` with small asymmetric perturbations
  - Add small `rbs[1,0] = 0.001` (n=0, m=1 asymmetric boundary component)
  - Add small `zbc[1,0] = 0.001` (n=0, m=1 asymmetric boundary component)
  - Add small `raxis_s[1] = 0.0001` (n=1 asymmetric axis component)
- [ ] **Create asymmetric stellarator** - Based on `cma.json` with asymmetric perturbations
  - Add `rbs[1,1] = 0.001` (n=1, m=1 asymmetric boundary)
  - Add `zbc[1,1] = 0.001` (n=1, m=1 asymmetric boundary)
- [ ] **Run with upstream VMEC2000** - Generate reference wout files
  - Use Fortran VMEC with identical input parameters
  - Save as `wout_solovev_asymmetric_ref.nc`, `wout_cma_asymmetric_ref.nc`

**Test Case Requirements:**
- Small asymmetric perturbations (< 1% of symmetric components)
- Should converge reliably with upstream VMEC2000
- Cover both tokamak and stellarator geometries
- Include both fixed and free boundary cases

### 2.2 Implement Asymmetric Validation Framework

**Core Testing Infrastructure:**
- [ ] **Create `test_asymmetric_physics.py`** - New test module for asymmetric validation
- [ ] **Implement `compare_asymmetric_outputs()`** - Compare VMEC++ vs reference
  - Handle both symmetric (`rmnc`, `zmns`) and asymmetric (`rmns`, `zmnc`) components
  - Compare asymmetric axis arrays (`raxis_s`, `zaxis_c`)
  - Validate asymmetric force balance arrays
- [ ] **Add asymmetric output quantities** - Ensure all asymmetric arrays are accessible
  - `rmns` (R sin(mθ - nζ) components)
  - `zmnc` (Z cos(mθ - nζ) components)
  - `lmns` (λ sin(mθ - nζ) components)
  - `bsubs` (B_s asymmetric components)

**Test Functions to Implement:**
- [ ] `test_asymmetric_tokamak_convergence()` - Basic convergence test
- [ ] `test_asymmetric_stellarator_convergence()` - Stellarator convergence test
- [ ] `test_asymmetric_vs_upstream_reference()` - Compare against VMEC2000 reference
- [ ] `test_asymmetric_force_balance()` - Validate force balance equations
- [ ] `test_asymmetric_geometric_quantities()` - Check geometric consistency

### 2.3 Extend Existing Test Suite

**Modify Current Tests:**
- [ ] **Extend `test_against_reference_wout()`** - Add asymmetric reference comparisons
- [ ] **Update `test_simsopt_compat.py`** - Add asymmetric compatibility tests
- [ ] **Enhance `test_free_boundary.py`** - Add asymmetric free boundary tests
- [ ] **Update C++ tests** - Add true asymmetric cases to `vmec_asymmetric_test.cc`

**SIMSOPT Integration:**
- [ ] **Test asymmetric optimization** - Ensure SIMSOPT can optimize asymmetric equilibria
- [ ] **Validate derivatives** - Check that asymmetric parameter derivatives are correct
- [ ] **Hot restart with asymmetric** - Test restart capability with asymmetric configurations

## Phase 3: Comprehensive Asymmetric Physics Validation

### 3.1 Mathematical Consistency Checks

**Fourier Transform Validation:**
- [ ] **Test basis conversions** - Verify internal product basis ↔ external combined basis
- [ ] **Check orthogonality** - Ensure Fourier basis functions are orthogonal
- [ ] **Validate periodicity** - Check that asymmetric functions have correct symmetry
- [ ] **Test inverse transforms** - Verify that Fourier ↔ real space is invertible

**Force Balance Validation:**
- [ ] **Compare force residuals** - Check that asymmetric force balance is satisfied
- [ ] **Validate pressure balance** - Ensure ∇p = j×B holds in asymmetric geometry
- [ ] **Check magnetic field** - Verify ∇·B = 0 and other Maxwell equations
- [ ] **Test equilibrium consistency** - Ensure equilibrium properties are self-consistent

### 3.2 Numerical Algorithm Validation

**Asymmetric Geometry Algorithms:**
- [ ] **Test `SymmetrizeRealSpaceGeometry()`** - Verify geometry extension from [0,π] to [0,2π]
- [ ] **Validate `SymmetrizeForces()`** - Check force symmetrization and separation
- [ ] **Test Jacobian calculations** - Ensure asymmetric Jacobian is computed correctly
- [ ] **Check metric tensor** - Validate asymmetric metric tensor components

**Convergence and Stability:**
- [ ] **Test convergence rates** - Compare asymmetric vs symmetric convergence
- [ ] **Validate stability** - Ensure asymmetric equilibria are stable
- [ ] **Check parameter sensitivity** - Test response to asymmetric parameter changes
- [ ] **Validate boundary conditions** - Ensure proper boundary condition handling

### 3.3 Performance and Scalability

**Performance Benchmarks:**
- [ ] **Compare execution time** - Asymmetric vs symmetric mode performance
- [ ] **Memory usage analysis** - Check memory overhead of asymmetric arrays
- [ ] **Scalability testing** - Test with larger mode numbers (higher resolution)
- [ ] **OpenMP performance** - Verify parallel efficiency in asymmetric mode

**Optimization Testing:**
- [ ] **Profile asymmetric code** - Identify performance bottlenecks
- [ ] **Optimize Fourier transforms** - Improve asymmetric transform efficiency
- [ ] **Test different compilers** - Ensure consistent behavior across compilers
- [ ] **Validate numerical precision** - Check for precision loss in asymmetric calculations

## Phase 4: Integration and Regression Testing

### 4.1 Continuous Integration Setup

**CI/CD Pipeline:**
- [ ] **Add asymmetric tests to CI** - Include in automated test suite
- [ ] **Create asymmetric benchmarks** - Regular performance monitoring
- [ ] **Set up reference comparison** - Automated comparison against upstream
- [ ] **Add regression detection** - Catch asymmetric functionality breakage

**Documentation and Examples:**
- [ ] **Create asymmetric examples** - Show how to use asymmetric mode
- [ ] **Update user documentation** - Explain asymmetric capabilities
- [ ] **Add developer guide** - Document asymmetric code structure
- [ ] **Create troubleshooting guide** - Help users debug asymmetric issues

### 4.2 Validation Against Literature

**Physics Validation:**
- [ ] **Compare against published results** - Validate against known asymmetric equilibria
- [ ] **Test edge cases** - Verify behavior at limits of asymmetric parameters
- [ ] **Cross-validate with other codes** - Compare against SPEC, HINT, etc.
- [ ] **Validate theoretical limits** - Check behavior as asymmetry → 0

**Code Quality:**
- [ ] **Review asymmetric code** - Ensure code follows project standards
- [ ] **Add comprehensive comments** - Document asymmetric algorithms
- [ ] **Clean up debug code** - Remove temporary debugging artifacts
- [ ] **Optimize for maintainability** - Ensure code is readable and maintainable

## Implementation Strategy

### Priority Order

**Phase 1 (Immediate - Next 2 weeks):**
1. Fix any C++ binding issues with asymmetric mode
2. Implement symmetric-with-lasym=true test suite
3. Validate that zero asymmetric coefficients give identical results

**Phase 2 (Short-term - Next 1 month):**
1. Create reference asymmetric test cases with upstream VMEC2000
2. Implement asymmetric validation framework
3. Add true asymmetric physics tests

**Phase 3 (Medium-term - Next 2 months):**
1. Comprehensive physics validation
2. Performance optimization
3. Mathematical consistency checks

**Phase 4 (Long-term - Next 3 months):**
1. Integration testing
2. Documentation and examples
3. CI/CD setup

### Success Metrics

**Immediate Success (Phase 1):**
- [ ] All symmetric test cases pass with `lasym=true` and zero asymmetric coefficients
- [ ] Results match symmetric mode to machine precision
- [ ] No crashes or numerical instabilities

**Short-term Success (Phase 2):**
- [ ] At least 3 asymmetric test cases with upstream reference validation
- [ ] Asymmetric results match VMEC2000 within acceptable tolerance
- [ ] Complete test coverage for asymmetric functionality

**Long-term Success (Phases 3-4):**
- [ ] Comprehensive asymmetric physics validation
- [ ] Performance comparable to symmetric mode
- [ ] Full integration with SIMSOPT and other downstream tools
- [ ] Robust CI/CD pipeline for asymmetric testing

## Risk Management

**Technical Risks:**
- **Fourier transform bugs** - Systematic testing of transform accuracy
- **Memory management issues** - Careful validation of asymmetric array handling
- **Numerical precision problems** - Use appropriate tolerances and validation
- **Performance degradation** - Profile and optimize asymmetric code paths

**Project Risks:**
- **Scope creep** - Focus on core validation first, then expand
- **Resource constraints** - Prioritize most critical tests and features
- **Integration complexity** - Test integration points early and often
- **Upstream compatibility** - Maintain regular comparison with upstream VMEC2000

## Notes

**Key Files to Focus On:**
- `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.cc` - Core asymmetric physics
- `src/vmecpp/cpp/vmecpp/vmec/vmec/vmec_asymmetric_test.cc` - Existing C++ tests
- `tests/test_init.py` - Python test infrastructure
- `src/vmecpp/cpp/vmecpp/vmec/boundaries/guess_magnetic_axis.cc` - Asymmetric axis handling

**Test Data Management:**
- Store asymmetric reference data in `examples/data/asymmetric/`
- Use consistent naming convention: `*_asymmetric_ref.nc`
- Maintain both small and medium-sized test cases
- Document test case generation procedures

This comprehensive TODO provides a clear roadmap for validating asymmetric VMEC++ functionality against upstream VMEC2000, ensuring correctness and completeness of the asymmetric implementation.
