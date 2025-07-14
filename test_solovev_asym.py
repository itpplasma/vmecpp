#!/usr/bin/env python3
"""
Test asymmetric mode with simple solovev case
"""

import sys
import os
import json
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    
    print("=== TESTING SOLOVEV WITH ASYMMETRIC MODE ===")
    
    # Load solovev JSON (known to work in symmetric mode)
    json_file = '/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/solovev.json'
    
    with open(json_file, 'r') as f:
        config = json.load(f)
    
    # Add lasym flag
    print(f"Original lasym: {config.get('lasym', False)}")
    config['lasym'] = True
    print(f"Modified lasym: {config['lasym']}")
    
    # Single grid for simplicity
    config['ns_array'] = [5]
    config['ftol_array'] = [1e-8]
    config['niter_array'] = [100]
    
    # Save modified config
    modified_file = 'solovev_asym.json'
    with open(modified_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Test with standalone executable
    print("\nTesting with vmec_standalone...")
    cmd = f"./build/vmec_standalone {modified_file} 2>&1 | head -50"
    os.system(cmd)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()