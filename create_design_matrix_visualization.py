#!/usr/bin/env python3
"""
Create a design matrix visualization similar to the figure shown
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import seaborn as sns

def create_design_matrix_visualization():
    """Create a design matrix visualization for NARSAD data"""
    
    # Load the data
    df_conditions = pd.read_csv('narsad_conditions_data.csv')
    df_contrasts = pd.read_csv('narsad_contrasts_minimal.csv')
    
    # Set up the figure
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(4, 3, height_ratios=[2, 1, 1, 1], width_ratios=[1, 3, 1], 
                  hspace=0.3, wspace=0.3)
    
    # Get unique conditions and create design matrix
    unique_conditions = sorted(df_conditions['conditions'].unique())
    n_conditions = len(unique_conditions)
    
    # Create a simple design matrix representation
    # For visualization, we'll show which trials belong to which condition
    design_matrix = np.zeros((len(df_conditions), n_conditions))
    
    for i, condition in enumerate(unique_conditions):
        trial_indices = df_conditions[df_conditions['conditions'] == condition].index
        design_matrix[trial_indices, i] = 1
    
    # Main design matrix plot
    ax_main = fig.add_subplot(gs[0, 1])
    
    # Create heatmap of design matrix
    im = ax_main.imshow(design_matrix.T, cmap='Reds', aspect='auto', interpolation='nearest')
    
    # Set labels
    ax_main.set_xlabel('Trial Number', fontsize=12, fontweight='bold')
    ax_main.set_ylabel('Regressors', fontsize=12, fontweight='bold')
    ax_main.set_title('Design Matrix: NARSAD Conditions', fontsize=14, fontweight='bold')
    
    # Set y-axis labels
    ax_main.set_yticks(range(n_conditions))
    ax_main.set_yticklabels(unique_conditions, fontsize=10)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax_main, shrink=0.8)
    cbar.set_label('Regressor Activity', fontsize=10)
    
    # Add grid
    ax_main.grid(True, alpha=0.3)
    
    # Left panel - Condition slider/selector
    ax_slider = fig.add_subplot(gs[0, 0])
    ax_slider.set_xlim(0, 1)
    ax_slider.set_ylim(0, n_conditions)
    ax_slider.axis('off')
    
    # Create slider-like visualization
    for i, condition in enumerate(unique_conditions):
        y_pos = n_conditions - i - 0.5
        color = 'red' if i == 0 else 'lightgray'
        rect = patches.Rectangle((0.2, y_pos-0.4), 0.6, 0.8, 
                               facecolor=color, edgecolor='black', linewidth=1)
        ax_slider.add_patch(rect)
        ax_slider.text(0.5, y_pos, f'R{i+1}', ha='center', va='center', 
                      fontsize=8, fontweight='bold', color='white')
    
    ax_slider.set_title('Regressors', fontsize=12, fontweight='bold')
    
    # Right panel - Contrast information
    ax_contrasts = fig.add_subplot(gs[0, 2])
    ax_contrasts.axis('off')
    
    # Show some key contrasts
    contrast_text = "Key Contrasts:\n\n"
    for i, (_, contrast) in enumerate(df_contrasts.head(6).iterrows()):
        contrast_text += f"C{i+1}: {contrast['contrast_name']}\n"
    
    ax_contrasts.text(0.05, 0.95, contrast_text, transform=ax_contrasts.transAxes,
                     fontsize=9, verticalalignment='top', fontfamily='monospace')
    ax_contrasts.set_title('Contrasts', fontsize=12, fontweight='bold')
    
    # Bottom panels - Detailed information
    # Panel 1: Condition details
    ax_details = fig.add_subplot(gs[1, :])
    ax_details.axis('off')
    
    # Create a table showing condition details
    condition_data = []
    for condition in unique_conditions:
        trials = df_conditions[df_conditions['conditions'] == condition]
        condition_data.append({
            'Condition': condition,
            'Trial Count': len(trials),
            'First Onset': f"{trials['onset'].min():.0f}s",
            'Last Onset': f"{trials['onset'].max():.0f}s",
            'Duration': f"{trials['duration'].iloc[0]:.0f}s"
        })
    
    # Create table
    table_data = []
    headers = ['Condition', 'Trial Count', 'First Onset', 'Last Onset', 'Duration']
    for row in condition_data:
        table_data.append([row[h] for h in headers])
    
    table = ax_details.table(cellText=table_data, colLabels=headers,
                           cellLoc='center', loc='center',
                           bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Color the header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax_details.set_title('Condition Details', fontsize=12, fontweight='bold', pad=20)
    
    # Panel 2: Contrast weights
    ax_weights = fig.add_subplot(gs[2, :])
    ax_weights.axis('off')
    
    # Show contrast weights as a matrix
    contrast_weights = np.zeros((len(df_contrasts), n_conditions))
    contrast_names = []
    
    for i, (_, contrast) in enumerate(df_contrasts.iterrows()):
        contrast_names.append(contrast['contrast_name'])
        if contrast['condition1'] in unique_conditions:
            idx = unique_conditions.index(contrast['condition1'])
            contrast_weights[i, idx] = contrast['weight1']
    
    # Create heatmap of contrast weights
    im2 = ax_weights.imshow(contrast_weights, cmap='RdBu_r', aspect='auto', 
                           vmin=-1, vmax=1, interpolation='nearest')
    
    # Set labels
    ax_weights.set_xticks(range(n_conditions))
    ax_weights.set_xticklabels(unique_conditions, rotation=45, ha='right')
    ax_weights.set_yticks(range(len(contrast_names)))
    ax_weights.set_yticklabels([f"C{i+1}" for i in range(len(contrast_names))])
    ax_weights.set_xlabel('Regressors', fontsize=10)
    ax_weights.set_ylabel('Contrasts', fontsize=10)
    ax_weights.set_title('Contrast Weights Matrix', fontsize=12, fontweight='bold')
    
    # Add colorbar
    cbar2 = plt.colorbar(im2, ax=ax_weights, shrink=0.8)
    cbar2.set_label('Weight', fontsize=10)
    
    # Panel 3: Trial timeline
    ax_timeline = fig.add_subplot(gs[3, :])
    
    # Create timeline showing trial types
    colors = plt.cm.Set3(np.linspace(0, 1, n_conditions))
    condition_colors = dict(zip(unique_conditions, colors))
    
    for i, (_, trial) in enumerate(df_conditions.iterrows()):
        condition = trial['conditions']
        onset = trial['onset']
        duration = trial['duration']
        color = condition_colors[condition]
        
        ax_timeline.barh(0, duration, left=onset, height=0.8, 
                        color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    ax_timeline.set_xlabel('Time (seconds)', fontsize=10)
    ax_timeline.set_ylabel('Trials', fontsize=10)
    ax_timeline.set_title('Trial Timeline', fontsize=12, fontweight='bold')
    ax_timeline.set_ylim(-0.5, 0.5)
    ax_timeline.set_yticks([])
    
    # Add legend
    legend_elements = [patches.Patch(color=color, label=condition) 
                      for condition, color in condition_colors.items()]
    ax_timeline.legend(handles=legend_elements, loc='upper right', 
                      bbox_to_anchor=(1, 1), fontsize=8)
    
    plt.suptitle('NARSAD fMRI Design Matrix and Contrasts', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('narsad_design_matrix_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Design matrix visualization saved as 'narsad_design_matrix_visualization.png'")
    print(f"Total conditions: {n_conditions}")
    print(f"Total trials: {len(df_conditions)}")
    print(f"Total contrasts: {len(df_contrasts)}")

if __name__ == "__main__":
    create_design_matrix_visualization()
