#!/usr/bin/env python3
"""
Example script showing how to define df_trial_info and use it with existing workflow functions
This demonstrates the proper way to integrate df_trial_info into the analysis pipeline
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add current directory to path
sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')

from first_level_workflows import (
    first_level_wf, 
    first_level_wf_LSS, 
    first_level_wf_voxelwise,
    extract_cs_conditions,
    create_contrasts
)

def define_df_trial_info():
    """
    Define df_trial_info - this is where you load your trial data
    """
    print("=" * 60)
    print("DEFINING df_trial_info")
    print("=" * 60)
    
    # Method 1: Load from CSV file (most common)
    data_path = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if os.path.exists(data_path):
        df_trial_info = pd.read_csv(data_path)
        print(f"✓ Loaded from CSV: {df_trial_info.shape}")
    else:
        # Method 2: Create from scratch (for testing)
        print("CSV not found, creating example data...")
        df_trial_info = pd.DataFrame({
            'trial_type': ['FIXATION', 'CS-', 'FIXATION', 'CSS', 'US_CSS', 'CSR', 'FIXATION', 'CS-', 'CSS', 'US_CSR'],
            'onset': [0, 12, 18, 31, 37, 50, 56, 68, 74, 80],
            'duration': [12, 6, 13, 6, 0, 6, 12, 6, 6, 0]
        })
        print(f"✓ Created example data: {df_trial_info.shape}")
    
    print(f"Columns: {list(df_trial_info.columns)}")
    print(f"Trial types: {sorted(df_trial_info['trial_type'].unique())}")
    print(f"Time range: {df_trial_info['onset'].min():.1f} - {df_trial_info['onset'].max():.1f} seconds")
    
    return df_trial_info

def run_standard_analysis(df_trial_info):
    """
    Run standard first-level analysis using df_trial_info
    """
    print("\n" + "=" * 60)
    print("STANDARD FIRST-LEVEL ANALYSIS")
    print("=" * 60)
    
    # Define input files (replace with your actual paths)
    in_files = {
        'sub-01': {
            'bold': '/path/to/sub-01_task-narsad_bold.nii.gz',
            'mask': '/path/to/sub-01_task-narsad_brainmask.nii.gz',
            'events': '/path/to/sub-01_task-narsad_events.tsv',
            'regressors': '/path/to/sub-01_task-narsad_confounds.tsv',
            'tr': 2.5
        }
    }
    
    output_dir = '/tmp/narsad_analysis/standard'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create workflow
    wf = first_level_wf(
        in_files=in_files,
        output_dir=output_dir,
        df_trial_info=df_trial_info,  # <-- df_trial_info is passed here
        contrast_type='standard',
        fwhm=6.0,
        use_smoothing=True
    )
    
    print(f"✓ Workflow created for standard analysis")
    print(f"✓ df_trial_info used to generate contrasts and session info")
    print(f"✓ Output directory: {output_dir}")
    
    return wf

def run_lss_analysis(df_trial_info):
    """
    Run LSS (Least Squares Separate) analysis using df_trial_info
    """
    print("\n" + "=" * 60)
    print("LSS ANALYSIS")
    print("=" * 60)
    
    # Define input files
    in_files = {
        'sub-01': {
            'bold': '/path/to/sub-01_task-narsad_bold.nii.gz',
            'mask': '/path/to/sub-01_task-narsad_brainmask.nii.gz',
            'events': '/path/to/sub-01_task-narsad_events.tsv',
            'regressors': '/path/to/sub-01_task-narsad_confounds.tsv',
            'tr': 2.5
        }
    }
    
    output_dir = '/tmp/narsad_analysis/lss'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create LSS workflow for trial ID 1
    wf = first_level_wf_LSS(
        in_files=in_files,
        output_dir=output_dir,
        trial_ID=1,  # Which trial to analyze
        df_trial_info=df_trial_info,  # <-- df_trial_info is passed here
        contrast_type='minimal',
        use_smoothing=False
    )
    
    print(f"✓ LSS workflow created for trial ID 1")
    print(f"✓ df_trial_info used to generate trial-specific contrasts")
    print(f"✓ Output directory: {output_dir}")
    
    return wf

def run_voxelwise_analysis(df_trial_info):
    """
    Run voxelwise analysis using df_trial_info
    """
    print("\n" + "=" * 60)
    print("VOXELWISE ANALYSIS")
    print("=" * 60)
    
    # Define input files
    inputs = {
        'sub-01': {
            'bold': '/path/to/sub-01_task-narsad_bold.nii.gz',
            'mask': '/path/to/sub-01_task-narsad_brainmask.nii.gz',
            'events': '/path/to/sub-01_task-narsad_events.tsv',
            'regressors': '/path/to/sub-01_task-narsad_confounds.tsv',
            'tr': 2.5
        }
    }
    
    output_dir = '/tmp/narsad_analysis/voxelwise'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create voxelwise workflow
    wf = first_level_wf_voxelwise(
        inputs=inputs,
        output_dir=output_dir,
        df_trial_info=df_trial_info,  # <-- df_trial_info is passed here
        contrast_type='standard',
        fwhm=6.0,
        use_smoothing=True
    )
    
    print(f"✓ Voxelwise workflow created")
    print(f"✓ df_trial_info used to generate voxelwise contrasts")
    print(f"✓ Output directory: {output_dir}")
    
    return wf

def demonstrate_condition_extraction(df_trial_info):
    """
    Demonstrate how df_trial_info is used to extract conditions
    """
    print("\n" + "=" * 60)
    print("CONDITION EXTRACTION DEMONSTRATION")
    print("=" * 60)
    
    # Extract conditions using df_trial_info
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    print(f"✓ Conditions extracted from df_trial_info")
    print(f"✓ CS- first: {cs_conditions['first']}")
    print(f"✓ CS- others: {cs_conditions['other']}")
    print(f"✓ CSS first: {css_conditions['first']}")
    print(f"✓ CSS others: {css_conditions['other']}")
    print(f"✓ CSR first: {csr_conditions['first']}")
    print(f"✓ CSR others: {csr_conditions['other']}")
    print(f"✓ Other conditions: {other_conditions}")
    
    # Show the enhanced DataFrame
    print(f"\nEnhanced DataFrame with 'conditions' column:")
    print(df_with_conditions[['trial_type', 'conditions', 'onset', 'duration']].head(10))
    
    return df_with_conditions

def demonstrate_contrast_generation(df_trial_info):
    """
    Demonstrate how df_trial_info is used to generate contrasts
    """
    print("\n" + "=" * 60)
    print("CONTRAST GENERATION DEMONSTRATION")
    print("=" * 60)
    
    # Generate contrasts using df_trial_info
    contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions = create_contrasts(df_trial_info, contrast_type='minimal')
    
    print(f"✓ Generated {len(contrasts)} contrasts from df_trial_info")
    print(f"✓ Contrast types: {[c[0] for c in contrasts]}")
    
    # Show first few contrasts
    print(f"\nFirst 5 contrasts:")
    for i, contrast in enumerate(contrasts[:5], 1):
        print(f"  {i}. {contrast[0]}")
    
    return contrasts

def main():
    """
    Main function demonstrating df_trial_info usage
    """
    print("NARSAD ANALYSIS WITH df_trial_info")
    print("This script shows how to define and use df_trial_info in your analysis")
    
    # Step 1: Define df_trial_info
    df_trial_info = define_df_trial_info()
    
    # Step 2: Demonstrate condition extraction
    df_with_conditions = demonstrate_condition_extraction(df_trial_info)
    
    # Step 3: Demonstrate contrast generation
    contrasts = demonstrate_contrast_generation(df_trial_info)
    
    # Step 4: Create workflows (demonstration)
    print("\n" + "=" * 60)
    print("WORKFLOW CREATION (DEMONSTRATION)")
    print("=" * 60)
    print("Note: These workflows are created but not executed (would need real data)")
    
    try:
        # Create different types of workflows
        wf_standard = run_standard_analysis(df_trial_info)
        wf_lss = run_lss_analysis(df_trial_info)
        wf_voxelwise = run_voxelwise_analysis(df_trial_info)
        
        print(f"\n✓ All workflows created successfully")
        print(f"✓ df_trial_info was used in all workflow functions")
        
    except Exception as e:
        print(f"⚠ Workflow creation failed (expected with placeholder data): {e}")
        print("This is normal when using placeholder file paths")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ df_trial_info defined and loaded")
    print("✓ Conditions extracted and grouped")
    print("✓ Contrasts generated")
    print("✓ Workflows created (ready for execution with real data)")
    print(f"\nKey point: df_trial_info is passed to all workflow functions")
    print(f"and used internally to generate contrasts and session info")

if __name__ == "__main__":
    main()
