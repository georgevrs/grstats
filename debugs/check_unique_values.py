"""
Check unique values in each column to identify missing information
"""

import pandas as pd
import sys
import os

# Add the lfs_utils directory to the path
sys.path.append('lfs_utils')

from job_sexage_parser import JOBSexAgeParser

def check_unique_values():
    """Check unique values in each column to identify missing information"""
    
    print("="*80)
    print("CHECKING UNIQUE VALUES IN JOB-SexAge PARSED DATA")
    print("="*80)
    
    # Initialize parser
    parser = JOBSexAgeParser()
    
    # Create analysis dict
    analysis = {
        'file_path': 'assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx',
        'sheet_name': 'JOB-SexAge'
    }
    
    # Parse the data
    print("Parsing JOB-SexAge sheet...")
    parsed_df = parser.parse_sheet(analysis)
    
    print(f"\nData shape: {parsed_df.shape}")
    print(f"Total columns: {len(parsed_df.columns)}")
    
    # Check unique values for each column
    print("\n" + "="*80)
    print("UNIQUE VALUES ANALYSIS")
    print("="*80)
    
    for col in parsed_df.columns:
        unique_vals = parsed_df[col].unique()
        print(f"\n{col}:")
        print(f"  Unique values: {len(unique_vals)}")
        print(f"  Values: {unique_vals}")
        
        # Check for _Z values
        z_count = (parsed_df[col] == '_Z').sum()
        if z_count > 0:
            print(f"  _Z count: {z_count}")
        
        # Check for missing values
        missing_count = parsed_df[col].isnull().sum()
        if missing_count > 0:
            print(f"  Missing values: {missing_count}")
    
    # Check specific columns that should have rich data
    print("\n" + "="*80)
    print("DETAILED ANALYSIS OF KEY COLUMNS")
    print("="*80)
    
    key_columns = [
        'Number of persons working at the local unit',
        'Sector of economic activity', 
        'Type of occupation',
        'Status in employment'
    ]
    
    for col in key_columns:
        if col in parsed_df.columns:
            print(f"\n{col}:")
            unique_vals = parsed_df[col].unique()
            print(f"  Unique values: {len(unique_vals)}")
            print(f"  Values: {unique_vals}")
            
            # Check distribution
            value_counts = parsed_df[col].value_counts()
            print(f"  Value distribution:")
            for val, count in value_counts.items():
                print(f"    {val}: {count}")
        else:
            print(f"\n{col}: COLUMN MISSING!")
    
    # Check _subcategory columns
    print("\n" + "="*80)
    print("_SUBCATEGORY COLUMNS ANALYSIS")
    print("="*80)
    
    subcategory_cols = [col for col in parsed_df.columns if col.endswith('_subcategory')]
    
    for col in subcategory_cols:
        print(f"\n{col}:")
        unique_vals = parsed_df[col].unique()
        print(f"  Unique values: {len(unique_vals)}")
        print(f"  Values: {unique_vals}")
        
        # Check distribution
        value_counts = parsed_df[col].value_counts()
        print(f"  Value distribution:")
        for val, count in value_counts.items():
            print(f"    {val}: {count}")
    
    # Check if we're missing expected values
    print("\n" + "="*80)
    print("MISSING EXPECTED VALUES CHECK")
    print("="*80)
    
    expected_values = {
        'Number of persons working at the local unit': [
            'Up to 10 persons', '11 to 19 persons', '20 to 49 persons', 
            '50 persons or more', 'Do not know but more than 10 person'
        ],
        'Business ownership': ['Public sector', 'Private sector'],
        'Sector of economic activity': ['Primary', 'Secondary', 'Tertiary'],
        'Type of occupation': [
            'Highly skilled non-manual', 'Low skilled non-manual', 'Skilled manual',
            'Agriculture, forestry, animal husbandry, fishing', 'Elementary occupations'
        ]
    }
    
    for col, expected in expected_values.items():
        if col in parsed_df.columns:
            actual_vals = set(parsed_df[col].unique())
            expected_set = set(expected)
            missing = expected_set - actual_vals
            extra = actual_vals - expected_set
            
            print(f"\n{col}:")
            if missing:
                print(f"  MISSING expected values: {missing}")
            if extra:
                print(f"  EXTRA unexpected values: {extra}")
            if not missing and not extra:
                print(f"  ✓ All expected values present")
        else:
            print(f"\n{col}: COLUMN MISSING!")
    
    return parsed_df

if __name__ == "__main__":
    check_unique_values()
