#!/usr/bin/env python3
"""
Test script to verify the import fix for extract_cs_conditions.
"""

import sys
import os
import tempfile
import pandas as pd

def test_imports():
    """Test that all required imports work."""
    try:
        from create_1st_voxelWise import get_condition_names_from_events
        from first_level_workflows import extract_cs_conditions, create_interesting_contrasts
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_integration():
    """Test the integration between the two modules."""
    try:
        from create_1st_voxelWise import get_condition_names_from_events
        from first_level_workflows import extract_cs_conditions
        
        # Create a dummy events file
        dummy_events = pd.DataFrame({
            'onset': [0, 2, 4, 6, 8],
            'duration': [1, 1, 1, 1, 1],
            'trial_type': ['CS-', 'CSS', 'CSR', 'FIXATION', 'CS-']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            dummy_events.to_csv(f.name, index=False)
            events_file = f.name
        
        # Test the integration
        contrasts, cs, css, csr, other, names = get_condition_names_from_events(events_file)
        print(f"✓ Integration test successful: {len(contrasts)} contrasts generated")
        
        # Clean up
        os.unlink(events_file)
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing import fix for extract_cs_conditions...")
    print("=" * 50)
    
    success = True
    
    print("1. Testing imports...")
    success &= test_imports()
    
    print("\n2. Testing integration...")
    success &= test_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! The import fix is working.")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    sys.exit(0 if success else 1)
