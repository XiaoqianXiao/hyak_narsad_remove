#Nipype v1.10.0.
from nipype.pipeline import engine as pe
from nipype.algorithms.modelgen import SpecifyModel
from nipype.interfaces import fsl, utility as niu, io as nio
from niworkflows.interfaces.bids import DerivativesDataSink as BIDSDerivatives
from utils import _dict_ds
from utils import _dict_ds_lss
from utils import _bids2nipypeinfo
from utils import _bids2nipypeinfo_lss
from nipype.interfaces.fsl import SUSAN, ApplyMask, FLIRT, FILMGLS, Level1Design, FEATModel
import logging

# Author: Xiaoqian Xiao (xiao.xiaoqian.320@gmail.com)
# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class DerivativesDataSink(BIDSDerivatives):
    """Custom data sink for first-level analysis outputs."""
    out_path_base = 'firstLevel'

DATA_ITEMS = ['bold', 'mask', 'events', 'regressors', 'tr']
DATA_ITEMS_LSS = ['bold', 'mask', 'events', 'regressors', 'tr', 'trial_ID']

def extract_cs_conditions(df_trial_info):
    """
    Extract and group CS-, CSS, and CSR conditions from a pandas DataFrame.
    
    This function adds a 'conditions' column to the DataFrame that groups trials:
    - First trial of each CS type becomes 'CS-_first', 'CSS_first', 'CSR_first'
    - Remaining trials of each type become 'CS-_others', 'CSS_others', 'CSR_others'
    - All other trials keep their original trial_type as conditions value
    
    Args:
        df_trial_info (pandas.DataFrame): DataFrame with columns 'trial_type', 'onset', 'duration'.
                                        The 'trial_type' column contains condition names,
                                        and 'onset' column is used for chronological sorting.
    
    Returns:
        tuple: (df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions)
            - df_with_conditions: DataFrame with added 'conditions' column
            - cs_conditions: dict with 'first' and 'other' keys for CS- conditions
            - css_conditions: dict with 'first' and 'other' keys for CSS conditions  
            - csr_conditions: dict with 'first' and 'other' keys for CSR conditions
            - other_conditions: List of non-CS/CSS/CSR conditions
    """
    import pandas as pd
    
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


# =============================================================================
# CORE WORKFLOW FUNCTIONS
# =============================================================================

def first_level_wf(in_files, output_dir, condition_names=None, contrasts=None, 
                   fwhm=6.0, brightness_threshold=1000, high_pass_cutoff=100,
                   use_smoothing=True, use_derivatives=True, model_serial_correlations=True):
    """
    Generic first-level workflow for fMRI analysis.
    
    Args:
        in_files (dict): Input files dictionary
        output_dir (str): Output directory path
        condition_names (list): List of condition names (auto-detected if None)
        contrasts (list): List of contrast tuples (auto-generated if None)
        fwhm (float): Smoothing FWHM
        brightness_threshold (float): SUSAN brightness threshold
        high_pass_cutoff (float): High-pass filter cutoff
        use_smoothing (bool): Whether to apply smoothing
        use_derivatives (bool): Whether to use temporal derivatives
        model_serial_correlations (bool): Whether to model serial correlations
    
    Returns:
        pe.Workflow: Configured first-level workflow
    """
    if not in_files:
        raise ValueError("in_files cannot be empty")
    
    workflow = pe.Workflow(name='wf_1st_level')
    workflow.config['execution']['use_relative_paths'] = True
    workflow.config['execution']['remove_unnecessary_outputs'] = False

    # Data source
    datasource = pe.Node(niu.Function(function=_dict_ds, output_names=DATA_ITEMS),
                         name='datasource')
    datasource.inputs.in_dict = in_files
    datasource.iterables = ('sub', sorted(in_files.keys()))

    # Extract motion parameters from regressors file
    runinfo = pe.Node(niu.Function(
        input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names'],
        function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
        name='runinfo')

    # Set the column names to be used from the confounds file
    runinfo.inputs.regressors_names = ['dvars', 'framewise_displacement'] + \
                                      ['a_comp_cor_%02d' % i for i in range(6)] + \
                                      ['cosine%02d' % i for i in range(4)]

    # Mask
    apply_mask = pe.Node(ApplyMask(), name='apply_mask')
    
    # Optional smoothing
    if use_smoothing:
        susan = pe.Node(SUSAN(), name='susan')
        susan.inputs.fwhm = fwhm
        susan.inputs.brightness_threshold = brightness_threshold
        preproc_output = susan
    else:
        preproc_output = apply_mask

    # Model specification
    l1_spec = pe.Node(SpecifyModel(
        parameter_source='FSL',
        input_units='secs',
        high_pass_filter_cutoff=high_pass_cutoff
    ), name='l1_spec')


    # Level 1 model design
    l1_model = pe.Node(Level1Design(
        bases={'dgamma': {'derivs': use_derivatives}},
        model_serial_correlations=model_serial_correlations,
        contrasts=contrasts
    ), name='l1_model')

    # FEAT model specification
    feat_spec = pe.Node(FEATModel(), name='feat_spec')
    
    # FEAT fitting
    feat_fit = pe.Node(FILMGLS(smooth_autocorr=True, mask_size=5), name='feat_fit', mem_gb=12)
    
    # Select output files
    n_contrasts = len(contrasts)
    feat_select = pe.Node(nio.SelectFiles({
        **{f'cope{i}': f'cope{i}.nii.gz' for i in range(1, n_contrasts + 1)},
        **{f'varcope{i}': f'varcope{i}.nii.gz' for i in range(1, n_contrasts + 1)}
    }), name='feat_select')

    # Data sinks for copes and varcopes
    ds_copes = [
        pe.Node(DerivativesDataSink(
            base_directory=str(output_dir), keep_dtype=False, desc=f'cope{i}'),
            name=f'ds_cope{i}', run_without_submitting=True)
        for i in range(1, n_contrasts + 1)
    ]

    ds_varcopes = [
        pe.Node(DerivativesDataSink(
            base_directory=str(output_dir), keep_dtype=False, desc=f'varcope{i}'),
            name=f'ds_varcope{i}', run_without_submitting=True)
        for i in range(1, n_contrasts + 1)
    ]

    # Build workflow connections
    connections = _build_workflow_connections(
        datasource, apply_mask, runinfo, l1_spec, l1_model, 
        feat_spec, feat_fit, feat_select, preproc_output, use_smoothing
    )
    
    # Add data sink connections
    for i in range(1, n_contrasts + 1):
        connections.extend([
            (datasource, ds_copes[i - 1], [('bold', 'source_file')]),
            (datasource, ds_varcopes[i - 1], [('bold', 'source_file')]),
            (feat_select, ds_copes[i - 1], [(f'cope{i}', 'in_file')]),
            (feat_select, ds_varcopes[i - 1], [(f'varcope{i}', 'in_file')])
        ])

    workflow.connect(connections)
    return workflow

def _build_workflow_connections(datasource, apply_mask, runinfo, l1_spec, l1_model, 
                              feat_spec, feat_fit, feat_select, preproc_output, use_smoothing):
    """
    Build workflow connections based on smoothing configuration.
    
    Args:
        datasource: Data source node
        apply_mask: Mask application node
        runinfo: Run info node
        l1_spec: Level 1 specification node
        l1_model: Level 1 model node
        feat_spec: FEAT specification node
        feat_fit: FEAT fitting node
        feat_select: FEAT selection node
        preproc_output: Preprocessing output node
        use_smoothing: Whether smoothing is used
    
    Returns:
        list: List of workflow connections
    """
    connections = [
        (datasource, apply_mask, [('bold', 'in_file'), ('mask', 'mask_file')]),
        (datasource, runinfo, [('events', 'events_file'), ('regressors', 'regressors_file')]),
        (datasource, l1_spec, [('tr', 'time_repetition')]),
        (datasource, l1_model, [('tr', 'interscan_interval')]),
        (l1_spec, l1_model, [('session_info', 'session_info')]),
        (l1_model, feat_spec, [('fsf_files', 'fsf_file'), ('ev_files', 'ev_files')]),
        (feat_spec, feat_fit, [('design_file', 'design_file'), ('con_file', 'tcon_file')]),
        (feat_fit, feat_select, [('results_dir', 'base_directory')]),
    ]
    
    # Add smoothing connections if used
    if use_smoothing:
        connections.extend([
            (apply_mask, preproc_output, [('out_file', 'in_file')]),
            (preproc_output, l1_spec, [('smoothed_file', 'functional_runs')]),
            (preproc_output, runinfo, [('smoothed_file', 'in_file')]),
            (preproc_output, feat_fit, [('smoothed_file', 'in_file')])
        ])
    else:
        connections.extend([
            (apply_mask, l1_spec, [('out_file', 'functional_runs')]),
            (apply_mask, runinfo, [('out_file', 'in_file')]),
            (apply_mask, feat_fit, [('out_file', 'in_file')])
        ])
    
    # Add runinfo connections
    connections.extend([
        (runinfo, l1_spec, [('info', 'subject_info'), ('realign_file', 'realignment_parameters')])
    ])
    
    return connections


def create_interesting_contrasts(df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions):
    """
    Create a focused set of interesting contrasts for NARSAD analysis.
    
    Args:
        df_with_conditions (pandas.DataFrame): DataFrame with conditions column
        cs_conditions (dict): CS- condition information
        css_conditions (dict): CSS condition information  
        csr_conditions (dict): CSR condition information
        other_conditions (list): Other condition names
    
    Returns:
        list: List of contrast tuples
    """
    # Get all unique conditions that actually exist
    all_conditions = df_with_conditions['conditions'].unique().tolist()
    
    # Check which conditions actually have trials
    conditions_with_trials = {}
    for condition in all_conditions:
        trial_count = len(df_with_conditions[df_with_conditions['conditions'] == condition])
        conditions_with_trials[condition] = trial_count
        logger.info(f"Condition '{condition}': {trial_count} trials")
    
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
            
            # Check if both conditions exist AND have trials
            if (condition1 in all_conditions and condition2 in all_conditions and
                conditions_with_trials.get(condition1, 0) > 0 and conditions_with_trials.get(condition2, 0) > 0):
                contrast = (contrast_name, 'T', [condition1, condition2], [1, -1])
                contrasts.append(contrast)
                logger.info(f"Added contrast: {contrast_name} - {description}")
            else:
                missing_conditions = []
                if condition1 not in all_conditions or conditions_with_trials.get(condition1, 0) == 0:
                    missing_conditions.append(condition1)
                if condition2 not in all_conditions or conditions_with_trials.get(condition2, 0) == 0:
                    missing_conditions.append(condition2)
                logger.warning(f"Contrast {contrast_name}: conditions {missing_conditions} missing or have no trials")
        else:
            logger.warning(f"Invalid contrast format: {contrast_name}")
    
    logger.info(f"Created {len(contrasts)} interesting contrasts")
    return contrasts


def first_level_wf_LSS(in_files, output_dir, df_trial_info=None, contrast_type='interesting',
                      fwhm=6.0, brightness_threshold=1000, high_pass_cutoff=100,
                      use_smoothing=True, use_derivatives=True, model_serial_correlations=True):
    """
    First-level workflow with Least Squares Separate (LSS) approach.
    
    Args:
        in_files (dict): Input files dictionary
        output_dir (str): Output directory path
        df_trial_info (pandas.DataFrame): Trial information DataFrame
        contrast_type (str): Type of contrasts to generate ('interesting', 'standard', 'custom')
        fwhm (float): Smoothing FWHM
        brightness_threshold (float): SUSAN brightness threshold
        high_pass_cutoff (float): High-pass filter cutoff
        use_smoothing (bool): Whether to apply smoothing
        use_derivatives (bool): Whether to use temporal derivatives
        model_serial_correlations (bool): Whether to model serial correlations
    
    Returns:
        pe.Workflow: Configured LSS workflow
    """
    if not in_files:
        raise ValueError("in_files cannot be empty")
    
    if df_trial_info is None:
        raise ValueError("df_trial_info is required for LSS workflow")
    
    # Process trial information
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    # Generate contrasts based on type
    if contrast_type == 'interesting':
        contrasts = create_interesting_contrasts(df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions)
    else:
        # Default to standard contrasts if not interesting
        contrasts = create_standard_contrasts(df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions)
    
    # Get condition names
    condition_names = df_with_conditions['conditions'].unique().tolist()
    
    workflow = pe.Workflow(name='wf_1st_level_LSS')
    workflow.config['execution']['use_relative_paths'] = True
    workflow.config['execution']['remove_unnecessary_outputs'] = False

    # Data source
    datasource = pe.Node(niu.Function(function=_dict_ds_lss, output_names=DATA_ITEMS_LSS),
                         name='datasource')
    datasource.inputs.in_dict = in_files
    datasource.iterables = ('sub', sorted(in_files.keys()))

    # Extract motion parameters from regressors file
    runinfo = pe.Node(niu.Function(
        input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names'],
        function=_bids2nipypeinfo_lss, output_names=['info', 'realign_file']),
        name='runinfo')

    # Set the column names to be used from the confounds file
    runinfo.inputs.regressors_names = ['dvars', 'framewise_displacement'] + \
                                      ['a_comp_cor_%02d' % i for i in range(6)] + \
                                      ['cosine%02d' % i for i in range(4)]

    # Mask
    apply_mask = pe.Node(ApplyMask(), name='apply_mask')
    
    # Optional smoothing
    if use_smoothing:
        susan = pe.Node(SUSAN(), name='susan')
        susan.inputs.fwhm = fwhm
        susan.inputs.brightness_threshold = brightness_threshold
        preproc_output = susan
    else:
        preproc_output = apply_mask

    # Model specification
    l1_spec = pe.Node(SpecifyModel(
        parameter_source='FSL',
        input_units='secs',
        high_pass_filter_cutoff=high_pass_cutoff
    ), name='l1_spec')

    # Level 1 model design
    l1_model = pe.Node(Level1Design(
        bases={'dgamma': {'derivs': use_derivatives}},
        model_serial_correlations=model_serial_correlations,
        contrasts=contrasts
    ), name='l1_model')

    # FEAT model specification
    feat_spec = pe.Node(FEATModel(), name='feat_spec')
    
    # FEAT fitting
    feat_fit = pe.Node(FILMGLS(smooth_autocorr=True, mask_size=5), name='feat_fit', mem_gb=12)
    
    # Select output files
    n_contrasts = len(contrasts)
    feat_select = pe.Node(nio.SelectFiles({
        **{f'cope{i}': f'cope{i}.nii.gz' for i in range(1, n_contrasts + 1)},
        **{f'varcope{i}': f'varcope{i}.nii.gz' for i in range(1, n_contrasts + 1)}
    }), name='feat_select')

    # Data sinks for copes and varcopes
    ds_copes = [
        pe.Node(DerivativesDataSink(
            base_directory=str(output_dir), keep_dtype=False, desc=f'cope{i}'),
            name=f'ds_cope{i}', run_without_submitting=True)
        for i in range(1, n_contrasts + 1)
    ]

    ds_varcopes = [
        pe.Node(DerivativesDataSink(
            base_directory=str(output_dir), keep_dtype=False, desc=f'varcope{i}'),
            name=f'ds_varcope{i}', run_without_submitting=True)
        for i in range(1, n_contrasts + 1)
    ]

    # Build workflow connections
    connections = _build_workflow_connections(
        datasource, apply_mask, runinfo, l1_spec, l1_model, 
        feat_spec, feat_fit, feat_select, preproc_output, use_smoothing
    )
    
    # Add data sink connections
    for i in range(1, n_contrasts + 1):
        connections.extend([
            (datasource, ds_copes[i - 1], [('bold', 'source_file')]),
            (datasource, ds_varcopes[i - 1], [('bold', 'source_file')]),
            (feat_select, ds_copes[i - 1], [(f'cope{i}', 'in_file')]),
            (feat_select, ds_varcopes[i - 1], [(f'varcope{i}', 'in_file')])
        ])

    workflow.connect(connections)
    return workflow


def first_level_wf_voxelwise(in_files, output_dir, df_trial_info=None, contrast_type='interesting',
                           fwhm=6.0, brightness_threshold=1000, high_pass_cutoff=100,
                           use_smoothing=True, use_derivatives=True, model_serial_correlations=True):
    """
    First-level voxel-wise workflow with trial processing.
    
    Args:
        in_files (dict): Input files dictionary
        output_dir (str): Output directory path
        df_trial_info (pandas.DataFrame): Trial information DataFrame
        contrast_type (str): Type of contrasts to generate ('interesting', 'standard', 'custom')
        fwhm (float): Smoothing FWHM
        brightness_threshold (float): SUSAN brightness threshold
        high_pass_cutoff (float): High-pass filter cutoff
        use_smoothing (bool): Whether to apply smoothing
        use_derivatives (bool): Whether to use temporal derivatives
        model_serial_correlations (bool): Whether to model serial correlations
    
    Returns:
        pe.Workflow: Configured voxel-wise workflow
    """
    if not in_files:
        raise ValueError("in_files cannot be empty")
    
    if df_trial_info is None:
        raise ValueError("df_trial_info is required for voxel-wise workflow")
    
    # Process trial information
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    # Generate contrasts based on type
    if contrast_type == 'interesting':
        contrasts = create_interesting_contrasts(df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions)
    else:
        # Default to standard contrasts if not interesting
        contrasts = create_standard_contrasts(df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions)
    
    # Get condition names
    condition_names = df_with_conditions['conditions'].unique().tolist()
    
    # Helper function to process events for conditions
    def process_events_for_conditions(df_with_conditions, events_file):
        """
        Process events file to create FSL-compatible format with conditions.
        
        Args:
            df_with_conditions (pandas.DataFrame): DataFrame with conditions column
            events_file (str): Path to original events file
        
        Returns:
            str: Path to processed events file
        """
        import pandas as pd
        import tempfile
        import os
        
        # Create a copy of the dataframe with the conditions column
        processed_df = df_with_conditions[['onset', 'duration', 'conditions']].copy()
        
        # Rename conditions to trial_type for FSL compatibility
        processed_df = processed_df.rename(columns={'conditions': 'trial_type'})
        
        # Create temporary file for processed events
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', prefix='processed_events_')
        os.close(temp_fd)
        
        # Write processed events to temporary file
        processed_df.to_csv(temp_path, index=False, sep='\t')
        
        logger.info(f"Processed events file created: {temp_path}")
        logger.info(f"Processed events shape: {processed_df.shape}")
        logger.info(f"Unique trial types: {processed_df['trial_type'].unique()}")
        
        return temp_path
    
    workflow = pe.Workflow(name='wf_1st_level_voxelwise')
    workflow.config['execution']['use_relative_paths'] = True
    workflow.config['execution']['remove_unnecessary_outputs'] = False

    # Data source
    datasource = pe.Node(niu.Function(function=_dict_ds, output_names=DATA_ITEMS),
                         name='datasource')
    datasource.inputs.in_dict = in_files
    datasource.iterables = ('sub', sorted(in_files.keys()))

    # Process events for conditions
    process_events = pe.Node(niu.Function(
        input_names=['df_with_conditions', 'events_file'],
        output_names=['processed_events_file'],
        function=process_events_for_conditions),
        name='process_events')
    process_events.inputs.df_with_conditions = df_with_conditions

    # Extract motion parameters from regressors file
    runinfo = pe.Node(niu.Function(
        input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names'],
        function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
        name='runinfo')

    # Set the column names to be used from the confounds file
    runinfo.inputs.regressors_names = ['dvars', 'framewise_displacement'] + \
                                      ['a_comp_cor_%02d' % i for i in range(6)] + \
                                      ['cosine%02d' % i for i in range(4)]

    # Mask
    apply_mask = pe.Node(ApplyMask(), name='apply_mask')
    
    # Optional smoothing
    if use_smoothing:
        susan = pe.Node(SUSAN(), name='susan')
        susan.inputs.fwhm = fwhm
        susan.inputs.brightness_threshold = brightness_threshold
        preproc_output = susan
    else:
        preproc_output = apply_mask

    # Model specification
    l1_spec = pe.Node(SpecifyModel(
        parameter_source='FSL',
        input_units='secs',
        high_pass_filter_cutoff=high_pass_cutoff
    ), name='l1_spec')

    # Level 1 model design
    l1_model = pe.Node(Level1Design(
        bases={'dgamma': {'derivs': use_derivatives}},
        model_serial_correlations=model_serial_correlations,
        contrasts=contrasts
    ), name='l1_model')

    # FEAT model specification
    feat_spec = pe.Node(FEATModel(), name='feat_spec')
    
    # FEAT fitting
    feat_fit = pe.Node(FILMGLS(smooth_autocorr=True, mask_size=5), name='feat_fit', mem_gb=12)
    
    # Select output files
    n_contrasts = len(contrasts)
    feat_select = pe.Node(nio.SelectFiles({
        **{f'cope{i}': f'cope{i}.nii.gz' for i in range(1, n_contrasts + 1)},
        **{f'varcope{i}': f'varcope{i}.nii.gz' for i in range(1, n_contrasts + 1)}
    }), name='feat_select')

    # Data sinks for copes and varcopes
    ds_copes = [
        pe.Node(DerivativesDataSink(
            base_directory=str(output_dir), keep_dtype=False, desc=f'cope{i}'),
            name=f'ds_cope{i}', run_without_submitting=True)
        for i in range(1, n_contrasts + 1)
    ]

    ds_varcopes = [
        pe.Node(DerivativesDataSink(
            base_directory=str(output_dir), keep_dtype=False, desc=f'varcope{i}'),
            name=f'ds_varcope{i}', run_without_submitting=True)
        for i in range(1, n_contrasts + 1)
    ]

    # Build workflow connections
    connections = _build_workflow_connections(
        datasource, apply_mask, runinfo, l1_spec, l1_model, 
        feat_spec, feat_fit, feat_select, preproc_output, use_smoothing
    )
    
    # Add process_events connections
    connections.extend([
        (datasource, process_events, [('events', 'events_file')]),
        (process_events, runinfo, [('processed_events_file', 'events_file')])
    ])
    
    # Add data sink connections
    for i in range(1, n_contrasts + 1):
        connections.extend([
            (datasource, ds_copes[i - 1], [('bold', 'source_file')]),
            (datasource, ds_varcopes[i - 1], [('bold', 'source_file')]),
            (feat_select, ds_copes[i - 1], [(f'cope{i}', 'in_file')]),
            (feat_select, ds_varcopes[i - 1], [(f'varcope{i}', 'in_file')])
        ])

    workflow.connect(connections)
    return workflow


def create_standard_contrasts(df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions):
    """
    Create standard contrasts for NARSAD analysis.
    
    Args:
        df_with_conditions (pandas.DataFrame): DataFrame with conditions column
        cs_conditions (dict): CS- condition information
        css_conditions (dict): CSS condition information  
        csr_conditions (dict): CSR condition information
        other_conditions (list): Other condition names
    
    Returns:
        list: List of contrast tuples
    """
    # Get all unique conditions that actually exist
    all_conditions = df_with_conditions['conditions'].unique().tolist()
    
    # Check which conditions actually have trials
    conditions_with_trials = {}
    for condition in all_conditions:
        trial_count = len(df_with_conditions[df_with_conditions['conditions'] == condition])
        conditions_with_trials[condition] = trial_count
        logger.info(f"Condition '{condition}': {trial_count} trials")
    
    contrasts = []
    
    # Add contrasts for conditions that have trials
    for condition in all_conditions:
        if conditions_with_trials.get(condition, 0) > 0:
            contrast = (f"{condition} > FIXATION", 'T', [condition, 'FIXATION'], [1, -1])
            contrasts.append(contrast)
            logger.info(f"Added standard contrast: {condition} > FIXATION")
    
    logger.info(f"Created {len(contrasts)} standard contrasts")
    return contrasts