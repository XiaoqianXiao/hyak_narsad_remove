# Trial-to-Condition Mapping: Code Analysis

## Overview
This document provides a detailed analysis of exactly where and how the code maps trials to conditions in the NARSAD fMRI analysis pipeline.

## 1. Primary Mapping Functions

### A. `extract_cs_conditions()` in `first_level_workflows.py` (Lines 28-122)

**Location**: `/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove/first_level_workflows.py`

**Purpose**: This is the **main function** that processes trial data and creates the condition mapping.

#### **Step-by-Step Mapping Process:**

```python
# 1. Initialize conditions column (Line 68)
df_work['conditions'] = df_work['trial_type'].copy()

# 2. Identify CS- trials (Lines 74-76)
cs_trials = df_work[df_work['trial_type'].str.startswith('CS-') & 
                   ~df_work['trial_type'].str.startswith('CSS') & 
                   ~df_work['trial_type'].str.startswith('CSR')].copy()

# 3. Find first CS- trial by onset time (Line 82)
cs_first_idx = cs_trials.sort_values('onset').index[0]

# 4. Map first CS- trial to 'CS-_first' (Line 83)
df_work.loc[cs_first_idx, 'conditions'] = 'CS-_first'

# 5. Map remaining CS- trials to 'CS-_others' (Lines 84-85)
cs_other_indices = cs_trials[cs_trials.index != cs_first_idx].index
df_work.loc[cs_other_indices, 'conditions'] = 'CS-_others'
```

#### **Critical Logic:**
- **Sorting by onset**: `sort_values('onset')` ensures chronological ordering
- **Index-based mapping**: Uses DataFrame index to identify specific trials
- **String matching**: Uses `str.startswith()` to identify CS- vs CSS vs CSR
- **Exclusion logic**: `~df_work['trial_type'].str.startswith('CSS')` prevents CSS trials from being classified as CS-

### B. `_bids2nipypeinfo()` in `utils.py` (Lines 26-150)

**Location**: `/Users/xiaoqianxiao/PycharmProjects/hyak_narsad_remove/utils.py`

**Purpose**: Converts the processed conditions into FSL-compatible format.

#### **Key Mapping Logic:**

```python
# 1. Count CS- trials (Line 85)
cs_count = raw_conditions.count('CS-')

# 2. Create condition list with splitting (Lines 86-96)
if cs_count > 1:
    conditions = ['CS-_first', 'CS-_others']
    other_conditions = [c for c in set(raw_conditions) if c != 'CS-']
    conditions.extend(other_conditions)

# 3. Process each condition (Lines 103-146)
for condition in runinfo.conditions:
    if condition == 'CS-_first':
        # Get first CS- trial (Line 108)
        first_cs = cs_events.iloc[0:1]
        runinfo.onsets.append(np.round(first_cs.onset.values, 3).tolist())
        
    elif condition == 'CS-_others':
        # Get all CS- trials except first (Line 125)
        other_cs = cs_events.iloc[1:]
        runinfo.onsets.append(np.round(other_cs.onset.values, 3).tolist())
```

## 2. Data Flow Architecture

### **Input → Processing → Output Chain:**

```
1. Events CSV File
   ↓
2. extract_cs_conditions() [first_level_workflows.py]
   ↓
3. _bids2nipypeinfo() [utils.py]
   ↓
4. FSL Design Matrix
```

### **Detailed Data Transformation:**

#### **Step 1: Raw Events Data**
```csv
trial_type,onset,duration,amplitudes
CS-,0,1,1.0
CSS,2,1,1.0
CSR,4,1,1.0
FIXATION,6,1,1.0
CS-,8,1,1.0
CSS,10,1,1.0
```

#### **Step 2: After extract_cs_conditions()**
```python
# DataFrame with added 'conditions' column:
trial_type  onset  duration  conditions
CS-         0      1         CS-_first
CSS         2      1         CSS_first
CSR         4      1         CSR_first
FIXATION    6      1         FIXATION
CS-         8      1         CS-_others
CSS         10     1         CSS_others
```

#### **Step 3: After _bids2nipypeinfo()**
```python
# FSL Bunch object:
runinfo.conditions = ['CS-_first', 'CSS_first', 'CSR_first', 'FIXATION', 'CS-_others', 'CSS_others']
runinfo.onsets = [[0], [2], [4], [6], [8], [10]]
runinfo.durations = [[1], [1], [1], [1], [1], [1]]
```

## 3. Critical Mapping Decisions

### **A. Chronological Ordering**
```python
# Line 82 in first_level_workflows.py
cs_first_idx = cs_trials.sort_values('onset').index[0]
```
- **Why**: Ensures the "first" trial is truly the first chronologically
- **Method**: Sorts by onset time, takes index of first trial
- **Result**: Guarantees temporal accuracy

### **B. String Matching Logic**
```python
# Lines 74-76 in first_level_workflows.py
cs_trials = df_work[df_work['trial_type'].str.startswith('CS-') & 
                   ~df_work['trial_type'].str.startswith('CSS') & 
                   ~df_work['trial_type'].str.startswith('CSR')].copy()
```
- **Why**: Prevents CSS and CSR trials from being classified as CS-
- **Logic**: CSS and CSR also start with "CS-" but should be separate
- **Result**: Accurate condition identification

### **C. Index-Based Mapping**
```python
# Lines 83-85 in first_level_workflows.py
df_work.loc[cs_first_idx, 'conditions'] = 'CS-_first'
cs_other_indices = cs_trials[cs_trials.index != cs_first_idx].index
df_work.loc[cs_other_indices, 'conditions'] = 'CS-_others'
```
- **Why**: Preserves exact trial identity through DataFrame index
- **Method**: Uses `.loc[]` with specific indices
- **Result**: Maintains trial-to-condition traceability

## 4. Error Handling and Edge Cases

### **A. Empty DataFrames**
```python
# Lines 53-57 in first_level_workflows.py
if not isinstance(df_trial_info, pd.DataFrame):
    raise ValueError("df_trial_info must be a pandas DataFrame")
if df_trial_info.empty:
    raise ValueError("DataFrame cannot be empty")
```

### **B. Missing Columns**
```python
# Lines 59-62 in first_level_workflows.py
required_columns = ['trial_type', 'onset']
missing_columns = [col for col in required_columns if col not in df_trial_info.columns]
if missing_columns:
    raise ValueError(f"DataFrame missing required columns: {missing_columns}")
```

### **C. Single Trial Handling**
```python
# Lines 132-136 in utils.py
else:
    # Fallback if only 1 CS- trial
    runinfo.onsets.append([])
    runinfo.durations.append([])
    runinfo.amplitudes.append([])
```

## 5. Integration Points

### **A. Called from create_1st_voxelWise.py**
```python
# Line 161 in create_1st_voxelWise.py
df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
```

### **B. Used in workflow creation**
```python
# Lines 164-167 in first_level_workflows.py
runinfo = pe.Node(niu.Function(
    input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names'],
    function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
    name='runinfo')
```

## 6. Debugging and Logging

### **A. Comprehensive Logging**
```python
# Lines 70-71, 86, 94, 102, 106, 119-120 in first_level_workflows.py
logger.info(f"Using DataFrame input with {len(df_work)} trials")
logger.info(f"CS- conditions: first trial at index {cs_first_idx}, {len(cs_other_indices)} others")
logger.info(f"Unique conditions for contrast generation: {unique_conditions}")
```

### **B. Debug Output in utils.py**
```python
# Lines 40-42 in utils.py
print("=== DEBUG: loaded event columns ===")
print(events.columns.tolist())
print(events.head())
```

## 7. Key Advantages of This Mapping Approach

1. **Temporal Accuracy**: Sort by onset ensures chronological correctness
2. **Traceability**: Index-based mapping preserves trial identity
3. **Flexibility**: Handles variable numbers of trials per condition
4. **Robustness**: Comprehensive error handling and edge case management
5. **Transparency**: Extensive logging for debugging and verification
6. **FSL Compatibility**: Output format matches FSL requirements exactly

This mapping system ensures that every trial can be traced from the original events file through to its specific design matrix column, providing complete transparency in the analysis pipeline.
