#!/usr/bin/env python3
import json
import os

# Create minimal test case that reproduces Eigen error
config = {
    "lasym": True,
    "nfp": 19,
    "mpol": 5,
    "ntor": 3,
    "ns_array": [5],
    "ftol_array": [1e-4],
    "niter_array": [600],
    "delt": 0.9,
    "tcon0": 1.0,
    "aphi": [1.0],
    "rbc": [[1.0] + [0.0]*6 for _ in range(10)],
    "zbs": [[0.0]*7 for _ in range(10)],
    "rbs": [[0.0]*7 for _ in range(10)],
    "zbc": [[0.0]*7 for _ in range(10)]
}

with open('debug_eigen.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Running debug case with GDB to find exact crash location...")