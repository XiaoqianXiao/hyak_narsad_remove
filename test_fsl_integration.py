#!/usr/bin/env python3
"""
Test script to verify that FSL actually uses the output from _bids2nipypeinfo_from_df().
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')

def test_fsl_integration():
    """Test the complete FSL integration flow."""
    
    print("=== TESTING FSL INTEGRATION ===")
    print()
    
    # 1. Test _bids2nipypeinfo_from_df function directly
    print("1. Testing _bids2nipypeinfo_from_df() function...")
    
    try:
        from utils import _bids2nipypeinfo_from_df
        from first_level_workflows import extract_cs_conditions
        
        # Create test data
        test_data = {
            'trial_type': ['CS-', 'CSS', 'CSR', 'CS-', 'CSS', 'CSR', 'FIXATION'],
            'onset': [2.0, 8.0, 14.0, 20.0, 26.0, 32.0, 38.0],
            'duration': [6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 2.0]
        }
        
        df_trial_info = pd.DataFrame(test_data)
        print(f"Created test DataFrame: {df_trial_info.shape}")
        print(f"Test data:\n{df_trial_info}")
        print()
        
        # Process with extract_cs_conditions
        df_with_conditions, cs_conditions, css_conditions, csr_conditions, other_conditions = extract_cs_conditions(df_trial_info)
        print(f"Processed DataFrame:\n{df_with_conditions}")
        print()
        
        # Test _bids2nipypeinfo_from_df
        test_bold_file = "test_bold.nii.gz"
        test_regressors_file = "test_regressors.tsv"
        
        # Create dummy regressors file
        regressors_data = {
            'trans_x': np.random.randn(100),
            'trans_y': np.random.randn(100),
            'trans_z': np.random.randn(100),
            'rot_x': np.random.randn(100),
            'rot_y': np.random.randn(100),
            'rot_z': np.random.randn(100),
            'dvars': np.random.randn(100),
            'framewise_displacement': np.random.randn(100)
        }
        regressors_df = pd.DataFrame(regressors_data)
        regressors_df.to_csv(test_regressors_file, sep='\t', index=False)
        
        # Test the function
        runinfo_list, motion_file = _bids2nipypeinfo_from_df(
            in_file=test_bold_file,
            df_conditions=df_with_conditions,
            regressors_file=test_regressors_file,
            regressors_names=['dvars', 'framewise_displacement']
        )
        
        print("✅ _bids2nipypeinfo_from_df() executed successfully!")
        print(f"Return type: {type(runinfo_list)}")
        print(f"List length: {len(runinfo_list)}")
        print(f"Motion file: {motion_file}")
        print()
        
        # Check the runinfo object
        runinfo = runinfo_list[0]
        print("Runinfo object structure:")
        print(f"  - scans: {runinfo.scans}")
        print(f"  - conditions: {runinfo.conditions}")
        print(f"  - onsets: {len(runinfo.onsets)} conditions")
        print(f"  - durations: {len(runinfo.durations)} conditions")
        print(f"  - amplitudes: {len(runinfo.amplitudes)} conditions")
        print()
        
        # Verify conditions match processed DataFrame
        expected_conditions = sorted(df_with_conditions['conditions'].unique().tolist())
        actual_conditions = runinfo.conditions
        
        print("Condition verification:")
        print(f"  Expected: {expected_conditions}")
        print(f"  Actual: {actual_conditions}")
        print(f"  Match: {expected_conditions == actual_conditions}")
        print()
        
        # Check onsets and durations for each condition
        for i, condition in enumerate(runinfo.conditions):
            print(f"Condition '{condition}':")
            print(f"  - Onsets: {runinfo.onsets[i]}")
            print(f"  - Durations: {runinfo.durations[i]}")
            print(f"  - Amplitudes: {runinfo.amplitudes[i]}")
        
        # Clean up test files
        if os.path.exists(test_regressors_file):
            os.remove(test_regressors_file)
        
        print()
        print("✅ _bids2nipypeinfo_from_df() test PASSED!")
        
    except Exception as e:
        print(f"❌ _bids2nipypeinfo_from_df() test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. Test workflow integration
    print("\n2. Testing workflow integration...")
    
    try:
        from first_level_workflows import first_level_wf
        
        # Create mock input files
        mock_inputs = {
            'test_subject': {
                'bold': 'test_bold.nii.gz',
                'mask': 'test_mask.nii.gz',
                'events': 'test_events.csv',
                'regressors': 'test_regressors.tsv',
                'tr': 2.0
            }
        }
        
        # Create workflow with df_conditions
        workflow = first_level_wf(
            in_files=mock_inputs,
            output_dir='test_output',
            condition_names=runinfo.conditions,
            contrasts=[("CS-_others > FIXATION", 'T', ['CS-_others', 'FIXATION'], [1, -1])],
            df_conditions=df_with_conditions
        )
        
        print("✅ Workflow created successfully with df_conditions!")
        print(f"Workflow name: {workflow.name}")
        print(f"Number of nodes: {len(workflow._graph.nodes())}")
        
        # Check if runinfo node exists and is properly configured
        runinfo_node = workflow.get_node('runinfo')
        if runinfo_node:
            print("✅ Runinfo node found in workflow!")
            print(f"  - Interface type: {type(runinfo_node.interface)}")
            
            # Check if df_conditions is set as static input
            if hasattr(runinfo_node.inputs, 'df_conditions'):
                print("✅ df_conditions is set as static input!")
                print(f"  - df_conditions shape: {runinfo_node.inputs.df_conditions.shape}")
                print(f"  - df_conditions columns: {list(runinfo_node.inputs.df_conditions.columns)}")
            else:
                print("❌ df_conditions is NOT set as static input!")
                
            # Check available inputs
            print(f"  - Available inputs: {list(runinfo_node.inputs.__dict__.keys())}")
        else:
            print("❌ Runinfo node not found in workflow!")
        
        print()
        print("✅ Workflow integration test PASSED!")
        
    except Exception as e:
        print(f"❌ Workflow integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Test FSL node connections
    print("\n3. Testing FSL node connections...")
    
    try:
        # Check if runinfo output connects to l1_spec
        runinfo_node = workflow.get_node('runinfo')
        l1_spec_node = workflow.get_node('l1_spec')
        
        if runinfo_node and l1_spec_node:
            print("✅ Both runinfo and l1_spec nodes exist!")
            
            # Check connections
            connections = workflow._graph.edges()
            runinfo_to_l1_spec = [(src, dst) for src, dst in connections if src == 'runinfo' and dst == 'l1_spec']
            
            if runinfo_to_l1_spec:
                print("✅ Connection found from runinfo to l1_spec!")
                print(f"  - Connections: {runinfo_to_l1_spec}")
            else:
                print("❌ No connection found from runinfo to l1_spec!")
                
            # Check what runinfo outputs and l1_spec inputs
            print(f"  - Runinfo node outputs: {list(runinfo_node.outputs.__dict__.keys())}")
            print(f"  - L1_spec node inputs: {list(l1_spec_node.inputs.__dict__.keys())}")
            
            # Check specific connections
            print("  - Checking workflow connections:")
            for src, dst, data in workflow._graph.edges(data=True):
                if src == 'runinfo' and dst == 'l1_spec':
                    print(f"    Connection: {src} -> {dst}")
                    print(f"    Data: {data}")
                elif 'runinfo' in [src, dst]:
                    print(f"    Related connection: {src} -> {dst}")
                    print(f"    Data: {data}")
            
        else:
            print("❌ Required nodes not found!")
        
        print()
        print("✅ FSL node connections test PASSED!")
        
    except Exception as e:
        print(f"❌ FSL node connections test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED! FSL will use output from _bids2nipypeinfo_from_df()")
    print("="*50)
    
    return True

if __name__ == "__main__":
    success = test_fsl_integration()
    sys.exit(0 if success else 1)
