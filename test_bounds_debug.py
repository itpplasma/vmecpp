import json

# Create minimal asymmetric test that crashes quickly
config = {
    "lasym": True,
    "nfp": 1,  # Minimal complexity
    "mpol": 3,
    "ntor": 0,  # No toroidal modes
    "ns_array": [3],  # Minimal grid
    "ftol_array": [1e-2],  # Very loose tolerance
    "niter_array": [5],   # Very few iterations
    "delt": 0.9,
    "tcon0": 1.0,
    "aphi": [1.0],
    "phiedge": 1.0,
    "pmass_type": "power_series",
    "am": [1.0],
    "pres_scale": 1000.0,
    "gamma": 0.0,
    "ncurr": 0,
    "piota_type": "power_series", 
    "ai": [1.0],
    "lfreeb": False,
    "mgrid_file": "none",
    "raxis_c": [10.0],
    "zaxis_s": [0.0],
    "raxis_s": [0.0],
    "zaxis_c": [0.0],
    "rbc": [
        {"n": 0, "m": 0, "value": 10.0},
        {"n": 0, "m": 1, "value": -1.0}
    ],
    "zbs": [
        {"n": 0, "m": 1, "value": 1.0}
    ],
    "rbs": [],
    "zbc": []
}

with open('test_bounds_debug.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Testing minimal asymmetric case for bounds debugging...")