#!/usr/bin/env python3
"""
Test script for the DataFrame input functionality in extract_cs_conditions function.
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from first_level_workflows import extract_cs_conditions, create_contrasts

def test_dataframe_input():
    """Test the extract_cs_conditions function with DataFrame input."""
    
    print("=== Testing DataFrame input functionality ===\n")
    
    # Test case 1: Create a sample DataFrame with onset, duration, trial_type columns
    print("Test 1: DataFrame with mixed trial order (chronological sorting)")
    data = {
        'onset': [15.0, 5.0, 10.0, 3.0, 8.0, 12.0, 20.0, 25.0, 0.0, 0.0],
        'duration': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0],
        'trial_type': ['CS-1', 'CS-2', 'CSS1', 'CSS2', 'CSR1', 'CSR2', 'US', 'FIXATION', 'baseline', 'rest']
    }
    df = pd.DataFrame(data)
    
    print("Input DataFrame:")
    print(df)
    print()
    
    print("Note: The function now uses internal DataFrames for each condition type (CS-, CSS, CSR)")
    print("This makes sorting and processing more straightforward and efficient.")
    print()
    
    # Test with DataFrame input
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info=df)
    
    print("Results:")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()
    
    # Test case 2: Create contrasts with DataFrame input
    print("Test 2: Create contrasts with DataFrame input")
    contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions = create_contrasts(df_trial_info=df, contrast_type='standard')
    
    print(f"Generated {len(contrasts)} contrasts:")
    for i, contrast in enumerate(contrasts, 1):
        print(f"  {i}. {contrast[0]}: {contrast[2]} with weights {contrast[3]}")
    print()
    
    # Test case 3: Real-world example with typical fMRI event file structure
    print("Test 3: Real-world fMRI event file structure")
    real_data = {
        'onset': [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
        'duration': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
        'trial_type': ['CS-', 'CSS', 'CSR', 'CS-', 'CSS', 'CSR', 'US', 'FIXATION', 'CS-', 'CSS']
    }
    real_df = pd.DataFrame(real_data)
    
    print("Real-world DataFrame:")
    print(real_df)
    print()
    
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info=real_df)
    
    print("Results:")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()
    
    # Test case 4: Error handling - missing required columns
    print("Test 4: Error handling - missing required columns")
    try:
        bad_data = {
            'onset': [0.0, 10.0, 20.0],
            'duration': [2.0, 2.0, 2.0],
            'wrong_column': ['CS-', 'CSS', 'CSR']
        }
        bad_df = pd.DataFrame(bad_data)
        extract_cs_conditions(df_trial_info=bad_df)
    except ValueError as e:
        print(f"Expected error caught: {e}")
    print()
    
    # Test case 5: Error handling - non-DataFrame input
    print("Test 5: Error handling - non-DataFrame input")
    try:
        extract_cs_conditions("not_a_dataframe")
    except ValueError as e:
        print(f"Expected error caught: {e}")
    print()
    
    # Test case 6: Error handling - empty DataFrame
    print("Test 6: Error handling - empty DataFrame")
    try:
        empty_df = pd.DataFrame(columns=['trial_type', 'onset', 'duration'])
        extract_cs_conditions(empty_df)
    except ValueError as e:
        print(f"Expected error caught: {e}")
    print()

if __name__ == "__main__":
    test_dataframe_input()
    print("All DataFrame tests completed!")
