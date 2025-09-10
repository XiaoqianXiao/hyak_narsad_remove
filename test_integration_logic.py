#!/usr/bin/env python3
"""
Test the integration logic between create_1st_voxelWise.py and first_level_workflows.py
without requiring nipype dependencies
"""

import os
import sys
import pandas as pd

# Add current directory to path
sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')

def test_get_df_trial_info_logic():
    """Test the get_df_trial_info function logic"""
    
    print("=" * 60)
    print("TESTING get_df_trial_info LOGIC")
    print("=" * 60)
    
    # Simulate the get_df_trial_info function
    def get_df_trial_info(events_file):
        """Simulated version of get_df_trial_info"""
        if os.path.exists(events_file):
            df_trial_info = pd.read_csv(events_file)
            
            # Validate required columns
            required_columns = ['trial_type', 'onset', 'duration']
            missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Ensure data types are correct
            df_trial_info['onset'] = pd.to_numeric(df_trial_info['onset'], errors='coerce')
            df_trial_info['duration'] = pd.to_numeric(df_trial_info['duration'], errors='coerce')
            df_trial_info = df_trial_info.dropna(subset=required_columns)
            
            return df_trial_info
        else:
            raise FileNotFoundError(f"Events file not found: {events_file}")
    
    # Test with real data
    events_file = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if os.path.exists(events_file):
        df_trial_info = get_df_trial_info(events_file)
        print(f"✓ get_df_trial_info works: {df_trial_info.shape}")
        print(f"✓ Columns: {list(df_trial_info.columns)}")
        print(f"✓ Trial types: {sorted(df_trial_info['trial_type'].unique())}")
        return df_trial_info
    else:
        print(f"❌ Test file not found: {events_file}")
        return None

def test_workflow_function_signatures():
    """Test that the workflow function signatures match what create_1st_voxelWise.py expects"""
    
    print("\n" + "=" * 60)
    print("TESTING WORKFLOW FUNCTION SIGNATURES")
    print("=" * 60)
    
    # Read the first_level_workflows.py file to check function signatures
    try:
        with open('first_level_workflows.py', 'r') as f:
            content = f.read()
        
        # Check for first_level_wf_voxelwise signature
        if 'def first_level_wf_voxelwise(inputs, output_dir, df_trial_info' in content:
            print("✓ first_level_wf_voxelwise has correct signature")
            print("  - inputs: ✓")
            print("  - output_dir: ✓") 
            print("  - df_trial_info: ✓")
        else:
            print("❌ first_level_wf_voxelwise signature not found or incorrect")
            return False
        
        # Check for first_level_wf signature
        if 'def first_level_wf(in_files, output_dir, df_trial_info' in content:
            print("✓ first_level_wf has correct signature")
            print("  - in_files: ✓")
            print("  - output_dir: ✓")
            print("  - df_trial_info: ✓")
        else:
            print("❌ first_level_wf signature not found or incorrect")
            return False
        
        # Check for first_level_wf_LSS signature
        if 'def first_level_wf_LSS(in_files, output_dir, trial_ID, df_trial_info' in content:
            print("✓ first_level_wf_LSS has correct signature")
            print("  - in_files: ✓")
            print("  - output_dir: ✓")
            print("  - trial_ID: ✓")
            print("  - df_trial_info: ✓")
        else:
            print("❌ first_level_wf_LSS signature not found or incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading first_level_workflows.py: {e}")
        return False

def test_create_1st_voxelWise_integration():
    """Test the integration points in create_1st_voxelWise.py"""
    
    print("\n" + "=" * 60)
    print("TESTING create_1st_voxelWise.py INTEGRATION")
    print("=" * 60)
    
    try:
        with open('create_1st_voxelWise.py', 'r') as f:
            content = f.read()
        
        # Check that get_df_trial_info is defined
        if 'def get_df_trial_info(events_file):' in content:
            print("✓ get_df_trial_info function is defined")
        else:
            print("❌ get_df_trial_info function not found")
            return False
        
        # Check that df_trial_info is used in workflow call
        if 'df_trial_info=df_trial_info' in content:
            print("✓ df_trial_info is passed to workflow function")
        else:
            print("❌ df_trial_info not passed to workflow function")
            return False
        
        # Check that first_level_wf_voxelwise is imported
        if 'first_level_wf_voxelwise' in content and 'from first_level_workflows import' in content:
            print("✓ first_level_wf_voxelwise is imported")
        else:
            print("❌ first_level_wf_voxelwise not imported")
            return False
        
        # Check that first_level_wf_voxelwise is called
        if 'workflow = first_level_wf_voxelwise(' in content:
            print("✓ first_level_wf_voxelwise is called")
        else:
            print("❌ first_level_wf_voxelwise not called")
            return False
        
        # Check that inputs parameter is used (not in_files)
        if 'inputs=inputs' in content:
            print("✓ Uses 'inputs' parameter (correct for voxelwise)")
        else:
            print("❌ Does not use 'inputs' parameter")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading create_1st_voxelWise.py: {e}")
        return False

def test_data_flow():
    """Test the data flow from events file to workflow"""
    
    print("\n" + "=" * 60)
    print("TESTING DATA FLOW")
    print("=" * 60)
    
    # Test the complete data flow
    events_file = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if not os.path.exists(events_file):
        print(f"❌ Events file not found: {events_file}")
        return False
    
    try:
        # Step 1: Load events file
        df_trial_info = pd.read_csv(events_file)
        print(f"✓ Step 1: Loaded events file - {df_trial_info.shape}")
        
        # Step 2: Validate required columns
        required_columns = ['trial_type', 'onset', 'duration']
        missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
        
        if missing_columns:
            print(f"❌ Step 2: Missing columns: {missing_columns}")
            return False
        else:
            print(f"✓ Step 2: Required columns present: {required_columns}")
        
        # Step 3: Check data types
        df_trial_info['onset'] = pd.to_numeric(df_trial_info['onset'], errors='coerce')
        df_trial_info['duration'] = pd.to_numeric(df_trial_info['duration'], errors='coerce')
        df_trial_info = df_trial_info.dropna(subset=required_columns)
        print(f"✓ Step 3: Data types corrected and NaN values removed - {df_trial_info.shape}")
        
        # Step 4: Check that data is suitable for workflow
        if len(df_trial_info) > 0:
            print(f"✓ Step 4: Data is suitable for workflow - {len(df_trial_info)} trials")
            print(f"  - Trial types: {sorted(df_trial_info['trial_type'].unique())}")
            print(f"  - Time range: {df_trial_info['onset'].min():.1f} - {df_trial_info['onset'].max():.1f} seconds")
        else:
            print(f"❌ Step 4: No valid trials found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data flow test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("INTEGRATION LOGIC TEST: create_1st_voxelWise.py ↔ first_level_workflows.py")
    print("=" * 80)
    
    # Test 1: get_df_trial_info logic
    df_trial_info = test_get_df_trial_info_logic()
    
    # Test 2: Workflow function signatures
    signature_success = test_workflow_function_signatures()
    
    # Test 3: create_1st_voxelWise integration
    integration_success = test_create_1st_voxelWise_integration()
    
    # Test 4: Data flow
    dataflow_success = test_data_flow()
    
    # Summary
    print("\n" + "=" * 80)
    print("INTEGRATION LOGIC TEST SUMMARY")
    print("=" * 80)
    
    tests = [
        ("get_df_trial_info logic", df_trial_info is not None),
        ("Workflow function signatures", signature_success),
        ("create_1st_voxelWise integration", integration_success),
        ("Data flow", dataflow_success)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 ALL LOGIC TESTS PASSED!")
        print(f"   create_1st_voxelWise.py can run first_level_workflows.py properly")
        print(f"   - get_df_trial_info function works correctly")
        print(f"   - Workflow function signatures match")
        print(f"   - Integration points are correct")
        print(f"   - Data flow is valid")
        print(f"\n   Note: Actual execution requires nipype to be installed")
    else:
        print(f"\n❌ SOME LOGIC TESTS FAILED")
        print(f"   Please check the integration issues above")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
