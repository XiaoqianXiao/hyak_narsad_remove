# FSL GLM Modeling Analysis in NARSAD Pipeline

## Overview
This document explains how FSL models input data and builds GLM models within the `first_level_workflows.py` and `create_1st_voxelWise.py` scripts.

## FSL GLM Modeling Pipeline

### 1. Data Input Processing

#### **Input Files Structure:**
```
in_files = {
    'subject_id': {
        'bold': '/path/to/preprocessed_bold.nii.gz',    # Preprocessed BOLD data
        'mask': '/path/to/brain_mask.nii.gz',           # Brain mask
        'events': '/path/to/events.csv',                # Trial information
        'regressors': '/path/to/confounds.tsv',         # Motion/confound regressors
        'tr': 2.0                                       # Repetition time
    }
}
```

#### **Events File Processing (`utils._bids2nipypeinfo`):**
```python
# Events CSV Structure:
# trial_type,onset,duration,amplitudes
# CS-,0,1,1.0
# CSS,2,1,1.0
# CSR,4,1,1.0
# FIXATION,6,1,1.0

# Processed into FSL-compatible format:
conditions = ['CS-_first', 'CS-_others', 'CSS_first', 'CSS_others', 'CSR_first', 'CSR_others', 'FIXATION']
onsets = [[0], [8], [2], [10], [4], [12], [6, 14]]
durations = [[1], [1], [1], [1], [1], [1], [1, 1]]
amplitudes = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0], [1.0, 1.0]]
```

### 2. FSL Workflow Components

#### **A. SpecifyModel Node**
```python
l1_spec = pe.Node(SpecifyModel(
    parameter_source='FSL',                    # Use FSL parameter conventions
    input_units='secs',                       # Input time units
    high_pass_filter_cutoff=high_pass_cutoff  # High-pass filter (default: 100s)
), name='l1_spec')
```

**Purpose:** Creates session information for FSL's GLM
- Converts events into FSL-compatible format
- Applies high-pass filtering
- Handles temporal derivatives

#### **B. Level1Design Node**
```python
l1_model = pe.Node(Level1Design(
    bases={'dgamma': {'derivs': use_derivatives}},  # HRF basis functions
    model_serial_correlations=model_serial_correlations,  # Prewhitening
    contrasts=contrasts                              # Statistical contrasts
), name='l1_model')
```

**Purpose:** Creates FSL design matrix and contrast files
- Generates `.fsf` (FEAT setup file)
- Creates `.ev` (event files) for each condition
- Defines statistical contrasts

#### **C. FEATModel Node**
```python
feat_spec = pe.Node(FEATModel(), name='feat_spec')
```

**Purpose:** Converts design specification to FSL design matrix
- Reads `.fsf` and `.ev` files
- Creates design matrix (`.mat` file)
- Generates contrast files (`.con` and `.fts` files)

#### **D. FILMGLS Node**
```python
feat_fit = pe.Node(FILMGLS(
    smooth_autocorr=True,  # Smooth autocorrelation estimates
    mask_size=5           # Mask size for autocorrelation
), name='feat_fit', mem_gb=12)
```

**Purpose:** Fits GLM using FSL's FILM (FMRIB's Improved Linear Model)
- Performs prewhitening
- Estimates parameters and contrasts
- Generates COPE (contrast of parameter estimates) and VARCOPE files

### 3. GLM Model Specification

#### **Design Matrix Structure:**
```
Design Matrix Columns:
├── CS-_first        (regressor 1)
├── CS-_first_deriv  (temporal derivative)
├── CS-_others       (regressor 2)  
├── CS-_others_deriv (temporal derivative)
├── CSS_first        (regressor 3)
├── CSS_first_deriv  (temporal derivative)
├── CSS_others       (regressor 4)
├── CSS_others_deriv (temporal derivative)
├── CSR_first        (regressor 5)
├── CSR_first_deriv  (temporal derivative)
├── CSR_others       (regressor 6)
├── CSR_others_deriv (temporal derivative)
├── FIXATION         (regressor 7)
├── FIXATION_deriv   (temporal derivative)
├── Motion params    (6 regressors: trans_x, trans_y, trans_z, rot_x, rot_y, rot_z)
├── Confound params  (DVARS, FD, aCompCor, cosine regressors)
└── Constant term    (intercept)
```

#### **Basis Functions:**
- **Canonical HRF:** Double gamma function
- **Temporal Derivatives:** Capture timing variations
- **Duration:** Event duration (typically 1 TR)

### 4. Statistical Contrasts

#### **Interesting Contrasts Generated:**
```python
contrasts = [
    ("CS-_others > FIXATION", "T", ["CS-_others", "FIXATION"], [1, -1]),
    ("CSS_others > FIXATION", "T", ["CSS_others", "FIXATION"], [1, -1]),
    ("CSR_others > FIXATION", "T", ["CSR_others", "FIXATION"], [1, -1]),
    ("CSS_others > CSR_others", "T", ["CSS_others", "CSR_others"], [1, -1]),
    ("CSR_others > CSS_others", "T", ["CSR_others", "CSS_others"], [1, -1]),
    ("CSS_others > CS-_others", "T", ["CSS_others", "CS-_others"], [1, -1]),
    ("CSR_others > CS-_others", "T", ["CSR_others", "CS-_others"], [1, -1]),
    ("CS-_others > CSS_others", "T", ["CS-_others", "CSS_others"], [1, -1]),
    ("CS-_others > CSR_others", "T", ["CS-_others", "CSR_others"], [1, -1])
]
```

### 5. Workflow Execution Flow

```
1. Data Input
   ├── BOLD data (preprocessed)
   ├── Events file (trial info)
   ├── Confounds file (motion/artifacts)
   └── Brain mask

2. Preprocessing
   ├── Apply brain mask
   └── Optional smoothing (SUSAN)

3. Model Specification
   ├── SpecifyModel: Convert events to FSL format
   ├── Level1Design: Create design matrix
   └── FEATModel: Generate FSL design files

4. GLM Fitting
   ├── FILMGLS: Fit GLM with prewhitening
   ├── Estimate parameters (betas)
   └── Compute contrasts (COPEs)

5. Output
   ├── cope1.nii.gz, cope2.nii.gz, ... (contrast images)
   ├── varcope1.nii.gz, varcope2.nii.gz, ... (variance images)
   └── Design matrix and statistics files
```

### 6. Key FSL Features Used

#### **Prewhitening (FILM):**
- Models temporal autocorrelation
- Improves statistical efficiency
- Uses AR(1) model with smooth autocorrelation

#### **Temporal Derivatives:**
- Captures timing variations in HRF
- Improves model fit
- Reduces misspecification errors

#### **High-pass Filtering:**
- Removes low-frequency drift
- Default cutoff: 100 seconds
- Improves signal-to-noise ratio

#### **Motion Correction:**
- 6 motion parameters as regressors
- Reduces motion-related artifacts
- Includes temporal derivatives if needed

### 7. Memory and Performance

#### **Resource Requirements:**
- **FILMGLS:** 12GB RAM (large memory node)
- **Processing time:** ~30-60 minutes per subject
- **Output size:** ~100-200MB per subject

#### **Parallel Processing:**
- MultiProc plugin (4 CPUs)
- Subject-level parallelization
- Efficient memory management

This GLM modeling approach follows FSL best practices for first-level fMRI analysis, providing robust statistical inference for the NARSAD fear conditioning paradigm.
