#!/usr/bin/env python3
"""
Test script for the CCI *02_F_EN.xlsx parser
"""
import pandas as pd
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy_cci2 import parse_cci_sheet_02_format, add_time_period_and_freq

def test_parser():
    """Test the parser with a sample *02_F_EN.xlsx file"""
    cci_files = []
    for file in os.listdir("assets/CCI"):
        if file.endswith("02_F_EN.xlsx"):
            cci_files.append(os.path.join("assets/CCI", file))
    
    if not cci_files:
        print("No *02_F_EN.xlsx files found in assets/CCI")
        return
    
    # Use the first file found
    input_file = cci_files[0]
    print(f"Testing with file: {input_file}")
    
    try:
        # Load the Excel file
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        
        print(f"Sheet shape: {sheet.shape}")
        print("First 10 rows of the sheet:")
        print(sheet.head(10))
        print("\n" + "="*50 + "\n")
        
        # Parse the data
        df = parse_cci_sheet_02_format(sheet)
        print(f"Parsed {len(df)} rows")
        
        if len(df) > 0:
            print("\nFirst 10 rows of parsed data:")
            print(df.head(10))
            
            # Add TIME_PERIOD and FREQ
            df_with_time = add_time_period_and_freq(df)
            print(f"\nAfter adding TIME_PERIOD and FREQ: {len(df_with_time)} rows")
            print("\nSample of final data:")
            print(df_with_time.head(10))
            
            # Show unique years and categories
            print(f"\nUnique years: {sorted(df['Year'].unique())}")
            print(f"Unique categories: {df['CategoryName'].unique()}")
            print(f"Unique quarters: {sorted(df['Quarter'].unique())}")
            
        else:
            print("No data was parsed. Check the parser logic.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
