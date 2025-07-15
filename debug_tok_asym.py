#!/usr/bin/env python3
import vmecpp
import traceback

print("Debugging tok_asym segfault step by step...")

print("\n1. Testing input file loading...")
try:
    input_data = vmecpp.VmecInput.from_file("examples/data/tok_asym.json")
    print(f"   ✅ Input loaded successfully")
    print(f"   lasym = {input_data.lasym}")
    print(f"   nfp = {input_data.nfp}")
    print(f"   mpol = {input_data.mpol}")
    print(f"   ntor = {input_data.ntor}")
    print(f"   ns_array = {input_data.ns_array}")
except Exception as e:
    print(f"   ❌ Input loading failed: {e}")
    traceback.print_exc()
    exit(1)

print("\n2. Testing minimal run (1 iteration)...")
try:
    input_data.niter_array = [1]
    input_data.ftol_array = [1e-6]
    print(f"   Starting run with niter={input_data.niter_array[0]}...")
    output = vmecpp.run(input_data, verbose=True)
    print(f"   ✅ Minimal run successful")
except Exception as e:
    print(f"   ❌ Minimal run failed: {e}")
    traceback.print_exc()

print("\n3. Analyzing input parameters...")
print(f"   Boundary coefficients:")
print(f"     rbc shape: {getattr(input_data, 'rbc', 'None')}")
print(f"     zbs shape: {getattr(input_data, 'zbs', 'None')}")
print(f"     rbs shape: {getattr(input_data, 'rbs', 'None')}")  
print(f"     zbc shape: {getattr(input_data, 'zbc', 'None')}")
print(f"   Axis coefficients:")
print(f"     raxis_c: {getattr(input_data, 'raxis_c', 'None')}")
print(f"     zaxis_s: {getattr(input_data, 'zaxis_s', 'None')}")
print(f"     raxis_s: {getattr(input_data, 'raxis_s', 'None')}")
print(f"     zaxis_c: {getattr(input_data, 'zaxis_c', 'None')}")