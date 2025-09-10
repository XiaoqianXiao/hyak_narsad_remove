#!/usr/bin/env python3
"""
Generate and save contrast files for the NARSAD data
"""

import pandas as pd
import numpy as np

def extract_cs_conditions_new(df_trial_info):
    """
    Extract and group CS-, CSS, and CSR conditions from a pandas DataFrame.
    
    This function adds a 'conditions' column to the DataFrame that groups trials:
    - First trial of each CS type becomes 'CS-_first', 'CSS_first', 'CSR_first'
    - Remaining trials of each type become 'CS-_others', 'CSS_others', 'CSR_others'
    - All other trials keep their original trial_type as conditions value
    """
    import pandas as pd
    
    # Validate DataFrame input
    if not isinstance(df_trial_info, pd.DataFrame):
        raise ValueError("df_trial_info must be a pandas DataFrame")
    
    if df_trial_info.empty:
        raise ValueError("DataFrame cannot be empty")
    
    required_columns = ['trial_type', 'onset']
    missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
    if missing_columns:
        raise ValueError(f"DataFrame missing required columns: {missing_columns}")
    
    # Create a copy to avoid modifying original
    df_work = df_trial_info.copy()
    
    # Initialize conditions column with trial_type values
    df_work['conditions'] = df_work['trial_type'].copy()
    
    print(f"Using DataFrame input with {len(df_work)} trials")
    print(f"DataFrame columns: {list(df_work.columns)}")
    
    # Find first trial of each CS type (by onset time)
    cs_trials = df_work[df_work['trial_type'].str.startswith('CS-') & 
                       ~df_work['trial_type'].str.startswith('CSS') & 
                       ~df_work['trial_type'].str.startswith('CSR')].copy()
    css_trials = df_work[df_work['trial_type'].str.startswith('CSS')].copy()
    csr_trials = df_work[df_work['trial_type'].str.startswith('CSR')].copy()
    
    # Update conditions column for CS- trials
    if not cs_trials.empty:
        cs_first_idx = cs_trials.sort_values('onset').index[0]
        df_work.loc[cs_first_idx, 'conditions'] = 'CS-_first'
        cs_other_indices = cs_trials[cs_trials.index != cs_first_idx].index
        df_work.loc[cs_other_indices, 'conditions'] = 'CS-_others'
        print(f"CS- conditions: first trial at index {cs_first_idx}, {len(cs_other_indices)} others")
    
    # Update conditions column for CSS trials
    if not css_trials.empty:
        css_first_idx = css_trials.sort_values('onset').index[0]
        df_work.loc[css_first_idx, 'conditions'] = 'CSS_first'
        css_other_indices = css_trials[css_trials.index != css_first_idx].index
        df_work.loc[css_other_indices, 'conditions'] = 'CSS_others'
        print(f"CSS conditions: first trial at index {css_first_idx}, {len(css_other_indices)} others")
    
    # Update conditions column for CSR trials
    if not csr_trials.empty:
        csr_first_idx = csr_trials.sort_values('onset').index[0]
        df_work.loc[csr_first_idx, 'conditions'] = 'CSR_first'
        csr_other_indices = csr_trials[csr_trials.index != csr_first_idx].index
        df_work.loc[csr_other_indices, 'conditions'] = 'CSR_others'
        print(f"CSR conditions: first trial at index {csr_first_idx}, {len(csr_other_indices)} others")
    
    # Get unique conditions for contrast generation
    unique_conditions = df_work['conditions'].unique().tolist()
    print(f"Unique conditions for contrast generation: {unique_conditions}")
    
    # Extract grouped conditions for backward compatibility
    cs_conditions = {'first': 'CS-_first' if 'CS-_first' in unique_conditions else None, 
                     'other': ['CS-_others'] if 'CS-_others' in unique_conditions else []}
    css_conditions = {'first': 'CSS_first' if 'CSS_first' in unique_conditions else None, 
                      'other': ['CSS_others'] if 'CSS_others' in unique_conditions else []}
    csr_conditions = {'first': 'CSR_first' if 'CSR_first' in unique_conditions else None, 
                      'other': ['CSR_others'] if 'CSR_others' in unique_conditions else []}
    
    # Get other conditions (non-CS/CSS/CSR)
    other_conditions = df_work[~df_work['trial_type'].str.startswith('CS')]['trial_type'].unique().tolist()
    
    print(f"Processed conditions: CS-={cs_conditions}, CSS={css_conditions}, CSR={csr_conditions}")
    print(f"Other conditions: {other_conditions}")
    
    return df_work, cs_conditions, css_conditions, csr_conditions, other_conditions

def create_contrasts(df_trial_info, contrast_type='standard'):
    """Create contrasts using the new conditions column approach"""
    
    # Extract CS-, CSS, and CSR conditions with grouping
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions_new(df_trial_info)
    
    # Use the conditions column for contrast generation
    all_contrast_conditions = df_with_conditions['conditions'].unique().tolist()
    
    contrasts = []
    
    if contrast_type == 'minimal':
        # Create simple contrasts for each condition vs baseline
        for condition in all_contrast_conditions:
            contrasts.append((f'{condition}>baseline', 'T', [condition], [1]))
    
    elif contrast_type == 'standard':
        # Create pairwise contrasts between all conditions
        for i, cond1 in enumerate(all_contrast_conditions):
            for j, cond2 in enumerate(all_contrast_conditions):
                if i < j:  # Avoid duplicate contrasts
                    contrasts.append((f'{cond1}>{cond2}', 'T', [cond1, cond2], [1, -1]))
                    contrasts.append((f'{cond1}<{cond2}', 'T', [cond1, cond2], [-1, 1]))
    
    return contrasts, all_contrast_conditions, df_with_conditions

def save_contrasts_to_file(contrasts, filename):
    """Save contrasts to a text file"""
    with open(filename, 'w') as f:
        f.write("# Contrast File Generated for NARSAD Data\n")
        f.write("# Format: (contrast_name, contrast_type, conditions, weights)\n")
        f.write(f"# Total contrasts: {len(contrasts)}\n")
        f.write("# Generated using conditions column approach\n\n")
        
        for i, contrast in enumerate(contrasts, 1):
            contrast_name, contrast_type, conditions, weights = contrast
            f.write(f"{i:2d}. {contrast_name}\n")
            f.write(f"    Type: {contrast_type}\n")
            f.write(f"    Conditions: {conditions}\n")
            f.write(f"    Weights: {weights}\n\n")

def save_contrasts_to_csv(contrasts, filename):
    """Save contrasts to a CSV file"""
    contrast_data = []
    for i, contrast in enumerate(contrasts, 1):
        contrast_name, contrast_type, conditions, weights = contrast
        contrast_data.append({
            'contrast_id': i,
            'contrast_name': contrast_name,
            'contrast_type': contrast_type,
            'condition1': conditions[0] if len(conditions) > 0 else '',
            'condition2': conditions[1] if len(conditions) > 1 else '',
            'weight1': weights[0] if len(weights) > 0 else 0,
            'weight2': weights[1] if len(weights) > 1 else 0,
            'conditions_list': str(conditions),
            'weights_list': str(weights)
        })
    
    df_contrasts = pd.DataFrame(contrast_data)
    df_contrasts.to_csv(filename, index=False)
    return df_contrasts

def main():
    # Load the real NARSAD data
    df_trial_info = pd.read_csv('/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv')
    
    print("=" * 80)
    print("GENERATING CONTRAST FILES FOR NARSAD DATA")
    print("=" * 80)
    
    # Generate contrasts for different types
    contrast_types = ['minimal', 'standard']
    
    for contrast_type in contrast_types:
        print(f"\nGenerating {contrast_type} contrasts...")
        contrasts, conditions, df_with_conditions = create_contrasts(df_trial_info, contrast_type)
        
        print(f"Conditions: {conditions}")
        print(f"Number of contrasts: {len(contrasts)}")
        
        # Save to text file
        txt_filename = f'narsad_contrasts_{contrast_type}.txt'
        save_contrasts_to_file(contrasts, txt_filename)
        print(f"Saved to: {txt_filename}")
        
        # Save to CSV file
        csv_filename = f'narsad_contrasts_{contrast_type}.csv'
        df_contrasts = save_contrasts_to_csv(contrasts, csv_filename)
        print(f"Saved to: {csv_filename}")
        
        # Show first few contrasts
        print(f"\nFirst 5 {contrast_type} contrasts:")
        for i, contrast in enumerate(contrasts[:5], 1):
            print(f"  {i}. {contrast[0]}")
        
        if len(contrasts) > 5:
            print(f"  ... and {len(contrasts) - 5} more")
    
    # Also save the conditions DataFrame
    conditions_filename = 'narsad_conditions_data.csv'
    df_with_conditions.to_csv(conditions_filename, index=False)
    print(f"\nSaved conditions DataFrame to: {conditions_filename}")
    
    print(f"\n" + "=" * 80)
    print("FILES GENERATED:")
    print("=" * 80)
    print("1. narsad_contrasts_minimal.txt - Minimal contrasts (each condition vs baseline)")
    print("2. narsad_contrasts_minimal.csv - Minimal contrasts in CSV format")
    print("3. narsad_contrasts_standard.txt - Standard contrasts (all pairwise)")
    print("4. narsad_contrasts_standard.csv - Standard contrasts in CSV format")
    print("5. narsad_conditions_data.csv - Full DataFrame with conditions column")
    print("\nAll files are ready for use in fMRI analysis!")

if __name__ == "__main__":
    main()
