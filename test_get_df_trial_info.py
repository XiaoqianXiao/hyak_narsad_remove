#!/usr/bin/env python3
"""
Test script for the modified get_df_trial_info function
"""

import os
import sys
import pandas as pd

# Add current directory to path
sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')

def test_get_df_trial_info():
    """Test the get_df_trial_info function"""
    
    print("=" * 60)
    print("TESTING get_df_trial_info FUNCTION")
    print("=" * 60)
    
    # Import the function
    from create_1st_voxelWise import get_df_trial_info
    
    # Test with real NARSAD data
    events_file = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if os.path.exists(events_file):
        print(f"✓ Testing with real data: {events_file}")
        
        try:
            # Call the function
            df_trial_info = get_df_trial_info(events_file)
            
            print(f"✓ Successfully loaded df_trial_info")
            print(f"✓ Shape: {df_trial_info.shape}")
            print(f"✓ Columns: {list(df_trial_info.columns)}")
            print(f"✓ Trial types: {sorted(df_trial_info['trial_type'].unique())}")
            print(f"✓ Time range: {df_trial_info['onset'].min():.1f} - {df_trial_info['onset'].max():.1f} seconds")
            
            # Show first few rows
            print(f"\nFirst 10 rows:")
            print(df_trial_info.head(10))
            
            # Test that it has the required columns
            required_columns = ['trial_type', 'onset', 'duration']
            missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            else:
                print(f"✓ All required columns present: {required_columns}")
            
            # Test data types
            print(f"\nData types:")
            print(f"  trial_type: {df_trial_info['trial_type'].dtype}")
            print(f"  onset: {df_trial_info['onset'].dtype}")
            print(f"  duration: {df_trial_info['duration'].dtype}")
            
            # Check for NaN values
            nan_counts = df_trial_info[required_columns].isnull().sum()
            if nan_counts.sum() > 0:
                print(f"⚠ Warning: Found NaN values:")
                print(nan_counts)
            else:
                print(f"✓ No NaN values in required columns")
            
            print(f"\n✅ TEST PASSED: get_df_trial_info function works correctly!")
            return True
            
        except Exception as e:
            print(f"❌ TEST FAILED: {e}")
            return False
            
    else:
        print(f"❌ Test file not found: {events_file}")
        print("Creating example data for testing...")
        
        # Create example data
        example_data = {
            'trial_type': ['FIXATION', 'CS-', 'FIXATION', 'CSS', 'US_CSS', 'CSR', 'FIXATION', 'CS-', 'CSS', 'US_CSR'],
            'onset': [0, 12, 18, 31, 37, 50, 56, 68, 74, 80],
            'duration': [12, 6, 13, 6, 0, 6, 12, 6, 6, 0]
        }
        
        example_file = '/tmp/example_events.csv'
        pd.DataFrame(example_data).to_csv(example_file, index=False)
        
        try:
            df_trial_info = get_df_trial_info(example_file)
            print(f"✓ Successfully loaded example df_trial_info")
            print(f"✓ Shape: {df_trial_info.shape}")
            print(f"✓ Columns: {list(df_trial_info.columns)}")
            print(f"✅ TEST PASSED: get_df_trial_info function works with example data!")
            return True
            
        except Exception as e:
            print(f"❌ TEST FAILED with example data: {e}")
            return False

def main():
    """Main test function"""
    success = test_get_df_trial_info()
    
    if success:
        print(f"\n🎉 All tests passed! The get_df_trial_info function is working correctly.")
        print(f"   - It loads events files and returns df_trial_info DataFrames")
        print(f"   - It validates required columns and data types")
        print(f"   - It's ready to be used in the workflow functions")
    else:
        print(f"\n❌ Tests failed. Please check the function implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
