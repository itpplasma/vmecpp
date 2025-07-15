#!/usr/bin/env python3
import vmecpp

print("Loading input...")
input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
print(f"Loaded: lasym={input_data.lasym}, ntor={input_data.ntor}")

input_data.niter_array = [1]
input_data.ftol_array = [1e-6]

print("Running...")
output = vmecpp.run(input_data, verbose=False)
print("SUCCESS!")