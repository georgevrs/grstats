"""
Test the JOB-Regio parser with the same amazing logic as JOB-SexAge
"""

import pandas as pd
import sys
import os

# Add the lfs_utils directory to the path
sys.path.append('lfs_utils')

from job_regio_parser import JOBRegioParser

def test_job_regio_parser():
    """Test the JOB-Regio parser"""
    
    print("="*80)
    print("TESTING JOB-REGIO PARSER - SAME AMAZING LOGIC AS JOB-SexAge!")
    print("="*80)
    
    # Initialize parser
    parser = JOBRegioParser()
    
    # Create analysis dict
    analysis = {
        'file_path': 'assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx',
        'sheet_name': 'JOB-Regio'
    }
    
    # Parse the data
    print("1. Parsing JOB-Regio sheet...")
    parsed_df = parser.parse_sheet(analysis)
    
    print(f"Parsed data shape: {parsed_df.shape}")
    print(f"Columns: {list(parsed_df.columns)}")
    
    # Check unique values in key columns
    print("\n2. Checking unique values in key columns:")
    
    # Check basic dimensions
    if 'Year' in parsed_df.columns:
        years = parsed_df['Year'].unique()
        print(f"Years: {len(years)} unique values - {sorted(years)[:5]}...")
    
    if 'Region' in parsed_df.columns:
        regions = parsed_df['Region'].unique()
        print(f"Regions: {len(regions)} unique values - {regions}")
    
    # Check job characteristics
    if 'Job_Characteristic' in parsed_df.columns:
        characteristics = parsed_df['Job_Characteristic'].unique()
        print(f"Job Characteristics: {len(characteristics)} unique values")
        for char in sorted(characteristics):
            print(f"  - {char}")
    
    # Check data quality
    print(f"\n3. Data Quality Analysis:")
    print(f"Total records: {len(parsed_df)}")
    
    # Convert Value to numeric for analysis
    parsed_df['Value_numeric'] = pd.to_numeric(parsed_df['Value'], errors='coerce')
    non_zero_count = len(parsed_df[parsed_df['Value_numeric'] > 0])
    print(f"Records with non-zero values: {non_zero_count}")
    
    # Check _Z placeholders in the wide format columns
    _z_count = 0
    for col in parsed_df.columns:
        if col not in ['Year', 'Region', 'Unit_of_Measure', 'Value']:
            _z_count += len(parsed_df[parsed_df[col] == '_Z'])
    print(f"Total _Z placeholders across all columns: {_z_count}")
    
    # Check value types
    value_types = parsed_df['Value'].apply(type).value_counts()
    print(f"Value column types: {value_types}")
    
    # Check value distribution
    print(f"\n4. Value Distribution:")
    value_stats = parsed_df['Value_numeric'].describe()
    print(f"Value statistics:\n{value_stats}")
    
    print(f"\n🎉 JOB-REGIO PARSER TEST COMPLETED!")
    print(f"📊 Records: {len(parsed_df)}")
    print(f"🏗️ Structure: Same amazing logic as JOB-SexAge but for regions!")
    
    # Save the wide format DataFrame to Excel for verification
    print(f"\n5. Saving wide format DataFrame to Excel for verification...")
    output_filename = "test_job_regio_wide_format.xlsx"
    parsed_df.to_excel(output_filename, index=False)
    print(f"Saved wide format DataFrame to: {output_filename}")
    print(f"Columns in saved file: {list(parsed_df.columns)}")
    print(f"Shape: {parsed_df.shape}")

if __name__ == "__main__":
    test_job_regio_parser()
