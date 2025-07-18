# Clean Commit Strategy for Asymmetric Fix

## Essential Changes to Keep

### 1. Critical Fix in C++
- **File**: `src/vmecpp/cpp/vmecpp/vmec/ideal_mhd_model/fourier_asymmetric.cc`
- **Lines**: 306-313 (zeta reflection logic)
- **Change**: Fix incorrect zeta reflection for axisymmetric cases

### 2. Python Asymmetric Array Initialization
- **File**: `src/vmecpp/__init__.py`
- **Changes**: Initialize asymmetric arrays (rbs, zbc) with zeros when lasym=True
- **Reason**: Prevents crashes when asymmetric mode is enabled

### 3. Test Infrastructure
- **Files**: `tests/test_asymmetric_*.py`
- **Reason**: Comprehensive test suite for asymmetric mode

## Changes to Revert

### 1. Debug Output (Already Reverted)
- ✅ `guess_magnetic_axis.cc` - std::cout statements
- ✅ `boundaries.cc` - debug output
- ✅ `fourier_geometry.cc` - debug output
- ✅ `ideal_mhd_model.cc` - Jacobian trace output
- ✅ `vmec.cc` - iteration tracking

### 2. Temporary Debug Scripts
- `debug_*.py` files
- `find_bad_jacobian.py`
- `simple_jacobian_debug.py`
- `test_jacobian_original.py`
- `test_workarounds.py`

### 3. Test Input Files
- `input.test`
- `threed1.cma`
- `cma.json`

## Minimal PR Strategy

### Option 1: Single Commit with Critical Fix Only
```bash
# Create new branch from upstream
git checkout -b asymmetric-zeta-fix upstream/main

# Cherry-pick only the zeta reflection fix
# Manually apply changes to fourier_asymmetric.cc (lines 306-313)

# Test thoroughly
# Create minimal test case demonstrating the fix
```

### Option 2: Two Commits
1. Fix zeta reflection bug in C++
2. Add Python initialization for asymmetric arrays

### Option 3: Three Commits
1. Fix zeta reflection bug in C++
2. Add Python initialization for asymmetric arrays
3. Add comprehensive test suite for asymmetric mode

## Next Steps

1. Create clean branch from upstream/main
2. Apply ONLY the essential changes
3. Test with minimal asymmetric case
4. Document the fix clearly in commit message
5. Prepare for upstream PR
