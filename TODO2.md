# TODO2.md - Clean Asymmetric Mode Implementation Plan

## Current State Analysis

### Current Branch: `asym`
- **Based on**: PR 360 (`97cb87f Address jurasic-pf review comments`)
- **Status**: Successfully rebased onto PR 360 with critical bug fixes
- **Key Achievement**: Fixed axis recovery algorithm tie-breaking logic to match educational_VMEC

### Key Findings from Analysis

1. **CRITICAL ISSUE IDENTIFIED**: Asymmetric inverse DFT functionality is completely missing
   - Current code aborts with `exit(-1)` when `lasym=true`
   - Missing functions: `dft_FourierToReal_3d_asymm()`, `dft_FourierToReal_2d_asymm()`
   - No `fourier_asymmetric.cc` file exists in codebase

2. **Successful Fixes Applied**:
   - ✅ Axis recovery tie-breaking logic now matches educational_VMEC exactly
   - ✅ Grid search algorithm produces 98% improvement in Z-axis positioning
   - ✅ Rebased onto PR 360 with critical bug fixes (Python wrapper, output quantities)

3. **Current Test Result**:
   - `python -m vmecpp examples/data/input.up_down_asymmetric_tokamak` → **ABORTS**
   - Error: `asymmetric inv-DFT not implemented yet` → `exit(-1)`

## Root Cause Analysis

### Why Asymmetric Mode Fails
The fundamental issue is in `ideal_mhd_model.cc:geometryFromFourier()`:

```cpp
if (s_.lasym) {
  // FIXME(jons): implement non-symmetric DFT variants
  std::cerr << "asymmetric inv-DFT not implemented yet\n";
  // FIXME(jons): implement symrzl
  std::cerr << "symrzl not implemented yet\n";
  abort();  // Program terminates here
}
```

### Missing Implementation Components

1. **Asymmetric Fourier Transform Functions** (NOT IMPLEMENTED):
   - `dft_FourierToReal_3d_asymm()` - Transform asymmetric Fourier → real space
   - `dft_FourierToReal_2d_asymm()` - Transform asymmetric Fourier → real space (2D)
   - `symrzl()` - Symmetrization operation for asymmetric mode

2. **Missing Files**:
   - `fourier_asymmetric.cc` - Core asymmetric DFT implementation
   - `fourier_asymmetric.h` - Header for asymmetric DFT functions

3. **Integration Points**:
   - `ideal_mhd_model.cc` - Remove abort(), add asymmetric DFT calls
   - Build system integration for new asymmetric files

## Implementation Strategy

### Phase 1: Cherry-Pick from origin/main (HIGHEST PRIORITY)
1. **Analyze Commit History**:
   - Review all commits in `origin/main` since `prepare-asym`
   - Identify commits that implement asymmetric functionality
   - Focus on asymmetric DFT implementations, fourier_asymmetric.cc, ideal_mhd_model changes

2. **Systematic Cherry-Picking Process**:
   - Start from current `asym` branch (based on PR 360)
   - `git log --oneline prepare-asym..origin/main` to see all commits
   - For each commit, analyze if it contains asymmetric functionality:
     - Check commit message for "asymmetric", "lasym", "DFT", "fourier"
     - `git show <commit>` to examine changes
     - Look for `fourier_asymmetric.cc`, `ideal_mhd_model.cc` modifications
   - Cherry-pick relevant commits: `git cherry-pick <commit-hash>`
   - Resolve conflicts maintaining our axis recovery fixes

3. **Expected Asymmetric Commits to Find**:
   - Implementation of `fourier_asymmetric.cc` with DFT functions
   - Updates to `ideal_mhd_model.cc` removing the `abort()` call
   - Build system updates for asymmetric files
   - Any symrzl implementation

4. **Cherry-Pick Strategy**:
   ```bash
   # From asym branch
   git log --oneline prepare-asym..origin/main --grep="asymmetric\|lasym\|DFT\|fourier"
   git log --oneline prepare-asym..origin/main --all --grep="fourier_asymmetric"
   git log --oneline prepare-asym..origin/main -- "*fourier*" "*asymm*"

   # For each relevant commit:
   git show <commit-hash>  # Review changes
   git cherry-pick <commit-hash>  # Apply if asymmetric-related
   ```

### Phase 2: Research and Analysis (High Priority)
1. **Study Educational VMEC Implementation**:
   - Analyze `educational_VMEC/src/` asymmetric DFT functions
   - Document mathematical operations and data flow
   - Identify key differences from symmetric DFT

2. **Study jVMEC Implementation**:
   - Cross-reference with jVMEC asymmetric handling
   - Ensure consistency in mathematical approach

3. **Document Required Functions**:
   - Create detailed specifications for each missing function
   - Define input/output interfaces
   - Map data dependencies

### Phase 3: Core Implementation (High Priority)
1. **Create `fourier_asymmetric.cc`**:
   - Implement `FourierToReal3DAsymmFastPoloidal()`
   - Implement `FourierToReal2DAsymmFastPoloidal()`
   - Implement `RealToFourier3DAsymmFastPoloidal()`
   - Implement `RealToFourier2DAsymmFastPoloidal()`
   - Implement `symrzl()` symmetrization

2. **Create `fourier_asymmetric.h`**:
   - Function declarations
   - Include guards
   - Documentation

3. **Update `ideal_mhd_model.cc`**:
   - Remove `abort()` call
   - Add asymmetric DFT function calls
   - Add asymmetric force handling

4. **Update Build System**:
   - Add new files to CMake
   - Update includes and dependencies

### Phase 4: Testing and Validation (Medium Priority)
1. **Basic Functionality Test**:
   - Test with `input.up_down_asymmetric_tokamak`
   - Verify no crashes, basic convergence

2. **Cross-Implementation Validation**:
   - Compare output with educational_VMEC
   - Compare output with jVMEC
   - Validate convergence rates

3. **Comprehensive Testing**:
   - Test all 27 asymmetric inputs from educational_VMEC
   - Achieve 100% pass rate
   - Performance benchmarking

## Clean Implementation Approach

### Minimize Changes from Base (PR 360)
1. **Preserve PR 360 Improvements**:
   - Keep Python wrapper bug fixes
   - Keep output quantities indexing fixes
   - Keep test infrastructure

2. **Add Only Essential Changes**:
   - New asymmetric DFT files (`fourier_asymmetric.cc/h`)
   - Minimal changes to `ideal_mhd_model.cc` (remove abort, add calls)
   - Build system updates

3. **Maintain Clean History**:
   - Each logical change in separate commit
   - Clear commit messages explaining the purpose
   - No debug output in final commits

### Cherry-Pick Strategy from Our Work

**Keep These Changes**:
- ✅ Axis recovery tie-breaking logic fix (proven correct)
- ✅ Clean comment updates explaining the algorithm
- ✅ Documentation in `../benchmark_vmec/design/` (valuable analysis)

**Remove These Changes**:
- ❌ Temporary analysis files
- ❌ Duplicate input files

**Keep These Changes (For Now)**:
- ✅ Debug output in `guess_magnetic_axis.cc` (KEEP for development and debugging)
- ✅ All analysis and diagnostic information

## Development Workflow

### Step 1: Cherry-Pick Phase (IMMEDIATE PRIORITY)
1. **Search for Asymmetric Commits in origin/main**:
   ```bash
   git log --oneline prepare-asym..origin/main --grep="asymmetric\|lasym\|DFT\|fourier"
   git log --oneline prepare-asym..origin/main -- "*fourier*" "*asymm*" "*ideal_mhd*"
   ```
2. **Review Each Potential Commit**:
   - `git show <commit-hash>` to examine changes
   - Look for `fourier_asymmetric.cc`, `ideal_mhd_model.cc` modifications
   - Check if it removes the `abort()` call for asymmetric mode
3. **Cherry-Pick Relevant Commits**:
   - `git cherry-pick <commit-hash>` for each asymmetric implementation
   - Resolve conflicts while preserving our axis recovery fixes
   - Test after each cherry-pick to ensure no regressions

### Step 2: Analysis Phase
1. Study educational_VMEC asymmetric DFT implementation
2. Study jVMEC asymmetric implementation
3. Document required functions and interfaces
4. Create implementation specifications

### Step 3: Implementation Phase (if needed after cherry-picking)
1. Create `fourier_asymmetric.cc` with core functions (if not found in origin/main)
2. Create `fourier_asymmetric.h` with declarations (if not found in origin/main)
3. Update `ideal_mhd_model.cc` to use asymmetric functions (if not found in origin/main)
4. Update build system (if not found in origin/main)

### Step 4: Testing Phase
1. Test basic functionality (no crashes)
2. Test convergence on simple asymmetric case
3. Cross-validate with educational_VMEC
4. Comprehensive testing on all 27 asymmetric inputs

### Step 5: Validation Phase (NOT Clean Up - Keep Debug Output)
1. **KEEP debug output for development**
2. Validate commit history is clean
3. Update documentation
4. Final testing and validation

## Success Criteria

### Immediate Goals
- [ ] No crashes when running asymmetric inputs
- [ ] Basic convergence on `input.up_down_asymmetric_tokamak`
- [ ] Output matches educational_VMEC within reasonable tolerance

### Long-term Goals
- [ ] 100% pass rate on all 27 asymmetric inputs from educational_VMEC
- [ ] Convergence rates competitive with educational_VMEC
- [ ] Clean, maintainable code WITH debug output preserved for development
- [ ] Comprehensive documentation

## Risk Assessment

### High Risk
- **Complexity**: Asymmetric DFT implementation is mathematically complex
- **Integration**: Multiple components must work together correctly
- **Testing**: Requires extensive validation against reference implementations

### Mitigation Strategies
- **Incremental Development**: Build and test each component separately
- **Cross-Validation**: Compare with multiple reference implementations
- **Extensive Testing**: Test on comprehensive suite of asymmetric inputs
- **Documentation**: Maintain detailed documentation of all changes

## Conclusion

The path to working asymmetric mode is clear but requires implementing the missing asymmetric DFT functionality. Our current branch has a solid foundation with the axis recovery fixes and PR 360 improvements. The next phase requires focused implementation of the missing asymmetric Fourier transform functions.

**Current Status**: 🟡 Foundation Ready, Cherry-Pick Phase Required
**Next Step**: Cherry-pick asymmetric commits from origin/main
**Timeline**: Cherry-pick phase (immediate), then implementation if needed
**Risk Level**: Medium (cherry-picking) to Medium-High (if implementation needed)
