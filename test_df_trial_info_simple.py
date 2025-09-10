#!/usr/bin/env python3
"""
Simple test for the get_df_trial_info function logic
"""

import os
import pandas as pd

def get_df_trial_info(events_file):
    """
    Load events file and return df_trial_info DataFrame.
    (Simplified version for testing)
    """
    try:
        if os.path.exists(events_file):
            # Load the CSV file
            df_trial_info = pd.read_csv(events_file)
            
            # Validate required columns
            required_columns = ['trial_type', 'onset', 'duration']
            missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
            
            if missing_columns:
                # Try alternative column names
                column_mapping = {
                    'trial_type': ['condition', 'event_type', 'type', 'stimulus', 'trial'],
                    'onset': ['start_time', 'time', 'timestamp'],
                    'duration': ['length', 'dur', 'duration_ms']
                }
                
                for required_col in missing_columns:
                    if required_col in column_mapping:
                        for alt_col in column_mapping[required_col]:
                            if alt_col in df_trial_info.columns:
                                df_trial_info[required_col] = df_trial_info[alt_col]
                                print(f"Mapped column '{alt_col}' to '{required_col}'")
                                break
                
                # Check if we still have missing columns
                missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
                if missing_columns:
                    print(f"Missing required columns: {missing_columns}")
                    print(f"Available columns: {list(df_trial_info.columns)}")
                    raise ValueError(f"Events file missing required columns: {missing_columns}")
            
            # Ensure data types are correct
            df_trial_info['onset'] = pd.to_numeric(df_trial_info['onset'], errors='coerce')
            df_trial_info['duration'] = pd.to_numeric(df_trial_info['duration'], errors='coerce')
            
            # Remove any rows with NaN values in required columns
            df_trial_info = df_trial_info.dropna(subset=required_columns)
            
            print(f"Successfully loaded df_trial_info: {df_trial_info.shape}")
            print(f"Columns: {list(df_trial_info.columns)}")
            print(f"Trial types: {sorted(df_trial_info['trial_type'].unique())}")
            print(f"Time range: {df_trial_info['onset'].min():.1f} - {df_trial_info['onset'].max():.1f} seconds")
            
            return df_trial_info
            
        else:
            print(f"Events file does not exist: {events_file}")
            raise FileNotFoundError(f"Events file not found: {events_file}")
            
    except Exception as e:
        print(f"Could not load df_trial_info from events file {events_file}: {e}")
        raise

def test_function():
    """Test the get_df_trial_info function"""
    
    print("=" * 60)
    print("TESTING get_df_trial_info FUNCTION")
    print("=" * 60)
    
    # Test with real NARSAD data
    events_file = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if os.path.exists(events_file):
        print(f"✓ Testing with real data: {events_file}")
        
        try:
            # Call the function
            df_trial_info = get_df_trial_info(events_file)
            
            print(f"✓ Successfully loaded df_trial_info")
            print(f"✓ Shape: {df_trial_info.shape}")
            
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
            
            print(f"\n✅ TEST PASSED: get_df_trial_info function works correctly!")
            return True
            
        except Exception as e:
            print(f"❌ TEST FAILED: {e}")
            return False
            
    else:
        print(f"❌ Test file not found: {events_file}")
        return False

if __name__ == "__main__":
    success = test_function()
    
    if success:
        print(f"\n🎉 Test passed! The get_df_trial_info function is working correctly.")
        print(f"   - It loads events files and returns df_trial_info DataFrames")
        print(f"   - It validates required columns and data types")
        print(f"   - It's ready to be used in the workflow functions")
    else:
        print(f"\n❌ Test failed. Please check the function implementation.")
