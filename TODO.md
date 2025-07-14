# TODO: Non-Stellarator-Symmetric Field Implementation

This document tracks the implementation progress of non-stellarator-symmetric field support (lasym=true) in VMECPP according to TOKAMAK.md.

## ✅ COMPLETED IMPLEMENTATION

**Core asymmetric physics implementation is complete and functional:**
- All asymmetric Fourier transforms implemented (totzspa, symrzl, symforce, tomnspa)
- Fixed critical segfault in SymmetrizeForces function for empty span access
- Resolved convergence logic and jacobian check ordering issues
- Asymmetric test cases run without crashing (segfault-free)
- Force symmetrization working correctly for both 2D and 3D cases

## Current Priority: Quantitative Validation Strategy

### Target Test Cases for Validation
1. **input.tok_asym** - Asymmetric tokamak (nfp=1, mpol=7, ntor=0)
2. **input.HELIOTRON_asym** - Asymmetric stellarator (nfp=19, mpol=5, ntor=3)

### Validation Strategy Implementation

#### Phase 1: Fix Boundary Configuration Issues
- [ ] **Analyze and fix tok_asym boundary configuration**
  - Current issue: "solver failed during first iterations" due to boundary shape
  - Use reference ../jVMEC/test data to identify correct boundary parameters
  - Fix boundary spectral condensation and initial shape issues
  - Validate convergence with proper boundary geometry

- [ ] **Analyze and fix HELIOTRON_asym boundary configuration**
  - Current issue: Same boundary shape problem as tok_asym
  - Cross-reference with ../educational_VMEC asymmetric test cases
  - Ensure proper axis positioning and boundary coefficients
  - Test convergence with corrected configuration

#### Phase 2: Quantitative Validation Using Existing Tools
- [ ] **Run validation using scripts/validate_asymmetric.py**
  - Fix boundary issues first to enable successful runs
  - Compare asymmetric coefficients (rmns, zmnc arrays) with reference
  - Validate force residuals and convergence patterns
  - Use tolerance-based comparison for numerical accuracy

- [ ] **C++ standalone validation**
  - Use ./build/vmec_standalone for direct C++ testing
  - Generate .out.h5 files for both test cases
  - Compare HDF5 outputs with reference data
  - Validate asymmetric arrays and convergence metrics

- [ ] **Python validation via vmecpp.run()**
  - Test both test cases through Python interface
  - Validate VmecOutput.wout asymmetric arrays
  - Compare with reference wout files using existing CompareWOut() function
  - Generate comparison reports

#### Phase 3: Systematic Validation
- [ ] **Reference data analysis**
  - Extract reference values from examples/data/wout_tok_asym.nc
  - Extract reference values from examples/data/wout_HELIOTRON_asym.nc
  - Document expected asymmetric coefficient patterns
  - Set up tolerance-based comparison framework

- [ ] **Convergence validation**
  - Validate iteration count and convergence patterns
  - Compare force residual evolution (fsqr, fsqz, fsql)
  - Check magnetic axis positioning and geometry
  - Validate physical quantities (beta, rotational transform)

- [ ] **Asymmetric coefficient validation**
  - Compare rmns arrays (asymmetric R coefficients)
  - Compare zmnc arrays (asymmetric Z coefficients)
  - Compare bmns arrays (asymmetric B-field components)
  - Validate non-zero asymmetric contributions where expected

#### Phase 4: Automated Testing Integration
- [ ] **C++ test suite validation**
  - Fix Bazel configuration issues for vmec_asymmetric_test.cc
  - Run automated tests with tolerance-based comparison
  - Integrate tests into CI/CD pipeline
  - Generate test reports for asymmetric validation

- [ ] **Python test suite validation**
  - Extend existing Python tests to include full run validation
  - Test both test cases through pytest framework
  - Validate against reference data automatically
  - Generate coverage reports for asymmetric code paths

### Success Criteria
- [ ] **tok_asym**: Converges and matches reference fsqr, asymmetric coefficients
- [ ] **HELIOTRON_asym**: Converges and matches reference behavior
- [ ] **Automated tests**: Pass with tolerance-based comparison
- [ ] **Zero crashes**: No segfaults or runtime errors during validation
- [ ] **Performance**: Comparable iteration counts to reference VMEC

## Implementation Notes

- Follow Google C++ Style Guide with physics domain adaptations
- Preserve traditional physics variable names
- Use ASCII characters only (no Unicode)
- Make incremental, testable changes
- Run pre-commit hooks before committing

## Historical Context (Completed Work)

**Previous major accomplishments:**
- Core asymmetric Fourier transforms implemented (totzspa, symrzl, symforce, tomnspa)
- Fixed geometry doubling bug in SymmetrizeRealSpaceGeometry
- Fixed convergence logic bug (jacobian check ordering)
- Fixed segfault in SymmetrizeForces for empty span access
- Added comprehensive test infrastructure
- Validated against reference behavior patterns from jVMEC
- Asymmetric input validation and array initialization working
- C++ pybind11 binding issues resolved
- Zero-crash policy maintained for physics computation