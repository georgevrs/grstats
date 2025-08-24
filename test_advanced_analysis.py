"""
Test Advanced Analysis Script
Tests the advanced sheet analyzer on the POPUL-Regio sheet
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lfs_utils.advanced_sheet_analyzer import AdvancedSheetAnalyzer

def main():
    """Main function to test advanced analysis"""
    
    # File path for the first LFS annual file (01)
    file_path = "assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx"
    sheet_name = "POPUL-Regio"
    
    print(f"Testing advanced analysis of sheet '{sheet_name}' from file '{file_path}'")
    print("="*80)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    
    # Create advanced analyzer and analyze the sheet
    analyzer = AdvancedSheetAnalyzer()
    
    try:
        # Analyze the sheet with advanced methods
        analysis = analyzer.analyze_sheet(file_path, sheet_name)
        
        # Print advanced summary
        analyzer.print_advanced_analysis(analysis)
        
        # Additional detailed analysis
        print("\nDETAILED ADVANCED ANALYSIS:")
        print("-" * 50)
        
        # Show the actual data structure
        data_struct = analysis['data_structure']
        print(f"\nData Structure Details:")
        print(f"  Data area: Rows {data_struct['data_start_row']} to {data_struct['data_end_row']}")
        print(f"  Data area: Columns {data_struct['data_start_col']} to {data_struct['data_end_col']}")
        
        # Show sample of the actual data
        if data_struct['data_start_row'] is not None:
            sample_data = analysis['raw_dataframe'].iloc[
                data_struct['data_start_row']:data_struct['data_start_row']+5, 
                data_struct['data_start_col']:data_struct['data_end_col']+1
            ]
            print(f"\nSample data from data area:")
            print(sample_data.to_string())
        
        # Show column structure analysis
        print(f"\nColumn Structure Analysis:")
        for col_info in data_struct['column_structure'][:10]:  # Show first 10 columns
            print(f"  Col {col_info['column_index']}: {col_info['header_values']} -> {col_info['data_type']}")
            if col_info['sample_values']:
                print(f"    Sample values: {col_info['sample_values'][:3]}")
        
        # Show hierarchical layout
        hierarchy = analysis['hierarchical_layout']
        print(f"\nHierarchical Layout Analysis:")
        print(f"  Main categories: {hierarchy['main_categories']}")
        print(f"  Sub categories: {hierarchy['sub_categories']}")
        print(f"  This is a cross-tabulation: {hierarchy['cross_tabulation']}")
        
        # Show data mapping
        mapping = analysis['data_mapping']
        print(f"\nData Mapping Analysis:")
        print(f"  Dimension columns:")
        for dim_col in mapping['dimension_columns']:
            print(f"    - {dim_col['name']} (col {dim_col['column_index']}, type: {dim_col['type']})")
        print(f"  Value columns: {len(mapping['value_columns'])}")
        
        # Show clean dimensions
        print(f"\nClean Dimensions Found:")
        for dim_name, dim_values in analysis['dimensions'].items():
            print(f"  - {dim_name}: {len(dim_values)} values")
            if dim_values:
                print(f"    Values: {dim_values}")
        
    except Exception as e:
        print(f"ERROR during advanced analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
