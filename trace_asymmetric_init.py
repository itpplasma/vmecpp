#!/usr/bin/env python3
"""Trace asymmetric coefficient initialization step by step."""

import vmecpp
import numpy as np

# Create a simple 2D asymmetric test case
vmec_input = vmecpp.VmecInput.from_file("examples/data/input.up_down_asymmetric_tokamak")

# Reduce to minimal setup
vmec_input.ns_array = np.array([5], dtype=np.int64)  # Very small grid
vmec_input.niter_array = np.array([1], dtype=np.int64)
vmec_input.mpol = 3  # Fewer modes
vmec_input.return_outputs_even_if_not_converged = True

# Reduce asymmetry to help convergence
vmec_input.rbs[1, 0] = 0.1  # Reduce from 0.6
vmec_input.rbs[2, 0] = 0.02  # Reduce from 0.12
vmec_input.zbs[1, 0] = 0.1  # Reduce from 0.6

print("=== TRACING ASYMMETRIC INITIALIZATION ===\n")
print(f"Configuration: lasym={vmec_input.lasym}, ntor={vmec_input.ntor}, mpol={vmec_input.mpol}, ns={vmec_input.ns_array[0]}")
print(f"\nBoundary coefficients:")
print(f"  RBC(0,0) = {vmec_input.rbc[0,0]}")
print(f"  RBC(1,0) = {vmec_input.rbc[1,0]}")
print(f"  RBS(1,0) = {vmec_input.rbs[1,0]}")
print(f"  RBS(2,0) = {vmec_input.rbs[2,0]}")
print(f"  ZBS(1,0) = {vmec_input.zbs[1,0]}")

try:
    result = vmecpp.run(vmec_input, verbose=True)
    print("\nRun completed!")
except RuntimeError as e:
    print(f"\nFailed: {e}")
    
print("\nDone.")