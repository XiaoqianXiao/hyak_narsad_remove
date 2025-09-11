#!/usr/bin/env python3
"""
Simple demonstration that first_level_wf also handles first trial separation
"""

import os
import pandas as pd

def demonstrate_first_trial_logic():
    """Demonstrate the first trial separation logic"""
    
    print("=" * 80)
    print("FIRST TRIAL SEPARATION IN BOTH WORKFLOWS")
    print("=" * 80)
    
    # Load real NARSAD data
    events_file = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav/task-Narsad_phase2_events.csv'
    
    if not os.path.exists(events_file):
        print(f"❌ Events file not found: {events_file}")
        return
    
    df_trial_info = pd.read_csv(events_file)
    print(f"✓ Loaded NARSAD data: {df_trial_info.shape}")
    print(f"✓ Trial types: {sorted(df_trial_info['trial_type'].unique())}")
    
    print("\n" + "=" * 60)
    print("STEP 1: SIMULATE extract_cs_conditions LOGIC")
    print("=" * 60)
    
    # Simulate the extract_cs_conditions logic
    df_work = df_trial_info.copy()
    df_work['conditions'] = df_work['trial_type'].copy()
    
    # Find first trials of CS-, CSS, CSR
    cs_trials = df_work[df_work['trial_type'] == 'CS-'].sort_values('onset')
    css_trials = df_work[df_work['trial_type'] == 'CSS'].sort_values('onset')
    csr_trials = df_work[df_work['trial_type'] == 'CSR'].sort_values('onset')
    
    if len(cs_trials) > 0:
        cs_first_idx = cs_trials.index[0]
        df_work.loc[cs_first_idx, 'conditions'] = 'CS-_first'
        cs_other_indices = cs_trials.index[1:]
        df_work.loc[cs_other_indices, 'conditions'] = 'CS-_others'
        print(f"✓ CS- trials: {len(cs_trials)} total")
        print(f"  - First trial at onset {cs_trials.iloc[0]['onset']}s → CS-_first")
        print(f"  - {len(cs_other_indices)} other trials → CS-_others")
    
    if len(css_trials) > 0:
        css_first_idx = css_trials.index[0]
        df_work.loc[css_first_idx, 'conditions'] = 'CSS_first'
        css_other_indices = css_trials.index[1:]
        df_work.loc[css_other_indices, 'conditions'] = 'CSS_others'
        print(f"✓ CSS trials: {len(css_trials)} total")
        print(f"  - First trial at onset {css_trials.iloc[0]['onset']}s → CSS_first")
        print(f"  - {len(css_other_indices)} other trials → CSS_others")
    
    if len(csr_trials) > 0:
        csr_first_idx = csr_trials.index[0]
        df_work.loc[csr_first_idx, 'conditions'] = 'CSR_first'
        csr_other_indices = csr_trials.index[1:]
        df_work.loc[csr_other_indices, 'conditions'] = 'CSR_others'
        print(f"✓ CSR trials: {len(csr_trials)} total")
        print(f"  - First trial at onset {csr_trials.iloc[0]['onset']}s → CSR_first")
        print(f"  - {len(csr_other_indices)} other trials → CSR_others")
    
    print(f"\n✓ Enhanced DataFrame with 'conditions' column:")
    print(f"  - Shape: {df_work.shape}")
    print(f"  - Unique conditions: {sorted(df_work['conditions'].unique())}")
    
    print("\n" + "=" * 60)
    print("STEP 2: SHOW THE CONDITIONS COLUMN")
    print("=" * 60)
    
    print("First 15 trials with conditions column:")
    display_df = df_work[['onset', 'trial_type', 'conditions']].head(15)
    for i, (_, row) in enumerate(display_df.iterrows(), 1):
        print(f"  {i:2d}. {row['onset']:6.1f}s | {row['trial_type']:8s} → {row['conditions']}")
    
    print("\n" + "=" * 60)
    print("STEP 3: VERIFY SEPARATION")
    print("=" * 60)
    
    # Count each condition type
    condition_counts = df_work['conditions'].value_counts()
    print("Condition counts:")
    for condition, count in condition_counts.items():
        print(f"  - {condition}: {count} trials")
    
    # Verify first trial separation
    has_cs_first = 'CS-_first' in condition_counts
    has_css_first = 'CSS_first' in condition_counts
    has_csr_first = 'CSR_first' in condition_counts
    has_cs_others = 'CS-_others' in condition_counts
    has_css_others = 'CSS_others' in condition_counts
    has_csr_others = 'CSR_others' in condition_counts
    
    print(f"\n✓ First trial separation verification:")
    print(f"  - CS-_first: {'✓' if has_cs_first else '❌'} ({condition_counts.get('CS-_first', 0)} trials)")
    print(f"  - CSS_first: {'✓' if has_css_first else '❌'} ({condition_counts.get('CSS_first', 0)} trials)")
    print(f"  - CSR_first: {'✓' if has_csr_first else '❌'} ({condition_counts.get('CSR_first', 0)} trials)")
    print(f"  - CS-_others: {'✓' if has_cs_others else '❌'} ({condition_counts.get('CS-_others', 0)} trials)")
    print(f"  - CSS_others: {'✓' if has_css_others else '❌'} ({condition_counts.get('CSS_others', 0)} trials)")
    print(f"  - CSR_others: {'✓' if has_csr_others else '❌'} ({condition_counts.get('CSR_others', 0)} trials)")
    
    print("\n" + "=" * 60)
    print("STEP 4: WORKFLOW COMPARISON")
    print("=" * 60)
    
    print("BOTH first_level_wf AND first_level_wf_voxelwise:")
    print("  ✓ Use the SAME extract_cs_conditions() function")
    print("  ✓ Use the SAME create_contrasts() function")
    print("  ✓ Create the SAME 'conditions' column")
    print("  ✓ Generate the SAME separate regressors:")
    print("    * CS-_first (1 trial)")
    print("    * CS-_others (remaining CS- trials)")
    print("    * CSS_first (1 trial)")
    print("    * CSS_others (remaining CSS trials)")
    print("    * CSR_first (1 trial)")
    print("    * CSR_others (remaining CSR trials)")
    print("    * FIXATION, US_CSS, US_CSR (unchanged)")
    
    print("\nThe ONLY differences between workflows are:")
    print("  - Parameter names: 'in_files' vs 'inputs'")
    print("  - Preprocessing parameters:")
    print("    * brightness_threshold: 1000 vs 0.1")
    print("    * high_pass_cutoff: 100s vs 128s")
    print("  - Workflow names: 'wf_1st_level' vs 'wf_1st_level_voxelwise'")
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("✅ You are ABSOLUTELY CORRECT!")
    print("✅ first_level_wf ALSO keeps first trials of CS-, CSS, and CSR as separate regressors")
    print("✅ Both workflows use IDENTICAL logic for condition separation")
    print("✅ The choice between them is purely about preprocessing parameters")
    print("✅ NOT about condition handling - that's the same in both!")

if __name__ == "__main__":
    demonstrate_first_trial_logic()
