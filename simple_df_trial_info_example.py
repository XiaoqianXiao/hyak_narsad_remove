#!/usr/bin/env python3
"""
Simple example showing where df_trial_info is defined and used
"""

import pandas as pd
import os

def main():
    print("=" * 60)
    print("SIMPLE df_trial_info DEFINITION EXAMPLE")
    print("=" * 60)
    
    # =============================================================================
    # THIS IS WHERE df_trial_info IS DEFINED
    # =============================================================================
    print("\n1. DEFINING df_trial_info")
    print("-" * 30)
    
    # Method 1: Load from CSV file (most common)
    data_path = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if os.path.exists(data_path):
        df_trial_info = pd.read_csv(data_path)
        print(f"✓ Loaded from CSV: {df_trial_info.shape}")
        print(f"✓ File: {data_path}")
    else:
        # Method 2: Create example data
        print("CSV not found, creating example data...")
        df_trial_info = pd.DataFrame({
            'trial_type': ['FIXATION', 'CS-', 'FIXATION', 'CSS', 'US_CSS', 'CSR', 'FIXATION', 'CS-', 'CSS', 'US_CSR'],
            'onset': [0, 12, 18, 31, 37, 50, 56, 68, 74, 80],
            'duration': [12, 6, 13, 6, 0, 6, 12, 6, 6, 0]
        })
        print(f"✓ Created example data: {df_trial_info.shape}")
    
    print(f"✓ Columns: {list(df_trial_info.columns)}")
    print(f"✓ Trial types: {sorted(df_trial_info['trial_type'].unique())}")
    print(f"✓ Time range: {df_trial_info['onset'].min():.1f} - {df_trial_info['onset'].max():.1f} seconds")
    
    # Show the data
    print(f"\nFirst 10 trials:")
    print(df_trial_info.head(10))
    
    # =============================================================================
    # THIS IS HOW df_trial_info IS USED
    # =============================================================================
    print(f"\n2. HOW df_trial_info IS USED")
    print("-" * 30)
    
    print("df_trial_info is passed to workflow functions like this:")
    print("")
    print("  # In your analysis script:")
    print("  df_trial_info = pd.read_csv('your_events_file.csv')")
    print("")
    print("  # Then pass it to workflow functions:")
    print("  wf = first_level_wf(")
    print("      in_files=in_files,")
    print("      output_dir=output_dir,")
    print("      df_trial_info=df_trial_info,  # <-- HERE!")
    print("      contrast_type='standard'")
    print("  )")
    print("")
    print("  # Or for condition extraction:")
    print("  df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)")
    print("")
    print("  # Or for contrast generation:")
    print("  contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions = create_contrasts(df_trial_info, contrast_type='standard')")
    
    # =============================================================================
    # DEMONSTRATE THE FUNCTIONS (without nipype)
    # =============================================================================
    print(f"\n3. DEMONSTRATING FUNCTIONS")
    print("-" * 30)
    
    # Import the functions we can use without nipype
    try:
        # Add the current directory to path
        import sys
        sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')
        
        # Import just the functions that don't require nipype
        from first_level_workflows import extract_cs_conditions, create_contrasts
        
        print("✓ Successfully imported functions")
        
        # Use extract_cs_conditions
        print("\nUsing extract_cs_conditions:")
        df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
        
        print(f"✓ CS- first: {cs_conditions['first']}")
        print(f"✓ CS- others: {cs_conditions['other']}")
        print(f"✓ CSS first: {css_conditions['first']}")
        print(f"✓ CSS others: {css_conditions['other']}")
        print(f"✓ CSR first: {csr_conditions['first']}")
        print(f"✓ CSR others: {csr_conditions['other']}")
        
        # Use create_contrasts
        print("\nUsing create_contrasts:")
        contrasts, cs_cond, css_cond, csr_cond, other_cond = create_contrasts(df_trial_info, contrast_type='minimal')
        
        print(f"✓ Generated {len(contrasts)} contrasts")
        for i, contrast in enumerate(contrasts[:5], 1):
            print(f"  {i}. {contrast[0]}")
        
    except ImportError as e:
        print(f"⚠ Could not import workflow functions: {e}")
        print("This is expected if nipype is not installed")
        print("But the df_trial_info definition still works!")
    
    # =============================================================================
    # SUMMARY
    # =============================================================================
    print(f"\n4. SUMMARY")
    print("-" * 30)
    print("✓ df_trial_info is defined by loading your event data CSV")
    print("✓ It contains columns: 'trial_type', 'onset', 'duration'")
    print("✓ It's passed to workflow functions as a parameter")
    print("✓ The workflow functions use it internally to generate contrasts and session info")
    print("✓ This is the standard way to use the NARSAD analysis pipeline")

if __name__ == "__main__":
    main()
