#!/usr/bin/env python3
"""
Test script to verify the visualization works correctly
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Configure matplotlib for display
plt.ion()  # Turn on interactive mode
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

# Add path to import from first_level_workflows
sys.path.append('/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove')
from first_level_workflows import extract_cs_conditions, create_interesting_contrasts

def create_design_matrix_viz(df_processed, contrasts, title):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(title, fontsize=16)
    
    unique_conditions = df_processed['conditions'].unique()
    condition_counts = {cond: len(df_processed[df_processed['conditions'] == cond]) 
                       for cond in unique_conditions}
    
    # 1. Condition counts
    conditions = list(condition_counts.keys())
    counts = list(condition_counts.values())
    bars = ax1.bar(range(len(conditions)), counts)
    ax1.set_title('Trial Counts per Condition')
    ax1.set_xticks(range(len(conditions)))
    ax1.set_xticklabels(conditions, rotation=45, ha='right')
    for bar, count in zip(bars, counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom')
    
    # 2. Trial timeline
    y_pos = 0
    for condition in sorted(unique_conditions):
        condition_trials = df_processed[df_processed['conditions'] == condition]
        for _, trial in condition_trials.iterrows():
            ax2.barh(y_pos, trial['duration'], left=trial['onset'], 
                    height=0.8, alpha=0.7, label=condition if y_pos == 0 else '')
        y_pos += 1
    ax2.set_title('Trial Timeline')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Conditions')
    ax2.set_yticks(range(len(unique_conditions)))
    ax2.set_yticklabels(sorted(unique_conditions))
    
    # 3. Contrast matrix
    contrast_matrix = []
    contrast_names = []
    for name, _, conditions, weights in contrasts:
        contrast_names.append(name)
        contrast_row = []
        for condition in sorted(unique_conditions):
            if condition in conditions:
                weight_idx = conditions.index(condition)
                contrast_row.append(weights[weight_idx])
            else:
                contrast_row.append(0)
        contrast_matrix.append(contrast_row)
    
    contrast_matrix = np.array(contrast_matrix)
    im = ax3.imshow(contrast_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    ax3.set_xticks(range(len(sorted(unique_conditions))))
    ax3.set_xticklabels(sorted(unique_conditions), rotation=45, ha='right')
    ax3.set_yticks(range(len(contrast_names)))
    ax3.set_yticklabels(contrast_names)
    ax3.set_title('Contrast Matrix')
    
    # Add text annotations
    for i in range(len(contrast_names)):
        for j in range(len(sorted(unique_conditions))):
            weight = contrast_matrix[i, j]
            if weight != 0:
                ax3.text(j, i, f'{weight:.0f}', ha='center', va='center', 
                        color='white' if abs(weight) > 0.5 else 'black', fontweight='bold')
    
    # 4. Summary
    ax4.axis('off')
    summary = f"""Summary:
• Total Conditions: {len(unique_conditions)}
• Total Trials: {len(df_processed)}
• Total Contrasts: {len(contrasts)}

Condition Groups:
• First Trials: {len([c for c in unique_conditions if '_first' in c])}
• Other Trials: {len([c for c in unique_conditions if '_others' in c])}
• Baseline: {len([c for c in unique_conditions if c == 'FIXATION'])}
• Other: {len([c for c in unique_conditions if '_first' not in c and '_others' not in c and c != 'FIXATION'])}"""
    
    ax4.text(0.1, 0.9, summary, transform=ax4.transAxes, fontsize=12,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    print("Testing NARSAD Trial Tracking Analysis...")
    
    # Load data
    behav_dir = '/Users/xiaoqianxiao/projects/NARSAD/MRI/source_data/behav'
    phase2_df = pd.read_csv(os.path.join(behav_dir, 'task-Narsad_phase2_events.csv'))
    
    print(f"Loaded Phase 2: {len(phase2_df)} trials")
    
    # Process data
    phase2_processed, _, _, _, _ = extract_cs_conditions(phase2_df)
    phase2_contrasts, _, _, _, _ = create_interesting_contrasts(phase2_df)
    
    print(f"Generated: {len(phase2_processed['conditions'].unique())} conditions, {len(phase2_contrasts)} contrasts")
    
    # Create visualization
    print("Creating visualization...")
    fig = create_design_matrix_viz(phase2_processed, phase2_contrasts, "Phase 2 Design Matrix")
    
    # Save figure
    plt.savefig('narsad_design_matrix_visualization.png', dpi=150, bbox_inches='tight')
    print("✅ Figure saved as 'narsad_design_matrix_visualization.png'")
    
    # Show figure
    plt.show()
    print("✅ Visualization complete!")

if __name__ == "__main__":
    main()
