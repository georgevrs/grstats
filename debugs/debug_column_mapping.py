"""
Debug the column mapping to see why some columns are being skipped
"""

import pandas as pd
import sys
import os

# Add the lfs_utils directory to the path
sys.path.append('lfs_utils')

from job_sexage_parser import JOBSexAgeParser

def debug_column_mapping():
    """Debug the column mapping creation"""
    
    print("="*80)
    print("DEBUGGING COLUMN MAPPING CREATION")
    print("="*80)
    
    # Read Excel without headers to see actual structure
    file_path = 'assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx'
    sheet_name = 'JOB-SexAge'
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    print(f"Excel shape: {df.shape}")
    
    # Extract the three levels correctly
    row0_categories = df.iloc[0]  # First Category
    row1_subcategories = df.iloc[1]  # Subcategories
    row2_subsubcategories = df.iloc[2]  # Sub-subcategories
    
    print(f"\nROW 0 (First Category) - Length: {len(row0_categories)}")
    print(f"ROW 1 (Subcategories) - Length: {len(row1_subcategories)}")
    print(f"ROW 2 (Sub-subcategories) - Length: {len(row2_subsubcategories)}")
    
    # Check each column manually
    print("\n" + "="*80)
    print("MANUAL COLUMN CHECK")
    print("="*80)
    
    for col_idx in range(75):  # Check all 75 columns
        # Skip Year, Sex, Age columns (0, 1, 2)
        if col_idx in [0, 1, 2]:
            continue
            
        # Check if ANY of the three levels have data
        has_first_category = col_idx < len(row0_categories) and pd.notna(row0_categories.iloc[col_idx])
        has_subcategory = col_idx < len(row1_subcategories) and pd.notna(row1_subcategories.iloc[col_idx])
        has_sub_subcategory = col_idx < len(row2_subsubcategories) and pd.notna(row2_subsubcategories.iloc[col_idx])
        
        if has_first_category or has_subcategory or has_sub_subcategory:
            # Determine the first category based on column position
            if col_idx == 3:
                first_category = 'Total Employed'
            elif col_idx in range(4, 9):
                first_category = 'Number of persons working at the local unit'
            elif col_idx in range(9, 11):
                first_category = 'Business ownership'
            elif col_idx in range(11, 20):
                first_category = 'Sector of economic activity'
            elif col_idx in range(20, 25):
                first_category = 'Type of occupation'
            elif col_idx in range(25, 29):
                first_category = 'Status in employment'
            elif col_idx in range(29, 31):
                first_category = 'Employment distinction'
            elif col_idx in range(31, 36):
                first_category = 'Reasons for the part-time work'
            elif col_idx in range(36, 41):
                first_category = 'Permanency of the job (for employees)'
            elif col_idx in range(41, 45):
                first_category = 'Reasons for having a temporary job'
            elif col_idx in range(45, 57):
                first_category = 'Hours actually worked during reference week'
            elif col_idx in range(57, 63):
                first_category = 'Hours actually worked in reference week related to usual hours'
            elif col_idx in range(63, 75):
                first_category = 'Atypical work'
            else:
                first_category = 'Unknown'
            
            # Get the actual values from the rows
            subcategory = row1_subcategories.iloc[col_idx] if has_subcategory else '_Z'
            sub_subcategory = row2_subsubcategories.iloc[col_idx] if has_sub_subcategory else '_Z'
            
            print(f"Column {col_idx:2d}: {first_category:40} -> {str(subcategory):30} -> {str(sub_subcategory):40}")
            
            # Show the actual values
            if has_first_category:
                print(f"           ROW 0: '{row0_categories.iloc[col_idx]}'")
            if has_subcategory:
                print(f"           ROW 1: '{row1_subcategories.iloc[col_idx]}'")
            if has_sub_subcategory:
                print(f"           ROW 2: '{row2_subsubcategories.iloc[col_idx]}'")
            print()
    
    # Now test the actual parser column mapping
    print("\n" + "="*80)
    print("TESTING ACTUAL PARSER COLUMN MAPPING")
    print("="*80)
    
    parser = JOBSexAgeParser()
    
    # Create analysis dict
    analysis = {
        'file_path': file_path,
        'sheet_name': sheet_name
    }
    
    # Call the column mapping method directly
    column_mapping = parser._create_correct_column_mapping(
        row0_categories, row1_subcategories, row2_subsubcategories
    )
    
    print(f"\nParser created {len(column_mapping)} column mappings")
    
    # Show what the parser actually mapped
    for mapping in column_mapping:
        col_idx = mapping['column']
        first_category = mapping['first_category']
        subcategory = mapping['subcategory']
        sub_subcategory = mapping['sub_subcategory']
        
        print(f"Parser Column {col_idx:2d}: {first_category:40} -> {str(subcategory):30} -> {str(sub_subcategory):40}")

if __name__ == "__main__":
    debug_column_mapping()
