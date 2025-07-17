#!/usr/bin/env python3


import vmecpp

print("Loading input...")
input_data = vmecpp.VmecInput.from_file(
    "examples/data/input.up_down_asymmetric_tokamak"
)
print("Running VMEC++...")
try:
    output = vmecpp.run(input_data)
    print("VMEC++ succeeded")
except Exception as e:
    print(f"VMEC++ failed: {e}")
    import traceback

    traceback.print_exc()
