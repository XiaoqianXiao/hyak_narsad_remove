#!/usr/bin/env python3
"""
Generate contrast CSV files for NARSAD phase2 and phase3 events
"""

import pandas as pd
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_cs_conditions(df_trial_info):
    """
    Extract and group CS-, CSS, and CSR conditions from a pandas DataFrame.
    
    This function adds a 'conditions' column to the DataFrame that groups trials:
    - First trial of each CS type becomes 'CS-_first', 'CSS_first', 'CSR_first'
    - Remaining trials of each type become 'CS-_others', 'CSS_others', 'CSR_others'
    - All other trials keep their original trial_type as conditions value
    """
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
    
    logger.info(f"Using DataFrame input with {len(df_work)} trials")
    logger.info(f"DataFrame columns: {list(df_work.columns)}")
    
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
        logger.info(f"CS- conditions: first trial at index {cs_first_idx}, {len(cs_other_indices)} others")
    
    # Update conditions column for CSS trials
    if not css_trials.empty:
        css_first_idx = css_trials.sort_values('onset').index[0]
        df_work.loc[css_first_idx, 'conditions'] = 'CSS_first'
        css_other_indices = css_trials[css_trials.index != css_first_idx].index
        df_work.loc[css_other_indices, 'conditions'] = 'CSS_others'
        logger.info(f"CSS conditions: first trial at index {css_first_idx}, {len(css_other_indices)} others")
    
    # Update conditions column for CSR trials
    if not csr_trials.empty:
        csr_first_idx = csr_trials.sort_values('onset').index[0]
        df_work.loc[csr_first_idx, 'conditions'] = 'CSR_first'
        csr_other_indices = csr_trials[csr_trials.index != csr_first_idx].index
        df_work.loc[csr_other_indices, 'conditions'] = 'CSR_others'
        logger.info(f"CSR conditions: first trial at index {csr_first_idx}, {len(csr_other_indices)} others")
    
    # Get unique conditions for contrast generation
    unique_conditions = df_work['conditions'].unique().tolist()
    logger.info(f"Unique conditions for contrast generation: {unique_conditions}")
    
    # Extract grouped conditions for backward compatibility
    cs_conditions = {'first': 'CS-_first' if 'CS-_first' in unique_conditions else None, 
                     'other': ['CS-_others'] if 'CS-_others' in unique_conditions else []}
    css_conditions = {'first': 'CSS_first' if 'CSS_first' in unique_conditions else None, 
                      'other': ['CSS_others'] if 'CSS_others' in unique_conditions else []}
    csr_conditions = {'first': 'CSR_first' if 'CSR_first' in unique_conditions else None, 
                      'other': ['CSR_others'] if 'CSR_others' in unique_conditions else []}
    
    # Get other conditions (non-CS/CSS/CSR)
    other_conditions = df_work[~df_work['trial_type'].str.startswith('CS')]['trial_type'].unique().tolist()
    
    logger.info(f"Processed conditions: CS-={cs_conditions}, CSS={css_conditions}, CSR={csr_conditions}")
    logger.info(f"Other conditions: {other_conditions}")
    
    return df_work, cs_conditions, css_conditions, csr_conditions, other_conditions


def create_interesting_contrasts(df_trial_info):
    """
    Create only the interesting contrasts for NARSAD analysis.
    
    This function creates a focused set of contrasts that are most relevant
    for the NARSAD study, focusing on comparisons between "others" conditions
    and baseline, as well as between different "others" conditions.
    """
    if df_trial_info is None:
        raise ValueError("df_trial_info is required")
    
    # Extract CS-, CSS, and CSR conditions with grouping
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    # Use the conditions column for contrast generation
    all_contrast_conditions = df_with_conditions['conditions'].unique().tolist()
    
    # Define the interesting contrasts
    interesting_contrasts = [
        ("CS-_others > FIXATION", "Other CS- trials vs baseline"),
        ("CSS_others > FIXATION", "Other CSS trials vs baseline"),
        ("CSR_others > FIXATION", "Other CSR trials vs baseline"),
        ("CSS_others > CSR_others", "Other CSS trials vs Other CSR trials"),
        ("CSR_others > CSS_others", "Other CSR trials vs Other CSS trials"),
        ("CSS_others > CS-_others", "Other CSS trials vs Other CS- trials"),
        ("CSR_others > CS-_others", "Other CSR trials vs Other CS- trials"),
        ("CS-_others > CSS_others", "Other CS- trials vs Other CSS trials"),
        ("CS-_others > CSR_others", "Other CS- trials vs Other CSR trials"),
    ]
    
    contrasts = []
    
    for contrast_name, description in interesting_contrasts:
        # Parse the contrast name (e.g., "CS-_others > FIXATION")
        if ' > ' in contrast_name:
            condition1, condition2 = contrast_name.split(' > ')
            condition1 = condition1.strip()
            condition2 = condition2.strip()
            
            # Check if both conditions exist
            if condition1 in all_contrast_conditions and condition2 in all_contrast_conditions:
                contrast = (contrast_name, 'T', [condition1, condition2], [1, -1])
                contrasts.append(contrast)
                logger.info(f"Added contrast: {contrast_name} - {description}")
            else:
                logger.warning(f"Contrast {contrast_name}: conditions {condition1}, {condition2} not found in {all_contrast_conditions}")
        else:
            logger.warning(f"Invalid contrast format: {contrast_name}")
    
    logger.info(f"Created {len(contrasts)} interesting contrasts")
    
    return contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions


def generate_contrast_csv(events_file, output_file):
    """
    Generate contrast CSV file for a given events file.
    
    Args:
        events_file (str): Path to events CSV file
        output_file (str): Path to output contrast CSV file
    """
    print(f"\n{'='*60}")
    print(f"PROCESSING: {os.path.basename(events_file)}")
    print(f"{'='*60}")
    
    # Load events file
    df_trial_info = pd.read_csv(events_file)
    print(f"Loaded {len(df_trial_info)} trials from {events_file}")
    print(f"Trial types: {sorted(df_trial_info['trial_type'].unique())}")
    
    # Generate contrasts
    contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions = create_interesting_contrasts(df_trial_info)
    
    # Create contrast DataFrame
    contrast_data = []
    for i, contrast in enumerate(contrasts, 1):
        contrast_data.append({
            'contrast_id': i,
            'contrast_name': contrast[0],
            'contrast_type': contrast[1],
            'condition1': contrast[2][0],
            'condition2': contrast[2][1],
            'weight1': contrast[3][0],
            'weight2': contrast[3][1],
            'description': f"C{i}: {contrast[0]}"
        })
    
    contrast_df = pd.DataFrame(contrast_data)
    
    # Save to CSV
    contrast_df.to_csv(output_file, index=False)
    print(f"✅ Saved {len(contrast_df)} contrasts to {output_file}")
    
    # Display summary
    print(f"\nContrast Summary:")
    print(f"  • Total contrasts: {len(contrast_df)}")
    print(f"  • Condition1 range: {contrast_df['condition1'].unique()}")
    print(f"  • Condition2 range: {contrast_df['condition2'].unique()}")
    print(f"  • All contrasts are T-contrasts")
    
    return contrast_df


def main():
    """Main function to generate contrast CSV files for both phases."""
    
    print("=" * 80)
    print("GENERATING CONTRAST CSV FILES FOR NARSAD PHASES")
    print("=" * 80)
    
    # Define paths
    behav_dir = "/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav"
    phase2_events = os.path.join(behav_dir, "task-Narsad_phase2_events.csv")
    phase3_events = os.path.join(behav_dir, "task-Narsad_phase3_events.csv")
    
    # Check if files exist
    if not os.path.exists(phase2_events):
        print(f"❌ Error: {phase2_events} not found")
        return 1
    
    if not os.path.exists(phase3_events):
        print(f"❌ Error: {phase3_events} not found")
        return 1
    
    # Generate contrast CSV for phase2
    phase2_output = "narsad_phase2_contrasts.csv"
    try:
        phase2_df = generate_contrast_csv(phase2_events, phase2_output)
    except Exception as e:
        print(f"❌ Error processing phase2: {e}")
        return 1
    
    # Generate contrast CSV for phase3
    phase3_output = "narsad_phase3_contrasts.csv"
    try:
        phase3_df = generate_contrast_csv(phase3_events, phase3_output)
    except Exception as e:
        print(f"❌ Error processing phase3: {e}")
        return 1
    
    # Summary
    print(f"\n{'='*80}")
    print("GENERATION COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Phase2 contrasts: {phase2_output} ({len(phase2_df)} contrasts)")
    print(f"✅ Phase3 contrasts: {phase3_output} ({len(phase3_df)} contrasts)")
    print(f"\nBoth files contain the 9 interesting contrasts:")
    print("  1. CS-_others > FIXATION")
    print("  2. CSS_others > FIXATION")
    print("  3. CSR_others > FIXATION")
    print("  4. CSS_others > CSR_others")
    print("  5. CSR_others > CSS_others")
    print("  6. CSS_others > CS-_others")
    print("  7. CSR_others > CS-_others")
    print("  8. CS-_others > CSS_others")
    print("  9. CS-_others > CSR_others")
    
    return 0


if __name__ == "__main__":
    exit(main())
