# TODO: VMEC++ Open Tasks

## Asymmetric Implementation

### 1. Improve Axis Recomputation Robustness
- Some challenging asymmetric configurations fail with "INITIAL JACOBIAN CHANGED SIGN!" 
- Need more sophisticated axis search strategies for edge cases

### 2. Free Boundary Asymmetric Support
- Implement asymmetric terms in NESTOR vacuum solver
- Update surface_geometry.cc and laplace_solver.cc

### 3. Memory Optimization
- Make asymmetric arrays optional when lasym=false
- Low priority performance optimization