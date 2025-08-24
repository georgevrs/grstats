"""
Check what keys are actually in the column mapping dictionary
"""

import pandas as pd
import sys
import os

# Add the lfs_utils directory to the path
sys.path.append('lfs_utils')

from job_sexage_parser import JOBSexAgeParser

def check_column_keys():
    """Check what keys are in the column mapping"""
    
    print("="*80)
    print("CHECKING COLUMN MAPPING KEYS")
    print("="*80)
    
    # Read Excel without headers to see actual structure
    file_path = 'assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx'
    sheet_name = 'JOB-SexAge'
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # Extract the three levels correctly
    row0_categories = df.iloc[0]
    row1_subcategories = df.iloc[1]
    row2_subsubcategories = df.iloc[2]
    
    # Initialize parser to get column mapping
    parser = JOBSexAgeParser()
    analysis = {
        'file_path': file_path,
        'sheet_name': sheet_name
    }
    
    # Get column mapping
    column_mapping = parser._create_correct_column_mapping(
        row0_categories, row1_subcategories, row2_subsubcategories
    )
    
    print(f"Column mapping created: {len(column_mapping)} columns")
    
    # Check the first column mapping to see what keys it has
    if column_mapping:
        first_col = column_mapping[0]
        print(f"\nFirst column mapping keys: {list(first_col.keys())}")
        print(f"First column mapping: {first_col}")
        
        # Check a few more to see the pattern
        print(f"\nSecond column mapping: {column_mapping[1]}")
        print(f"Third column mapping: {column_mapping[2]}")

if __name__ == "__main__":
    check_column_keys()
