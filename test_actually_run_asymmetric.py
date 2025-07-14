#!/usr/bin/env python3
"""
Test actually running asymmetric VMEC case.
"""
import pytest
import vmecpp

def test_run_asymmetric():
    """Test running asymmetric tokamak."""
    vmec_input = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    vmec_input.ns_array = [3]
    vmec_input.ftol_array = [1e-6]
    vmec_input.niter_array = [10]
    
    output = vmecpp.run(vmec_input, verbose=False)
    assert output is not None
    print(f"Converged: {output.success}")

if __name__ == "__main__":
    test_run_asymmetric()