# TODO: Non-Stellarator-Symmetric Field Implementation

This document tracks the implementation progress of non-stellarator-symmetric field support (lasym=true) in VMECPP according to TOKAMAK.md.

## High Priority Tasks

- [x] **Implement totzspa function for anti-symmetric Fourier transforms**
  - Add to fourier transform module to handle asymmetric contributions
  - Transform asymmetric Fourier coefficients (rmnsc, zmncc, lmncc, rmncs, zmnss, lmnss) to real space
  
- [x] **Implement symrzl function to extend geometry from [0,π] to [0,2π]**
  - Use reflection operations to combine symmetric and antisymmetric pieces
  - Symmetrize/antisymmetrize real-space quantities on extended theta interval
  
- [x] **Implement symforce function to symmetrize forces in u-v space**
  - Separate forces into symmetric and antisymmetric components
  - Critical for non-stellarator-symmetric equilibria
  
- [x] **Implement tomnspa function for inverse transform of antisymmetric forces**
  - Fourier transform antisymmetric forces back to spectral space
  
- [x] **Add mode scaling with sqrt(s) for odd-m modes in radial transformations**
  - Implement Equation (8c) from Hirshman, Schwenn & Nührenberg (1990)
  - Scale odd-m modes by 1/sqrt(s) to regularize radial derivatives
  
- [x] **Complete force calculations for lasym=true in vmec.cc (TODO items)**
  - Address TODO comments at lines 1384 and 1405
  - Implement asymmetric force terms
  
- [x] **Implement symoutput for output processing with lasym=true**
  - Address TODO at output_quantities.cc:4572
  - Symmetrize output quantities like B-field components

- [x] **Fix Python validation for asymmetric input fields**
  - Fixed VmecInput validation to initialize rbs/zbc arrays when lasym=True
  - Fixed assertion logic for asymmetric field handling

- [x] **Fix C++ array allocation for asymmetric fields**
  - Fixed VmecInput validation to initialize raxis_s/zaxis_c arrays when lasym=True
  - Added _validate_axis_coefficients_shapes method for proper axis array handling
  - Added resize_axis_coeff utility function for 1D coefficient arrays
  - Python-to-C++ conversion now works correctly for asymmetric configurations

- [ ] **Debug C++ segmentation fault in indata2json for asymmetric input files**
  - Crash occurs when loading input.HELIOTRON_asym and input.tok_asym
  - Likely issue in C++ boundary coefficient parsing for asymmetric cases

## Medium Priority Tasks

- [ ] **Add tokamak test case (input.tok_asym) from jVMEC**
  - Tokamak configuration with lasym=true, nfp=1, mpol=7, ntor=0
  - Include asymmetric boundary coefficients
  
- [ ] **Add HELIOTRON asymmetric test case from jVMEC**
  - Stellarator with lasym=true, nfp=19, mpol=5, ntor=3
  - Include reference outputs for validation

- [ ] **Add comprehensive tests for lasym=true configurations**
  - Unit tests for new functions  
  - Integration tests for asymmetric equilibria (manual testing works)

## Low Priority Tasks

- [ ] **Optimize memory allocation for optional asymmetric coefficient arrays**
  - Make raxis_s, zaxis_c, rbs, zbc optional (TODO items in vmec_indata.h)
  - Allocate only when lasym=true

## Final Validation

- [ ] **Run comprehensive tests and fix any issues**
  - Validate against jVMEC and educational VMEC results
  - Performance benchmarking for asymmetric vs symmetric cases
  - Ensure zero-crash policy maintained

## Current Status (✅ Major Progress Made)

**Core Algorithm Implementation: COMPLETE**
- All key asymmetric Fourier transforms implemented (totzspa, symrzl, tomnspa, symforce, symoutput)
- Mode scaling with sqrt(s) for odd-m modes implemented
- Asymmetric force calculations integrated into vmec.cc
- Python validation fixed for asymmetric fields

**Remaining Work: Infrastructure Fixes**
- C++ indata2json parser crash for asymmetric input files
- Test infrastructure once C++ issues resolved

**Manual Testing Status:**
- ✅ Python asymmetric validation works
- ✅ Asymmetric arrays properly initialized when lasym=True
- ✅ Python-to-C++ conversion works for asymmetric configurations
- ❌ C++ indata2json parser needs fixing for asymmetric input files

## Implementation Notes

- Follow Google C++ Style Guide with physics domain adaptations
- Preserve traditional physics variable names
- Use ASCII characters only (no Unicode)
- Make incremental, testable changes
- Run pre-commit hooks before committing