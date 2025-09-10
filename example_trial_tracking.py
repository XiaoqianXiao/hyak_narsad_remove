#!/usr/bin/env python3
"""
Example showing how trial types and onsets are tracked for contrast generation
"""

import pandas as pd
import numpy as np

# Create example trial data
example_data = {
    'trial_type': ['CS-1', 'CSS1', 'CSR1', 'CS-2', 'CSS2', 'CSR2', 'CS-3', 'US', 'FIXATION'],
    'onset': [5.0, 10.0, 8.0, 15.0, 20.0, 18.0, 25.0, 30.0, 0.0],
    'duration': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.5]
}

df = pd.DataFrame(example_data)
print("Original trial data:")
print(df)
print()

# Simulate the extract_cs_conditions function logic
def extract_cs_conditions_example(df_trial_info):
    """Example of how CS conditions are extracted and grouped"""
    
    # Group conditions by type
    cs_trials_df = df_trial_info.loc[df_trial_info['trial_type'].str.startswith('CS-') & 
                                     ~df_trial_info['trial_type'].str.startswith('CSS') & 
                                     ~df_trial_info['trial_type'].str.startswith('CSR')].copy()
    css_trials_df = df_trial_info.loc[df_trial_info['trial_type'].str.startswith('CSS')].copy()
    csr_trials_df = df_trial_info.loc[df_trial_info['trial_type'].str.startswith('CSR')].copy()
    
    print("CS- trials (before sorting):")
    print(cs_trials_df)
    print()
    
    print("CSS trials (before sorting):")
    print(css_trials_df)
    print()
    
    print("CSR trials (before sorting):")
    print(csr_trials_df)
    print()
    
    # Sort by onset time
    cs_trials_sorted = cs_trials_df.sort_values('onset').reset_index(drop=True)
    css_trials_sorted = css_trials_df.sort_values('onset').reset_index(drop=True)
    csr_trials_sorted = csr_trials_df.sort_values('onset').reset_index(drop=True)
    
    print("CS- trials (after sorting by onset):")
    print(cs_trials_sorted)
    print()
    
    print("CSS trials (after sorting by onset):")
    print(css_trials_sorted)
    print()
    
    print("CSR trials (after sorting by onset):")
    print(csr_trials_sorted)
    print()
    
    # Extract first and other conditions
    cs_conditions = {'first': None, 'other': []}
    css_conditions = {'first': None, 'other': []}
    csr_conditions = {'first': None, 'other': []}
    
    if not cs_trials_sorted.empty:
        cs_conditions['first'] = cs_trials_sorted.iloc[0]['trial_type']
        cs_conditions['other'] = cs_trials_sorted.iloc[1:]['trial_type'].tolist()
        print(f"CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    
    if not css_trials_sorted.empty:
        css_conditions['first'] = css_trials_sorted.iloc[0]['trial_type']
        css_conditions['other'] = css_trials_sorted.iloc[1:]['trial_type'].tolist()
        print(f"CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    
    if not csr_trials_sorted.empty:
        csr_conditions['first'] = csr_trials_sorted.iloc[0]['trial_type']
        csr_conditions['other'] = csr_trials_sorted.iloc[1:]['trial_type'].tolist()
        print(f"CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    
    # Other conditions
    other_conditions = df_trial_info.loc[~df_trial_info['trial_type'].str.startswith('CS')]['trial_type'].tolist()
    print(f"Other conditions: {other_conditions}")
    print()
    
    return cs_conditions, css_conditions, csr_conditions, other_conditions

# Run the example
cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions_example(df)

# Show how all_contrast_conditions is built
print("=" * 50)
print("HOW all_contrast_conditions IS BUILT:")
print("=" * 50)

all_contrast_conditions = []

# Add first trials as separate conditions
if cs_conditions['first']:
    all_contrast_conditions.append(cs_conditions['first'])
    print(f"Added first CS- trial: '{cs_conditions['first']}'")

if css_conditions['first']:
    all_contrast_conditions.append(css_conditions['first'])
    print(f"Added first CSS trial: '{css_conditions['first']}'")

if csr_conditions['first']:
    all_contrast_conditions.append(csr_conditions['first'])
    print(f"Added first CSR trial: '{csr_conditions['first']}'")

# Add grouped other trials as single conditions
if cs_conditions['other']:
    all_contrast_conditions.append('CS-_others')
    print(f"Added grouped CS- others: 'CS-_others'")

if css_conditions['other']:
    all_contrast_conditions.append('CSS_others')
    print(f"Added grouped CSS others: 'CSS_others'")

if csr_conditions['other']:
    all_contrast_conditions.append('CSR_others')
    print(f"Added grouped CSR others: 'CSR_others'")

# Add all other conditions
all_contrast_conditions.extend(other_conditions)
print(f"Added other conditions: {other_conditions}")

print()
print("FINAL all_contrast_conditions:")
print(all_contrast_conditions)

print()
print("=" * 50)
print("THE PROBLEM:")
print("=" * 50)
print("The design matrix will contain these actual trial names:")
print(df['trial_type'].tolist())
print()
print("But all_contrast_conditions contains these names:")
print(all_contrast_conditions)
print()
print("MISMATCH! The contrast generation will fail because:")
print("- 'CS-_others', 'CSS_others', 'CSR_others' don't exist in the design matrix")
print("- Only the original trial names exist in the design matrix")
