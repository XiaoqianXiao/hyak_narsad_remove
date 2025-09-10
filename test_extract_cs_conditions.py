#!/usr/bin/env python3
"""
Test script for the modified extract_cs_conditions function.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from first_level_workflows import extract_cs_conditions, create_contrasts

def test_extract_cs_conditions():
    """Test the extract_cs_conditions function with various condition names."""
    
    print("=== Testing extract_cs_conditions function ===\n")
    
    # Test case 1: CS-, CSS, and CSR conditions with multiple trials (alphabetical sorting)
    print("Test 1: CS-, CSS, and CSR conditions with multiple trials (alphabetical sorting)")
    condition_names_1 = ['CS-1', 'CS-2', 'CS-3', 'CSS1', 'CSS2', 'CSS3', 'CSR1', 'CSR2', 'US', 'FIXATION']
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(condition_names_1)
    
    print(f"Input conditions: {condition_names_1}")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()
    
    # Test case 1b: Same conditions but with onset times (chronological sorting)
    print("Test 1b: Same conditions but with onset times (chronological sorting)")
    onset_times_1 = [10.0, 5.0, 15.0, 8.0, 12.0, 3.0, 7.0, 20.0, 0.0, 0.0]  # Mixed order
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(condition_names_1, onset_times_1)
    
    print(f"Input conditions: {condition_names_1}")
    print(f"Onset times: {onset_times_1}")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()
    
    # Test case 2: Only CS- conditions
    print("Test 2: Only CS- conditions")
    condition_names_2 = ['CS-US_trial1', 'CS-US_trial2', 'CS-US_trial3', 'US', 'baseline']
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(condition_names_2)
    
    print(f"Input conditions: {condition_names_2}")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()
    
    # Test case 3: Single trials of each type
    print("Test 3: Single trials of each type")
    condition_names_3 = ['CS-', 'CSS', 'CSR', 'US', 'FIXATION']
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(condition_names_3)
    
    print(f"Input conditions: {condition_names_3}")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()
    
    # Test case 4: No CS-/CSS/CSR conditions
    print("Test 4: No CS-/CSS/CSR conditions")
    condition_names_4 = ['US', 'FIXATION', 'baseline']
    cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(condition_names_4)
    
    print(f"Input conditions: {condition_names_4}")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Other conditions: {other_conditions}")
    print()

def test_create_contrasts():
    """Test the create_contrasts function with the new format."""
    
    print("=== Testing create_contrasts function ===\n")
    
    # Test with CS-, CSS, and CSR conditions (alphabetical sorting)
    condition_names = ['CS-1', 'CS-2', 'CSS1', 'CSS2', 'CSR1', 'CSR2', 'US', 'FIXATION']
    contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions = create_contrasts(condition_names, 'standard')
    
    print(f"Input conditions: {condition_names}")
    print(f"Generated {len(contrasts)} contrasts:")
    for i, contrast in enumerate(contrasts, 1):
        print(f"  {i}. {contrast[0]}: {contrast[2]} with weights {contrast[3]}")
    print()
    
    # Test with onset times (chronological sorting)
    print("Test with onset times (chronological sorting):")
    onset_times = [15.0, 5.0, 10.0, 3.0, 8.0, 12.0, 0.0, 0.0]  # Mixed order
    contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions = create_contrasts(condition_names, 'standard', onset_times)
    
    print(f"Input conditions: {condition_names}")
    print(f"Onset times: {onset_times}")
    print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"Generated {len(contrasts)} contrasts:")
    for i, contrast in enumerate(contrasts, 1):
        print(f"  {i}. {contrast[0]}: {contrast[2]} with weights {contrast[3]}")
    print()

if __name__ == "__main__":
    test_extract_cs_conditions()
    test_create_contrasts()
    print("All tests completed!")
