# Events Processing Flow Analysis: extract_cs_conditions() → _bids2nipypeinfo()

## 🔍 **Current Issue Identified**

**The output of `extract_cs_conditions()` is NOT directly passed to `_bids2nipypeinfo()`!**

There's a **disconnect** in the current pipeline where:
1. `extract_cs_conditions()` processes the DataFrame and creates condition mappings
2. But `_bids2nipypeinfo()` reads the **original events file directly**, not the processed DataFrame

## 📍 **Where the Code Currently Is**

### **1. extract_cs_conditions() Usage**
**Location**: `create_1st_voxelWise.py` lines 161, 378

```python
# Line 161 in get_condition_names_from_events()
df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)

# Line 378 in run_subject_workflow()
contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions, condition_names = get_condition_names_from_events(events_file)
```

**What it does**: 
- Processes the events DataFrame
- Creates condition mappings (CS-_first, CS-_others, etc.)
- Returns processed DataFrame with 'conditions' column

### **2. _bids2nipypeinfo() Usage**
**Location**: `first_level_workflows.py` lines 164-167, 269

```python
# Lines 164-167: Node definition
runinfo = pe.Node(niu.Function(
    input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names'],
    function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
    name='runinfo')

# Line 269: Connection
(datasource, runinfo, [('events', 'events_file'), ('regressors', 'regressors_file')])
```

**What it does**:
- Reads the **original events file** directly from disk
- Processes it using its own logic (lines 81-96 in utils.py)
- Creates FSL-compatible format

## 🚨 **The Problem**

### **Two Separate Processing Paths**

#### **Path 1: extract_cs_conditions() Processing**
```
Events CSV → read_csv_with_detection() → extract_cs_conditions() → Processed DataFrame
```
- Creates: CS-_first, CS-_others, CSS_first, CSS_others, CSR_first, CSR_others
- Used for: Contrast generation in `get_condition_names_from_events()`

#### **Path 2: _bids2nipypeinfo() Processing**
```
Events CSV → read_csv_with_detection() → _bids2nipypeinfo() → FSL Bunch
```
- Creates: CS-_first, CS-_others (but using different logic in utils.py lines 81-96)
- Used for: FSL workflow execution

### **The Disconnect**
1. `extract_cs_conditions()` processes the DataFrame and creates condition mappings
2. `_bids2nipypeinfo()` **ignores this processing** and reads the original events file
3. Both functions implement **similar logic independently**
4. The processed DataFrame from `extract_cs_conditions()` is **never used** by `_bids2nipypeinfo()`

## 🔧 **How to Fix This**

### **Option 1: Pass Processed DataFrame to Workflow**
Modify the workflow to accept the processed DataFrame:

```python
# In first_level_workflows.py
def first_level_wf(in_files, output_dir, df_trial_info=None, contrasts=None, ...):
    # Create a custom function that uses the processed DataFrame
    def process_events_with_df(in_file, df_trial_info, regressors_file, regressors_names):
        # Use the pre-processed DataFrame instead of reading events file
        return _bids2nipypeinfo_from_df(in_file, df_trial_info, regressors_file, regressors_names)
    
    runinfo = pe.Node(niu.Function(
        input_names=['in_file', 'df_trial_info', 'regressors_file', 'regressors_names'],
        function=process_events_with_df, output_names=['info', 'realign_file']),
        name='runinfo')
```

### **Option 2: Modify _bids2nipypeinfo() to Accept DataFrame**
Create a new function that accepts the processed DataFrame:

```python
# In utils.py
def _bids2nipypeinfo_from_df(in_file, df_trial_info, regressors_file, regressors_names):
    """Version of _bids2nipypeinfo that uses pre-processed DataFrame."""
    # Use df_trial_info['conditions'] column instead of processing events file
    conditions = df_trial_info['conditions'].unique().tolist()
    
    # Rest of the logic using the processed conditions...
```

### **Option 3: Save Processed DataFrame to File**
Save the processed DataFrame and modify the workflow to use it:

```python
# In create_1st_voxelWise.py
def get_condition_names_from_events(events_file):
    # ... existing code ...
    df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
    
    # Save processed DataFrame
    processed_events_file = events_file.replace('.csv', '_processed.csv')
    df_with_conditions.to_csv(processed_events_file, index=False)
    
    # Return the processed file path instead of original
    return contrasts, cs_conditions, css_conditions, csr_conditions, other_conditions, condition_names, processed_events_file
```

## 📊 **Current Data Flow**

```
Events CSV
    ↓
┌─────────────────────────────────────┐
│ create_1st_voxelWise.py            │
│ get_condition_names_from_events()   │
│                                     │
│ 1. read_csv_with_detection()       │
│ 2. extract_cs_conditions()         │
│ 3. Create contrasts                │
│ 4. Return condition_names          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ first_level_wf()                   │
│                                     │
│ 1. Pass events_file to workflow    │
│ 2. Workflow calls _bids2nipypeinfo │
│ 3. _bids2nipypeinfo reads ORIGINAL │
│    events file (ignores processing) │
└─────────────────────────────────────┘
```

## 🎯 **Recommended Solution**

**Option 2** is the cleanest approach:

1. Create `_bids2nipypeinfo_from_df()` in utils.py
2. Modify the workflow to accept the processed DataFrame
3. Pass the processed DataFrame from `create_1st_voxelWise.py` to the workflow
4. Ensure consistent processing logic between both paths

This would ensure that:
- The same condition mapping logic is used throughout
- No duplicate processing occurs
- The processed DataFrame from `extract_cs_conditions()` is actually utilized
- The pipeline is more efficient and consistent

## 🔍 **Summary**

**Current State**: `extract_cs_conditions()` and `_bids2nipypeinfo()` run independently with similar but separate logic.

**Issue**: The processed DataFrame from `extract_cs_conditions()` is not passed to `_bids2nipypeinfo()`.

**Solution Needed**: Modify the workflow to use the processed DataFrame instead of re-reading the original events file.
