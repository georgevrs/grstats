"""
Debug the data parsing to see why not all data is being extracted
"""

import pandas as pd
import sys
import os

# Add the lfs_utils directory to the path
sys.path.append('lfs_utils')

from job_sexage_parser import JOBSexAgeParser

def debug_data_parsing():
    """Debug the data parsing step by step"""
    
    print("="*80)
    print("DEBUGGING DATA PARSING STEP BY STEP")
    print("="*80)
    
    # Read Excel without headers to see actual structure
    file_path = 'assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx'
    sheet_name = 'JOB-SexAge'
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    print(f"Excel shape: {df.shape}")
    
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
    
    print(f"\nColumn mapping created: {len(column_mapping)} columns")
    
    # Now let's debug the data parsing
    print("\n" + "="*50)
    print("DEBUGGING DATA PARSING")
    print("="*50)
    
    # Start from row 3 (after the 3 header rows)
    data_start_row = 3
    
    # Check first few data rows
    for row_idx in range(data_start_row, min(data_start_row + 5, len(df))):
        row_data = df.iloc[row_idx]
        
        print(f"\n--- ROW {row_idx} ---")
        
        # Check if row has data
        if pd.isna(row_data.iloc[0]) or str(row_data.iloc[0]).strip() == '':
            print("EMPTY ROW - SKIPPING")
            continue
            
        # Extract Year, Sex, Age
        year = row_data.iloc[0]
        sex = row_data.iloc[1] 
        age = row_data.iloc[2]
        
        print(f"Year: {year}, Sex: {sex}, Age: {age}")
        
        # Check a few specific columns to see what data is there
        for col_info in column_mapping[:10]:  # Check first 10 columns
            col_idx = col_info['column']
            category = col_info['first_category']
            subcategory = col_info['subcategory']
            subsubcategory = col_info['sub_subcategory']
            
            value = row_data.iloc[col_idx]
            
            if not pd.isna(value) and str(value).strip() != '':
                print(f"  Col {col_idx} ({category}): {value}")
            else:
                print(f"  Col {col_idx} ({category}): EMPTY")
    
    # Now let's see what the parser actually extracts
    print("\n" + "="*50)
    print("TESTING ACTUAL PARSER OUTPUT")
    print("="*50)
    
    parsed_df = parser.parse_sheet(analysis)
    
    print(f"Parsed data shape: {parsed_df.shape}")
    print(f"Columns: {list(parsed_df.columns)}")
    
    # Check unique values in key columns
    print("\nUnique values in key columns:")
    for col in ['Number of persons working at the local unit', 'Business ownership', 'Sector of economic activity']:
        if col in parsed_df.columns:
            unique_vals = parsed_df[col].unique()
            print(f"\n{col}: {len(unique_vals)} unique values")
            print(f"Values: {unique_vals[:10]}")  # Show first 10
        else:
            print(f"\n{col}: COLUMN NOT FOUND!")

if __name__ == "__main__":
    debug_data_parsing()
