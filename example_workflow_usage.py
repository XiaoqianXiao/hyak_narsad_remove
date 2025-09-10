#!/usr/bin/env python3
"""
Simple example showing how to define df_trial_info and use workflow functions
"""

import pandas as pd
import sys
sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')

from first_level_workflows import extract_cs_conditions, create_contrasts, first_level_wf

def main():
    print("=" * 60)
    print("SIMPLE WORKFLOW USAGE EXAMPLE")
    print("=" * 60)
    
    # =============================================================================
    # STEP 1: Define df_trial_info
    # =============================================================================
    print("\n1. DEFINING df_trial_info")
    print("-" * 30)
    
    # Load your trial data
    df_trial_info = pd.read_csv('/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv')
    
    print(f"✓ Loaded {len(df_trial_info)} trials")
    print(f"✓ Columns: {list(df_trial_info.columns)}")
    print(f"✓ Trial types: {df_trial_info['trial_type'].unique()}")
    
    # =============================================================================
    # STEP 2: Use extract_cs_conditions
    # =============================================================================
    print("\n2. EXTRACTING CONDITIONS")
    print("-" * 30)
    
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    print(f"✓ CS- first: {cs_conditions['first']}")
    print(f"✓ CS- others: {cs_conditions['other']}")
    print(f"✓ CSS first: {css_conditions['first']}")
    print(f"✓ CSS others: {css_conditions['other']}")
    print(f"✓ CSR first: {csr_conditions['first']}")
    print(f"✓ CSR others: {csr_conditions['other']}")
    
    # =============================================================================
    # STEP 3: Generate contrasts
    # =============================================================================
    print("\n3. GENERATING CONTRASTS")
    print("-" * 30)
    
    contrasts, _, _, _, _ = create_contrasts(df_trial_info, contrast_type='minimal')
    
    print(f"✓ Generated {len(contrasts)} contrasts")
    for i, contrast in enumerate(contrasts[:5], 1):
        print(f"  {i}. {contrast[0]}")
    
    # =============================================================================
    # STEP 4: Use in workflow (example)
    # =============================================================================
    print("\n4. WORKFLOW USAGE")
    print("-" * 30)
    
    # Example input files (you would use real paths)
    in_files = {
        'sub-01': {
            'bold': '/path/to/bold.nii.gz',
            'mask': '/path/to/mask.nii.gz', 
            'events': '/path/to/events.csv',
            'regressors': '/path/to/regressors.tsv',
            'tr': 2.5
        }
    }
    
    # Create workflow
    wf = first_level_wf(
        in_files=in_files,
        output_dir='/path/to/output',
        df_trial_info=df_trial_info,  # <-- df_trial_info is passed here
        contrast_type='minimal'
    )
    
    print("✓ Workflow created successfully")
    print("✓ df_trial_info is used internally to generate contrasts and session info")
    
    print(f"\nSUMMARY:")
    print(f"- df_trial_info defined: ✓")
    print(f"- Conditions extracted: ✓") 
    print(f"- Contrasts generated: ✓")
    print(f"- Workflow created: ✓")

if __name__ == "__main__":
    main()
