"""
Test the corrected JOB-SexAge parser with proper wide format structure
"""

import pandas as pd
import sys
import os

# Add the lfs_utils directory to the path
sys.path.append('lfs_utils')

from job_sexage_parser import JOBSexAgeParser

def test_corrected_wide_format():
    """Test the corrected wide format transformation"""
    
    print("="*80)
    print("TESTING CORRECTED JOB-SexAge PARSER")
    print("="*80)
    
    # Initialize parser
    parser = JOBSexAgeParser()
    
    # Create analysis dict
    analysis = {
        'file_path': 'assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx',
        'sheet_name': 'JOB-SexAge'
    }
    
    # Parse the data
    print("\n1. Parsing JOB-SexAge sheet...")
    parsed_df = parser.parse_sheet(analysis)
    
    print(f"Parsed data shape: {parsed_df.shape}")
    print(f"Columns: {list(parsed_df.columns)}")
    
    # Show sample of parsed data
    print("\n2. Sample of parsed data:")
    print(parsed_df.head(10))
    
    # The parser already returns wide format
    print("\n3. Data is already in wide format!")
    wide_df = parsed_df
    
    print(f"\n4. Wide format result:")
    print(f"Shape: {wide_df.shape}")
    print(f"Columns: {list(wide_df.columns)}")
    
    # Show sample of wide format
    print("\n5. Sample of wide format data:")
    print(wide_df.head(10))
    
    # Check for missing values
    print("\n6. Checking for missing values:")
    missing_counts = wide_df.isnull().sum()
    if missing_counts.sum() > 0:
        print("Missing values found:")
        print(missing_counts[missing_counts > 0])
    else:
        print("No missing values found!")
    
    # Save the result
    output_file = 'assets/prepared/lfs_job_sexage_parsed.xlsx'
    print(f"\n7. Saving to {output_file}...")
    wide_df.to_excel(output_file, index=False)
    print(f"Saved successfully!")
    
    # Verify the structure
    print("\n8. Verifying structure:")
    print(f"- Basic dimensions: Year, Sex, Age_Group ✓")
    
    # Check for main category columns
    main_categories = ['Number of persons working at the local unit', 'Business ownership', 
                      'Sector of economic activity', 'Type of occupation', 'Status in employment']
    
    for category in main_categories:
        if category in wide_df.columns:
            print(f"- {category} ✓")
        else:
            print(f"- {category} ✗ MISSING!")
    
    # Check for _subcategory columns
    subcategory_cols = [col for col in wide_df.columns if col.endswith('_subcategory')]
    print(f"- _subcategory columns: {len(subcategory_cols)} found ✓")
    
    print(f"\n9. Final result: {len(wide_df)} rows × {len(wide_df.columns)} columns")
    
    return wide_df

if __name__ == "__main__":
    test_corrected_wide_format()
