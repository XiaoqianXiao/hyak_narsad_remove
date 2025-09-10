#!/usr/bin/env python3
"""
Comparison between first_level_wf and first_level_wf_voxelwise workflows
"""

def compare_workflows():
    """Compare the two workflow functions"""
    
    print("=" * 80)
    print("COMPARISON: first_level_wf vs first_level_wf_voxelwise")
    print("=" * 80)
    
    print("\n1. FUNCTION SIGNATURES")
    print("-" * 50)
    print("first_level_wf:")
    print("  def first_level_wf(in_files, output_dir, df_trial_info, ...)")
    print("  - Uses 'in_files' parameter")
    print("  - Generic first-level workflow")
    
    print("\nfirst_level_wf_voxelwise:")
    print("  def first_level_wf_voxelwise(inputs, output_dir, df_trial_info, ...)")
    print("  - Uses 'inputs' parameter")
    print("  - Specialized for voxel-wise analysis")
    
    print("\n2. DEFAULT PARAMETERS")
    print("-" * 50)
    
    print("first_level_wf:")
    print("  - fwhm=6.0")
    print("  - brightness_threshold=1000")
    print("  - high_pass_cutoff=100")
    print("  - use_smoothing=True")
    print("  - use_derivatives=True")
    print("  - model_serial_correlations=True")
    
    print("\nfirst_level_wf_voxelwise:")
    print("  - fwhm=6.0")
    print("  - brightness_threshold=0.1")
    print("  - high_pass_cutoff=128")
    print("  - use_smoothing=True")
    print("  - use_derivatives=True")
    print("  - model_serial_correlations=True")
    
    print("\n3. KEY DIFFERENCES")
    print("-" * 50)
    
    print("Parameter Name:")
    print("  first_level_wf:     'in_files'")
    print("  first_level_wf_voxelwise: 'inputs'")
    print("  → Different parameter names for input data")
    
    print("\nBrightness Threshold:")
    print("  first_level_wf:     1000 (high threshold)")
    print("  first_level_wf_voxelwise: 0.1 (low threshold)")
    print("  → Voxelwise uses much lower threshold for SUSAN smoothing")
    
    print("\nHigh-Pass Filter Cutoff:")
    print("  first_level_wf:     100 seconds")
    print("  first_level_wf_voxelwise: 128 seconds")
    print("  → Voxelwise uses longer cutoff (less aggressive filtering)")
    
    print("\nWorkflow Name:")
    print("  first_level_wf:     'wf_1st_level'")
    print("  first_level_wf_voxelwise: 'wf_1st_level_voxelwise'")
    print("  → Different workflow identifiers")
    
    print("\n4. PURPOSE AND USE CASES")
    print("-" * 50)
    
    print("first_level_wf:")
    print("  - Generic first-level fMRI analysis")
    print("  - Standard preprocessing parameters")
    print("  - Suitable for most standard analyses")
    print("  - Higher brightness threshold (more conservative smoothing)")
    print("  - Standard high-pass filtering")
    
    print("\nfirst_level_wf_voxelwise:")
    print("  - Specialized for voxel-wise analysis")
    print("  - Optimized parameters for fine-grained analysis")
    print("  - Lower brightness threshold (more aggressive smoothing)")
    print("  - Longer high-pass cutoff (preserves more low-frequency signal)")
    print("  - Designed for CS- condition handling")
    
    print("\n5. WHEN TO USE WHICH")
    print("-" * 50)
    
    print("Use first_level_wf when:")
    print("  - Standard first-level analysis")
    print("  - ROI-based analysis")
    print("  - Group-level analysis preparation")
    print("  - Standard preprocessing is sufficient")
    
    print("\nUse first_level_wf_voxelwise when:")
    print("  - Voxel-wise analysis")
    print("  - Fine-grained temporal analysis")
    print("  - CS- condition separation is important")
    print("  - More aggressive smoothing is needed")
    print("  - Preserving low-frequency signal is important")
    
    print("\n6. PARAMETER IMPLICATIONS")
    print("-" * 50)
    
    print("Brightness Threshold (SUSAN smoothing):")
    print("  - 1000 (first_level_wf): More conservative, preserves more detail")
    print("  - 0.1 (first_level_wf_voxelwise): More aggressive, smoother results")
    
    print("\nHigh-Pass Cutoff:")
    print("  - 100s (first_level_wf): Removes slower drifts")
    print("  - 128s (first_level_wf_voxelwise): Preserves more low-frequency signal")
    
    print("\n7. SUMMARY")
    print("-" * 50)
    print("first_level_wf: Generic, conservative preprocessing")
    print("first_level_wf_voxelwise: Specialized, optimized for voxel-wise analysis")

if __name__ == "__main__":
    compare_workflows()
