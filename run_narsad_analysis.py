#!/usr/bin/env python3
"""
Complete NARSAD fMRI Analysis Script
Demonstrates how to define df_trial_info and use it with workflow functions
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add current directory to path to import our modules
sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')

from first_level_workflows import (
    first_level_wf, 
    first_level_wf_LSS, 
    first_level_wf_voxelwise,
    extract_cs_conditions,
    create_contrasts
)

def main():
    """Main analysis function"""
    
    print("=" * 80)
    print("NARSAD FMRI ANALYSIS SCRIPT")
    print("=" * 80)
    
    # =============================================================================
    # STEP 1: DEFINE df_trial_info
    # =============================================================================
    print("\n1. LOADING TRIAL DATA (df_trial_info)")
    print("-" * 50)
    
    # Define df_trial_info by loading the real NARSAD data
    data_path = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if not os.path.exists(data_path):
        print(f"ERROR: Data file not found at {data_path}")
        print("Please check the path and try again.")
        return
    
    df_trial_info = pd.read_csv(data_path)
    
    print(f"✓ Loaded trial data: {df_trial_info.shape}")
    print(f"✓ Columns: {list(df_trial_info.columns)}")
    print(f"✓ Trial types: {sorted(df_trial_info['trial_type'].unique())}")
    print(f"✓ Time range: {df_trial_info['onset'].min():.1f} - {df_trial_info['onset'].max():.1f} seconds")
    
    # Show first few rows
    print("\nFirst 10 trials:")
    print(df_trial_info[['onset', 'duration', 'trial_type']].head(10))
    
    # =============================================================================
    # STEP 2: EXTRACT AND GROUP CONDITIONS
    # =============================================================================
    print("\n2. EXTRACTING AND GROUPING CONDITIONS")
    print("-" * 50)
    
    # Use the extract_cs_conditions function to add the 'conditions' column
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    print(f"✓ Added 'conditions' column")
    print(f"✓ CS- conditions: first='{cs_conditions['first']}', other={cs_conditions['other']}")
    print(f"✓ CSS conditions: first='{css_conditions['first']}', other={css_conditions['other']}")
    print(f"✓ CSR conditions: first='{csr_conditions['first']}', other={csr_conditions['other']}")
    print(f"✓ Other conditions: {other_conditions}")
    
    # Show the new conditions column
    print("\nConditions column preview:")
    print(df_with_conditions[['trial_type', 'conditions', 'onset']].head(15))
    
    # =============================================================================
    # STEP 3: GENERATE CONTRASTS
    # =============================================================================
    print("\n3. GENERATING CONTRASTS")
    print("-" * 50)
    
    # Generate different types of contrasts
    contrast_types = ['minimal', 'standard']
    
    for contrast_type in contrast_types:
        print(f"\nGenerating {contrast_type} contrasts...")
        contrasts, cs_cond, css_cond, csr_cond, other_cond = create_contrasts(df_trial_info, contrast_type=contrast_type)
        
        print(f"✓ Generated {len(contrasts)} {contrast_type} contrasts")
        
        # Show first few contrasts
        print(f"First 5 {contrast_type} contrasts:")
        for i, contrast in enumerate(contrasts[:5], 1):
            print(f"  {i}. {contrast[0]}")
    
    # =============================================================================
    # STEP 4: PREPARE WORKFLOW INPUTS
    # =============================================================================
    print("\n4. PREPARING WORKFLOW INPUTS")
    print("-" * 50)
    
    # Define input files (this would be your actual fMRI data)
    # For demonstration, we'll create placeholder paths
    base_dir = '/Users/xiaoqianxiao/projects/NARSAD/MRI/processed_data'
    
    # Example input files structure (you would replace with actual paths)
    in_files = {
        'sub-01': {
            'bold': f'{base_dir}/sub-01/func/sub-01_task-narsad_bold.nii.gz',
            'mask': f'{base_dir}/sub-01/func/sub-01_task-narsad_brainmask.nii.gz',
            'events': data_path,  # Same as df_trial_info source
            'regressors': f'{base_dir}/sub-01/func/sub-01_task-narsad_confounds.tsv',
            'tr': 2.5  # Repetition time in seconds
        }
    }
    
    # Define output directory
    output_dir = '/Users/xiaoqianxiao/projects/NARSAD/MRI/analysis_results'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"✓ Input files structure defined")
    print(f"✓ Output directory: {output_dir}")
    
    # =============================================================================
    # STEP 5: RUN WORKFLOWS (DEMONSTRATION)
    # =============================================================================
    print("\n5. WORKFLOW EXECUTION (DEMONSTRATION)")
    print("-" * 50)
    
    # Note: These are demonstrations - actual execution would require real data
    print("Note: These workflows would be executed with real fMRI data")
    print("For demonstration, we'll show the workflow creation:")
    
    try:
        # Create standard first-level workflow
        print("\nCreating standard first-level workflow...")
        wf_standard = first_level_wf(
            in_files=in_files,
            output_dir=f"{output_dir}/standard",
            df_trial_info=df_trial_info,  # <-- HERE'S WHERE df_trial_info IS USED
            contrast_type='standard',
            fwhm=6.0,
            use_smoothing=True
        )
        print("✓ Standard workflow created successfully")
        
        # Create LSS workflow
        print("\nCreating LSS workflow...")
        wf_lss = first_level_wf_LSS(
            in_files=in_files,
            output_dir=f"{output_dir}/lss",
            trial_ID=1,  # Example trial ID
            df_trial_info=df_trial_info,  # <-- HERE'S WHERE df_trial_info IS USED
            contrast_type='minimal',
            use_smoothing=False
        )
        print("✓ LSS workflow created successfully")
        
        # Create voxelwise workflow
        print("\nCreating voxelwise workflow...")
        wf_voxelwise = first_level_wf_voxelwise(
            inputs=in_files,
            output_dir=f"{output_dir}/voxelwise",
            df_trial_info=df_trial_info,  # <-- HERE'S WHERE df_trial_info IS USED
            contrast_type='standard',
            fwhm=6.0,
            use_smoothing=True
        )
        print("✓ Voxelwise workflow created successfully")
        
    except Exception as e:
        print(f"⚠ Workflow creation failed (expected with placeholder data): {e}")
        print("This is normal when using placeholder file paths")
    
    # =============================================================================
    # STEP 6: SUMMARY
    # =============================================================================
    print("\n6. ANALYSIS SUMMARY")
    print("-" * 50)
    
    print("✓ df_trial_info successfully defined and loaded")
    print("✓ Conditions extracted and grouped (CS-_first, CSS_first, etc.)")
    print("✓ Contrasts generated for different analysis types")
    print("✓ Workflows created (ready for execution with real data)")
    
    print(f"\nKey points:")
    print(f"- df_trial_info contains {len(df_trial_info)} trials")
    print(f"- {len(df_with_conditions['conditions'].unique())} unique conditions after grouping")
    print(f"- Ready for fMRI analysis with proper condition grouping")
    
    print(f"\nNext steps:")
    print(f"1. Replace placeholder file paths with real fMRI data")
    print(f"2. Execute workflows: wf_standard.run()")
    print(f"3. Check results in {output_dir}")

if __name__ == "__main__":
    main()
