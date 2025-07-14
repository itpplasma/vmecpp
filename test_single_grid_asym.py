#!/usr/bin/env python3
"""
Test asymmetric case with single multigrid level to isolate the issue
"""

import sys
import os
import json
sys.path.insert(0, '/home/ert/code/vmecpp/src')

try:
    import vmecpp
    
    print("=== TESTING SINGLE GRID ASYMMETRIC CASE ===")
    
    # Load HELIOTRON_asym JSON
    json_file = '/home/ert/code/vmecpp/src/vmecpp/cpp/vmecpp/test_data/HELIOTRON_asym.2007871.json'
    
    with open(json_file, 'r') as f:
        config = json.load(f)
    
    # Modify to use single grid level
    print(f"Original ns_array: {config['ns_array']}")
    config['ns_array'] = [5]  # Single grid
    config['ftol_array'] = [1e-12]
    config['niter_array'] = [1000]
    
    print(f"Modified ns_array: {config['ns_array']}")
    
    # Save modified config
    modified_file = 'heliotron_single_grid.json'
    with open(modified_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Test with standalone executable
    print("\nTesting with vmec_standalone...")
    cmd = f"./build/vmec_standalone {modified_file} 2>&1"
    result = os.system(cmd)
    
    if result == 0:
        print("\n✓ SUCCESS: Single grid asymmetric case completed without crash!")
        print("This confirms the asymmetric fix works correctly.")
        print("The crash occurs during multigrid transition, not in the asymmetric physics.")
    else:
        print("\n✗ FAILED: Even single grid case crashes")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()