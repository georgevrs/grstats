"""
Debug Column Mapping Script
Examines the exact column structure to understand the data layout
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

def main():
    """Main function to debug column mapping"""
    
    # File path for the first LFS annual file (01)
    file_path = "assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx"
    sheet_name = "POPUL-Regio"
    
    print(f"Debugging column mapping for sheet '{sheet_name}' from file '{file_path}'")
    print("="*80)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    
    try:
        # Read the sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        print(f"Sheet loaded: {df.shape[0]} rows x {df.shape[1]} columns")
        
        # Examine the first few rows in detail
        print(f"\nROW 0 (Main categories):")
        print("-" * 50)
        row0 = df.iloc[0]
        for col_idx, cell_value in enumerate(row0):
            if pd.notna(cell_value) and str(cell_value).strip():
                print(f"  Col {col_idx:2d}: '{cell_value}'")
        
        print(f"\nROW 1 (Sub-categories):")
        print("-" * 50)
        row1 = df.iloc[1]
        for col_idx, cell_value in enumerate(row1):
            if pd.notna(cell_value) and str(cell_value).strip():
                print(f"  Col {col_idx:2d}: '{cell_value}'")
        
        print(f"\nROW 2:")
        print("-" * 50)
        row2 = df.iloc[2]
        for col_idx, cell_value in enumerate(row2):
            if pd.notna(cell_value) and str(cell_value).strip():
                print(f"  Col {col_idx:2d}: '{cell_value}'")
        
        print(f"\nROW 3 (First data row):")
        print("-" * 50)
        row3 = df.iloc[3]
        for col_idx, cell_value in enumerate(row3):
            if pd.notna(cell_value):
                print(f"  Col {col_idx:2d}: {cell_value}")
        
        # Analyze the structure
        print(f"\nSTRUCTURE ANALYSIS:")
        print("-" * 50)
        
        # Find where each main category starts and ends
        main_categories = {}
        current_category = None
        current_start = None
        
        for col_idx, cell_value in enumerate(row0):
            if pd.notna(cell_value) and str(cell_value).strip():
                cat_name = str(cell_value).strip()
                if cat_name not in main_categories:
                    main_categories[cat_name] = {'start': col_idx, 'end': col_idx}
                else:
                    main_categories[cat_name]['end'] = col_idx
        
        print("Main category column spans:")
        for cat_name, span in main_categories.items():
            print(f"  {cat_name}: Columns {span['start']} to {span['end']}")
        
        # Map sub-categories to main categories
        print(f"\nSub-category mapping:")
        print("-" * 50)
        
        for col_idx, cell_value in enumerate(row1):
            if pd.notna(cell_value) and str(cell_value).strip():
                sub_cat = str(cell_value).strip()
                
                # Find which main category this belongs to
                main_cat = None
                for cat_name, span in main_categories.items():
                    if col_idx >= span['start'] and col_idx <= span['end']:
                        main_cat = cat_name
                        break
                
                print(f"  Col {col_idx:2d}: '{sub_cat}' -> {main_cat}")
        
        # Show sample data for each category
        print(f"\nSAMPLE DATA BY CATEGORY:")
        print("-" * 50)
        
        for cat_name, span in main_categories.items():
            print(f"\n{cat_name} (Columns {span['start']}-{span['end']}):")
            
            # Get sub-categories for this main category
            sub_cats = []
            for col_idx in range(span['start'], span['end'] + 1):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    sub_cats.append(f"{col_idx}:{row1.iloc[col_idx]}")
            
            print(f"  Sub-categories: {sub_cats}")
            
            # Show sample values
            if span['start'] < len(row3):
                sample_values = []
                for col_idx in range(span['start'], min(span['end'] + 1, len(row3))):
                    if pd.notna(row3.iloc[col_idx]):
                        sample_values.append(f"{col_idx}:{row3.iloc[col_idx]}")
                
                print(f"  Sample values: {sample_values}")
        
        # Special analysis for Column C (Population total)
        print(f"\nSPECIAL ANALYSIS - COLUMN C (Population total):")
        print("-" * 50)
        print(f"Column 2 (Population total):")
        print(f"  Row 0 (Main category): '{row0.iloc[2]}'")
        print(f"  Row 1 (Sub-category): '{row1.iloc[2] if pd.notna(row1.iloc[2]) else 'None'}'")
        print(f"  Row 3 (First data): {row3.iloc[2]}")
        
        # Show a few more rows for Column C to see the pattern
        print(f"  Sample values from Column C:")
        for row_idx in range(3, min(8, len(df))):
            value = df.iloc[row_idx, 2]
            if pd.notna(value):
                print(f"    Row {row_idx}: {value}")
        
        # Check if Column C has the same Year+Region pattern
        print(f"\nColumn C data pattern analysis:")
        print(f"  - Year values: {df.iloc[3:8, 0].tolist()}")
        print(f"  - Region values: {df.iloc[3:8, 1].tolist()}")
        print(f"  - Population total values: {df.iloc[3:8, 2].tolist()}")
        
    except Exception as e:
        print(f"ERROR during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
