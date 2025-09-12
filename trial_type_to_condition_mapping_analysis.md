# Trial Type to Condition Mapping Analysis

## Overview
This document provides a detailed analysis of how the NARSAD fMRI analysis pipeline transforms `trial_type` values from the input events file into `condition` values used in the FSL GLM model, with special handling for first-trial separation.

## Complete Data Flow: Input → Output

### 1. **INPUT: Events File (CSV)**
```
File: task-Narsad_phase2_events.csv or task-Narsad_phase3_events.csv
Columns: trial_type, onset, duration, [other columns]
Example data:
trial_type    onset    duration
CS-          2.0      6.0
CSS          8.0      6.0  
CSR          14.0     6.0
CS-          20.0     6.0
FIXATION     26.0     2.0
```

### 2. **STEP 1: Data Loading (`create_1st_voxelWise.py`)**
**Function:** `get_condition_names_from_events(events_file)`
**Location:** Lines 138-214 in `create_1st_voxelWise.py`

```python
# Load events file with automatic separator detection
from utils import read_csv_with_detection
events_df = read_csv_with_detection(events_file)
df_trial_info = events_df.copy()
```

**What happens:**
- Uses `read_csv_with_detection()` to handle both comma and tab-separated files
- Creates `df_trial_info` DataFrame with columns: `trial_type`, `onset`, `duration`

### 3. **STEP 2: Condition Processing (`first_level_workflows.py`)**
**Function:** `extract_cs_conditions(df_trial_info)`
**Location:** Lines 29-123 in `first_level_workflows.py`

This is the **CORE MAPPING FUNCTION** that transforms trial_type → condition:

#### **3.1 Initialization**
```python
# Create working copy
df_work = df_trial_info.copy()

# Initialize conditions column with trial_type values
df_work['conditions'] = df_work['trial_type'].copy()
```

**At this point:** `conditions` column = `trial_type` column (exact copy)

#### **3.2 CS- Trial Separation**
```python
# Find CS- trials (excluding CSS and CSR)
cs_trials = df_work[df_work['trial_type'].str.startswith('CS-') & 
                   ~df_work['trial_type'].str.startswith('CSS') & 
                   ~df_work['trial_type'].str.startswith('CSR')].copy()

# Sort by onset time and identify first trial
if not cs_trials.empty:
    cs_first_idx = cs_trials.sort_values('onset').index[0]
    df_work.loc[cs_first_idx, 'conditions'] = 'CS-_first'
    cs_other_indices = cs_trials[cs_trials.index != cs_first_idx].index
    df_work.loc[cs_other_indices, 'conditions'] = 'CS-_others'
```

**Mapping Logic:**
- **First CS- trial (by onset time)** → `'CS-_first'`
- **All other CS- trials** → `'CS-_others'`

#### **3.3 CSS Trial Separation**
```python
# Find CSS trials
css_trials = df_work[df_work['trial_type'].str.startswith('CSS')].copy()

if not css_trials.empty:
    css_first_idx = css_trials.sort_values('onset').index[0]
    df_work.loc[css_first_idx, 'conditions'] = 'CSS_first'
    css_other_indices = css_trials[css_trials.index != css_first_idx].index
    df_work.loc[css_other_indices, 'conditions'] = 'CSS_others'
```

**Mapping Logic:**
- **First CSS trial (by onset time)** → `'CSS_first'`
- **All other CSS trials** → `'CSS_others'`

#### **3.4 CSR Trial Separation**
```python
# Find CSR trials
csr_trials = df_work[df_work['trial_type'].str.startswith('CSR')].copy()

if not csr_trials.empty:
    csr_first_idx = csr_trials.sort_values('onset').index[0]
    df_work.loc[csr_first_idx, 'conditions'] = 'CSR_first'
    csr_other_indices = csr_trials[csr_trials.index != cs_first_idx].index
    df_work.loc[csr_other_indices, 'conditions'] = 'CSR_others'
```

**Mapping Logic:**
- **First CSR trial (by onset time)** → `'CSR_first'`
- **All other CSR trials** → `'CSR_others'`

#### **3.5 Other Trials (Unchanged)**
```python
# All other trial types keep their original trial_type as condition
# (FIXATION, etc.)
```

**Mapping Logic:**
- **FIXATION** → `'FIXATION'` (unchanged)
- **Any other trial_type** → same value (unchanged)

### 4. **STEP 3: FSL Integration (`utils.py`)**
**Function:** `_bids2nipypeinfo_from_df()`
**Location:** Lines 26-131 in `utils.py`

#### **4.1 Input Validation**
```python
# Validate processed DataFrame
if 'conditions' not in df_conditions.columns:
    raise ValueError("DataFrame must have 'conditions' column from extract_cs_conditions()")
```

#### **4.2 Condition Extraction**
```python
# Get unique conditions from processed DataFrame
conditions = sorted(df_conditions['conditions'].unique().tolist())
```

**Result:** List of unique condition names: `['CS-_first', 'CS-_others', 'CSS_first', 'CSS_others', 'CSR_first', 'CSR_others', 'FIXATION']`

#### **4.3 Trial Grouping by Condition**
```python
# Process each condition
for condition in runinfo.conditions:
    # Get all trials for this condition
    condition_trials = df_conditions[df_conditions['conditions'] == condition]
    
    if len(condition_trials) > 0:
        # Extract onsets, durations, and amplitudes
        onsets = condition_trials['onset'].values
        durations = condition_trials['duration'].values
        
        runinfo.onsets.append(np.round(onsets, 3).tolist())
        runinfo.durations.append(np.round(durations, 3).tolist())
        runinfo.amplitudes.append([amplitude] * len(condition_trials))
```

### 5. **STEP 4: FSL Design Matrix Creation**
**Function:** `SpecifyModel` and `Level1Design` nodes
**Location:** Lines 196-208 in `first_level_workflows.py`

The processed conditions are used to create FSL design matrix columns:

```
Design Matrix Columns:
- CS-_first + temporal derivative
- CS-_others + temporal derivative  
- CSS_first + temporal derivative
- CSS_others + temporal derivative
- CSR_first + temporal derivative
- CSR_others + temporal derivative
- FIXATION + temporal derivative
- Motion parameters (6)
- Confounds (DVARS, FD, etc.)
- Constant term
```

### 6. **STEP 5: Contrast Generation**
**Function:** `get_condition_names_from_events()` (contrast section)
**Location:** Lines 174-212 in `create_1st_voxelWise.py`

```python
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
```

### 7. **OUTPUT: FSL GLM Results**
**Files Generated:**
- `cope1.nii.gz` to `cope9.nii.gz` (contrast estimates)
- `varcope1.nii.gz` to `varcope9.nii.gz` (variance estimates)
- `design.mat` (design matrix)
- `contrasts.con` (contrast definitions)

## Key Mapping Rules

### **Chronological Sorting**
- **Critical:** First trial identification is based on **onset time**, not trial order
- Uses `sort_values('onset')` to ensure chronological accuracy

### **String Matching Logic**
```python
# CS- trials (excluding CSS and CSR)
cs_trials = df_work[df_work['trial_type'].str.startswith('CS-') & 
                   ~df_work['trial_type'].str.startswith('CSS') & 
                   ~df_work['trial_type'].str.startswith('CSR')]

# CSS trials
css_trials = df_work[df_work['trial_type'].str.startswith('CSS')]

# CSR trials  
csr_trials = df_work[df_work['trial_type'].str.startswith('CSR')]
```

### **Index Preservation**
- Uses DataFrame `.index` to maintain trial identity
- Ensures each trial is mapped to exactly one condition

## Example Mapping

### **Input Events File:**
```
trial_type    onset    duration
CS-          2.0      6.0      → CS-_first
CSS          8.0      6.0      → CSS_first  
CSR          14.0     6.0      → CSR_first
CS-          20.0     6.0      → CS-_others
CSS          26.0     6.0      → CSS_others
CSR          32.0     6.0      → CSR_others
FIXATION     38.0     2.0      → FIXATION
```

### **Processed DataFrame:**
```
trial_type    onset    duration    conditions
CS-          2.0      6.0         CS-_first
CSS          8.0      6.0         CSS_first
CSR          14.0     6.0         CSR_first
CS-          20.0     6.0         CS-_others
CSS          26.0     6.0         CSS_others
CSR          32.0     6.0         CSR_others
FIXATION     38.0     2.0         FIXATION
```

### **FSL Design Matrix Columns:**
```
Column 1:  CS-_first + derivative
Column 2:  CS-_others + derivative
Column 3:  CSS_first + derivative
Column 4:  CSS_others + derivative
Column 5:  CSR_first + derivative
Column 6:  CSR_others + derivative
Column 7:  FIXATION + derivative
Column 8-13: Motion parameters
Column 14-23: Confounds
Column 24: Constant
```

## Critical Implementation Details

### **1. Data Flow Integrity**
- **Single Source of Truth:** `extract_cs_conditions()` is the only function that performs trial_type → condition mapping
- **Consistent Processing:** `_bids2nipypeinfo_from_df()` uses the processed DataFrame directly
- **No Redundant Processing:** Eliminates duplicate condition processing

### **2. Error Handling**
- **Validation:** Checks for required columns (`trial_type`, `onset`, `duration`)
- **Empty DataFrames:** Handles cases where no trials exist for a condition
- **Missing Conditions:** Gracefully handles missing trial types

### **3. Logging and Debugging**
```python
logger.info(f"CS- conditions: first trial at index {cs_first_idx}, {len(cs_other_indices)} others")
logger.info(f"Unique conditions for contrast generation: {unique_conditions}")
print(f"Condition '{condition}': {len(condition_trials)} trials at onsets {onsets.tolist()}")
```

### **4. Performance Considerations**
- **In-place Operations:** Uses `.loc[]` for efficient DataFrame updates
- **Vectorized Operations:** Uses pandas string methods for filtering
- **Memory Efficiency:** Creates working copy to avoid modifying original data

## Summary

The trial_type to condition mapping is a **two-stage process**:

1. **Stage 1:** `extract_cs_conditions()` transforms trial_type → condition with first-trial separation
2. **Stage 2:** `_bids2nipypeinfo_from_df()` converts processed conditions → FSL format

This architecture ensures **consistent processing** throughout the pipeline while maintaining **flexibility** for different trial types and **accuracy** in first-trial identification based on chronological order.
