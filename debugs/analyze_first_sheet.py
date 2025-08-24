"""
Analyze First Sheet Script
Analyzes the POPUL-Regio sheet from the first LFS annual file (01)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lfs_utils.sheet_analyzer import SheetAnalyzer

def main():
    """Main function to analyze the first sheet"""
    
    # File path for the first LFS annual file (01)
    file_path = "assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx"
    sheet_name = "POPUL-Regio"
    
    print(f"Starting analysis of sheet '{sheet_name}' from file '{file_path}'")
    print("="*80)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    
    # Create analyzer and analyze the sheet
    analyzer = SheetAnalyzer()
    
    try:
        # Analyze the sheet
        analysis = analyzer.analyze_sheet(file_path, sheet_name)
        
        # Print summary
        analyzer.print_analysis_summary(analysis)
        
        # Additional detailed analysis
        print("\nDETAILED ANALYSIS:")
        print("-" * 40)
        
        # Show first few rows of raw data
        print("\nFirst 10 rows of raw data:")
        print(analysis['raw_dataframe'].head(10).to_string())
        
        # Show dimensions in detail
        print(f"\nDetailed Dimensions Analysis:")
        for dim_name, dim_values in analysis['dimensions'].items():
            print(f"\nDimension: {dim_name}")
            print(f"  Values ({len(dim_values)}): {dim_values}")
        
        # Show data area information
        data_area = analysis['data_area']
        if data_area['start_row'] is not None:
            print(f"\nData Area Details:")
            print(f"  Start: Row {data_area['start_row']}, Col {data_area['start_col']}")
            print(f"  End: Row {data_area['end_row']}, Col {data_area['end_col']}")
            
                    # Show sample data from the data area
        if data_area['end_row'] and data_area['end_col']:
            sample_data = analysis['raw_dataframe'].iloc[data_area['start_row']:data_area['start_row']+5, data_area['start_col']:data_area['end_col']+1]
            print(f"\nSample data from data area:")
            print(sample_data.to_string())
        
    except Exception as e:
        print(f"ERROR during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
