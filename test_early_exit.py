import json

# Create test with very loose tolerance to converge quickly
config = {
    "lasym": True,
    "nfp": 19,
    "mpol": 5,
    "ntor": 3,
    "ns_array": [5],
    "ftol_array": [1e-1],  # Very loose to converge quickly
    "niter_array": [50],   # Few iterations
    "delt": 0.9,
    "tcon0": 1.0,
    "aphi": [1.0],
    "phiedge": 1.0,
    "pmass_type": "power_series",
    "am": [1.0, -2.0, 1.0],
    "pres_scale": 18000.0,
    "gamma": 0.0,
    "spres_ped": 1.0,
    "ncurr": 0,
    "piota_type": "power_series",
    "ai": [1.0, 1.5],
    "lfreeb": False,
    "mgrid_file": "none",
    "raxis_c": [10.0, 0.0, 0.0, 0.0],
    "zaxis_s": [0.0, 0.0, 0.0, 0.0],
    "raxis_s": [0.0, 0.0, 0.0, 0.0],
    "zaxis_c": [0.0, 0.0, 0.0, 0.0],
    "rbc": [
        {"n": 0, "m": 0, "value": 10.0},
        {"n": -1, "m": 1, "value": -0.3},
        {"n": 0, "m": 1, "value": -1.0}
    ],
    "zbs": [
        {"n": -1, "m": 1, "value": -0.3},
        {"n": 0, "m": 1, "value": 1.0}
    ]
}

with open('test_early_exit.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Testing with early exit...")