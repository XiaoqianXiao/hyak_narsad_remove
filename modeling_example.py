#!/usr/bin/env python3
"""
Example of how the conditions data is used in fMRI modeling
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def demonstrate_modeling_usage():
    """Show how the conditions data is used in fMRI modeling"""
    
    # Load the conditions data
    df_conditions = pd.read_csv('narsad_conditions_data.csv')
    
    print("=" * 80)
    print("FMRI MODELING USAGE EXAMPLE")
    print("=" * 80)
    
    print("1. LOADING CONDITIONS DATA:")
    print("-" * 40)
    print(f"Total trials: {len(df_conditions)}")
    print(f"Columns: {list(df_conditions.columns)}")
    print(f"Unique conditions: {sorted(df_conditions['conditions'].unique())}")
    
    print("\n2. DESIGN MATRIX CONSTRUCTION:")
    print("-" * 40)
    print("The 'conditions' column becomes the regressor names in the design matrix.")
    print("Each unique condition gets its own regressor column.")
    
    # Show how regressors are created
    unique_conditions = df_conditions['conditions'].unique()
    print(f"\nRegressor names (from conditions column):")
    for i, condition in enumerate(unique_conditions, 1):
        print(f"  {i:2d}. {condition}")
    
    print(f"\nTotal regressors: {len(unique_conditions)}")
    
    print("\n3. TRIAL-TO-REGRESSOR MAPPING:")
    print("-" * 40)
    print("Each trial maps to exactly one regressor based on its 'conditions' value:")
    
    # Show examples of trial-to-regressor mapping
    examples = [
        ("CS- trials", df_conditions[df_conditions['trial_type'] == 'CS-']),
        ("CSS trials", df_conditions[df_conditions['trial_type'] == 'CSS']),
        ("CSR trials", df_conditions[df_conditions['trial_type'] == 'CSR']),
        ("US trials", df_conditions[df_conditions['trial_type'].str.startswith('US')])
    ]
    
    for trial_type, trials in examples:
        print(f"\n{trial_type}:")
        for _, trial in trials.head(3).iterrows():
            print(f"  Onset {trial['onset']:3.0f}s: {trial['trial_type']:6s} → {trial['conditions']:12s}")
        if len(trials) > 3:
            print(f"  ... and {len(trials) - 3} more")
    
    print("\n4. CONTRAST GENERATION:")
    print("-" * 40)
    print("Contrasts are created between the regressor names (conditions column values):")
    
    # Load and show some contrasts
    df_contrasts = pd.read_csv('narsad_contrasts_minimal.csv')
    print(f"\nMinimal contrasts (each condition vs baseline):")
    for _, contrast in df_contrasts.head(5).iterrows():
        print(f"  {contrast['contrast_id']:2d}. {contrast['contrast_name']:20s} (regressor: {contrast['condition1']})")
    
    print(f"\nStandard contrasts (pairwise comparisons):")
    df_std_contrasts = pd.read_csv('narsad_contrasts_standard.csv')
    for _, contrast in df_std_contrasts.head(5).iterrows():
        print(f"  {contrast['contrast_id']:2d}. {contrast['contrast_name']:20s} ({contrast['condition1']} vs {contrast['condition2']})")
    
    print("\n5. WORKFLOW INTEGRATION:")
    print("-" * 40)
    print("In the actual workflow, this would be used as follows:")
    print("""
    # 1. Load event data
    df_events = pd.read_csv('narsad_conditions_data.csv')
    
    # 2. Create design matrix
    # Each unique condition becomes a regressor
    regressor_names = df_events['conditions'].unique()
    
    # 3. Generate contrasts
    contrasts = []
    for condition in regressor_names:
        contrasts.append((f'{condition}>baseline', 'T', [condition], [1]))
    
    # 4. Use in FSL/nipype
    level1design = Level1Design()
    level1design.inputs.session_info = [df_events.to_dict('records')]
    level1design.inputs.contrasts = contrasts
    """)
    
    print("\n6. KEY BENEFITS FOR MODELING:")
    print("-" * 40)
    print("✓ Separate regressors for first vs other trials")
    print("✓ Clean condition names (CS-_first, CSS_others, etc.)")
    print("✓ Easy contrast generation between any conditions")
    print("✓ Preserves all trial timing information")
    print("✓ Compatible with standard fMRI analysis pipelines")
    print("✓ No artificial or missing condition names")
    
    print("\n7. EXAMPLE ANALYSIS QUESTIONS:")
    print("-" * 40)
    print("With this setup, you can answer questions like:")
    print("• Is the first CS- trial different from other CS- trials? (CS-_first vs CS-_others)")
    print("• Are first trials different across conditions? (CS-_first vs CSS_first vs CSR_first)")
    print("• Are other trials different across conditions? (CS-_others vs CSS_others vs CSR_others)")
    print("• How do first trials compare to baseline? (CS-_first vs FIXATION)")
    print("• How do other trials compare to baseline? (CS-_others vs FIXATION)")
    print("• Are US responses different? (US_CSS vs US_CSR)")

if __name__ == "__main__":
    demonstrate_modeling_usage()
