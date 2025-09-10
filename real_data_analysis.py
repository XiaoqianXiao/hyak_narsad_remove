#!/usr/bin/env python3
"""
Analysis of real NARSAD data to show the trial tracking problem
"""

import pandas as pd
import numpy as np

# Load the real NARSAD data
df_trial_info = pd.read_csv('/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv')

print("=" * 80)
print("REAL NARSAD TRIAL DATA ANALYSIS")
print("=" * 80)

print(f"Shape: {df_trial_info.shape}")
print(f"Columns: {list(df_trial_info.columns)}")
print(f"Total trials: {len(df_trial_info)}")
print(f"All unique trial types: {sorted(df_trial_info['trial_type'].unique())}")

print("\n" + "=" * 80)
print("FIRST 20 ROWS")
print("=" * 80)
print(df_trial_info.head(20))

print("\n" + "=" * 80)
print("TRIAL TYPE COUNTS")
print("=" * 80)
trial_counts = df_trial_info['trial_type'].value_counts()
print(trial_counts)

print("\n" + "=" * 80)
print("SIMULATING extract_cs_conditions FUNCTION")
print("=" * 80)

# Simulate the extract_cs_conditions function logic
def simulate_extract_cs_conditions(df_trial_info):
    """Simulate the extract_cs_conditions function"""
    
    # Group conditions by type
    cs_trials_df = df_trial_info.loc[df_trial_info['trial_type'].str.startswith('CS-') & 
                                     ~df_trial_info['trial_type'].str.startswith('CSS') & 
                                     ~df_trial_info['trial_type'].str.startswith('CSR')].copy()
    css_trials_df = df_trial_info.loc[df_trial_info['trial_type'].str.startswith('CSS')].copy()
    csr_trials_df = df_trial_info.loc[df_trial_info['trial_type'].str.startswith('CSR')].copy()
    
    print("CS- trials found:")
    print(cs_trials_df)
    print()
    
    print("CSS trials found:")
    print(css_trials_df)
    print()
    
    print("CSR trials found:")
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

# Run the simulation
cs_conditions, css_conditions, csr_conditions, other_conditions = simulate_extract_cs_conditions(df_trial_info)

print("=" * 80)
print("HOW all_contrast_conditions IS CURRENTLY BUILT")
print("=" * 80)

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

print(f"\nFINAL all_contrast_conditions:")
print(all_contrast_conditions)

print("\n" + "=" * 80)
print("ACTUAL DESIGN MATRIX CONDITIONS")
print("=" * 80)

print("The design matrix will contain these actual trial names:")
design_matrix_conditions = df_trial_info['trial_type'].unique().tolist()
print(design_matrix_conditions)

print(f"\nNumber of unique conditions in design matrix: {len(design_matrix_conditions)}")
print(f"Number of conditions in all_contrast_conditions: {len(all_contrast_conditions)}")

print("\n" + "=" * 80)
print("THE PROBLEM - MISMATCH BETWEEN CONDITIONS")
print("=" * 80)

print("Design matrix contains:")
for cond in sorted(design_matrix_conditions):
    print(f"  - {cond}")

print("\nall_contrast_conditions contains:")
for cond in sorted(all_contrast_conditions):
    print(f"  - {cond}")

print("\nMISSING from all_contrast_conditions:")
missing = set(design_matrix_conditions) - set(all_contrast_conditions)
for cond in sorted(missing):
    print(f"  - {cond}")

print("\nEXTRA in all_contrast_conditions (not in design matrix):")
extra = set(all_contrast_conditions) - set(design_matrix_conditions)
for cond in sorted(extra):
    print(f"  - {cond}")

print(f"\nMISMATCH COUNT: {len(missing)} missing, {len(extra)} extra")

print("\n" + "=" * 80)
print("CORRECT all_contrast_conditions SHOULD BE")
print("=" * 80)

print("The correct approach would be to use ALL the actual trial names from the design matrix:")
correct_contrast_conditions = design_matrix_conditions.copy()
print(f"Correct all_contrast_conditions: {correct_contrast_conditions}")

print(f"\nThis would allow contrasts to be created between any of the actual conditions:")
print("Examples of possible contrasts:")
for i, cond1 in enumerate(correct_contrast_conditions[:3]):  # Show first 3
    for j, cond2 in enumerate(correct_contrast_conditions[:3]):
        if i < j:
            print(f"  - {cond1} > {cond2}")
            print(f"  - {cond1} < {cond2}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("1. The current code creates artificial condition names ('CS-_others', etc.)")
print("2. These artificial names don't exist in the design matrix")
print("3. Contrast generation will fail because it references non-existent conditions")
print("4. The solution is to use the actual trial names from the design matrix")
print("5. If grouping is needed, it should be done at the contrast level, not the condition level")
