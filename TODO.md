# TODO: Non-Stellarator-Symmetric Field Implementation

This document tracks the implementation progress of non-stellarator-symmetric field support (lasym=true) in VMECPP according to TOKAMAK.md.

## High Priority Tasks

- [x] **Implement totzspa function for anti-symmetric Fourier transforms**
  - Add to fourier transform module to handle asymmetric contributions
  - Transform asymmetric Fourier coefficients (rmnsc, zmncc, lmncc, rmncs, zmnss, lmnss) to real space
  
- [x] **Implement symrzl function to extend geometry from [0,π] to [0,2π]**
  - Use reflection operations to combine symmetric and antisymmetric pieces
  - Symmetrize/antisymmetrize real-space quantities on extended theta interval
  
- [ ] **Implement symforce function to symmetrize forces in u-v space**
  - Separate forces into symmetric and antisymmetric components
  - Critical for non-stellarator-symmetric equilibria
  
- [x] **Implement tomnspa function for inverse transform of antisymmetric forces**
  - Fourier transform antisymmetric forces back to spectral space
  
- [x] **Add mode scaling with sqrt(s) for odd-m modes in radial transformations**
  - Implement Equation (8c) from Hirshman, Schwenn & Nührenberg (1990)
  - Scale odd-m modes by 1/sqrt(s) to regularize radial derivatives
  
- [ ] **Complete force calculations for lasym=true in vmec.cc (TODO items)**
  - Address TODO comments at lines 1384 and 1405
  - Implement asymmetric force terms
  
- [ ] **Implement symoutput for output processing with lasym=true**
  - Address TODO at output_quantities.cc:4572
  - Symmetrize output quantities like B-field components
  
- [ ] **Add comprehensive tests for lasym=true configurations**
  - Unit tests for new functions
  - Integration tests for asymmetric equilibria

## Medium Priority Tasks

- [ ] **Add tokamak test case (input.tok_asym) from jVMEC**
  - Tokamak configuration with lasym=true, nfp=1, mpol=7, ntor=0
  - Include asymmetric boundary coefficients
  
- [ ] **Add HELIOTRON asymmetric test case from jVMEC**
  - Stellarator with lasym=true, nfp=19, mpol=5, ntor=3
  - Include reference outputs for validation

## Low Priority Tasks

- [ ] **Optimize memory allocation for optional asymmetric coefficient arrays**
  - Make raxis_s, zaxis_c, rbs, zbc optional (TODO items in vmec_indata.h)
  - Allocate only when lasym=true

## Final Validation

- [ ] **Run comprehensive tests and fix any issues**
  - Validate against jVMEC and educational VMEC results
  - Performance benchmarking for asymmetric vs symmetric cases
  - Ensure zero-crash policy maintained

## Implementation Notes

- Follow Google C++ Style Guide with physics domain adaptations
- Preserve traditional physics variable names
- Use ASCII characters only (no Unicode)
- Make incremental, testable changes
- Run pre-commit hooks before committing