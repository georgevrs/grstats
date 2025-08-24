"""
Debug the exact Excel structure to understand what I'm missing
"""

import pandas as pd

def debug_excel_structure():
    """Debug the exact Excel structure"""
    
    print("="*80)
    print("DEBUGGING EXCEL STRUCTURE")
    print("="*80)
    
    # Read Excel without headers
    df = pd.read_excel('assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx', 
                       sheet_name='JOB-SexAge', header=None)
    
    print(f"Excel shape: {df.shape}")
    
    print("\nROW 0 (First Category - Job Characteristics):")
    print("="*50)
    for i, val in enumerate(df.iloc[0]):
        if pd.notna(val) and str(val).strip():
            print(f"Col {i:2d}: {val}")
    
    print("\nROW 1 (Subcategories):")
    print("="*50)
    for i, val in enumerate(df.iloc[1]):
        if pd.notna(val) and str(val).strip():
            print(f"Col {i:2d}: {val}")
    
    print("\nROW 2 (Sub-subcategories):")
    print("="*50)
    for i, val in enumerate(df.iloc[2]):
        if pd.notna(val) and str(val).strip():
            print(f"Col {i:2d}: {val}")
    
    print("\n" + "="*80)
    print("UNDERSTANDING THE STRUCTURE:")
    print("="*80)
    
    print("ROW 0 contains the MAIN CATEGORIES (Job Characteristics):")
    print("- These should become COLUMNS in the wide format")
    print("- Each column represents a different aspect of job characteristics")
    
    print("\nROW 1 contains SUBcategories:")
    print("- These should become VALUES in the ROW 0 columns")
    print("- Each subcategory is a specific value for its parent category")
    
    print("\nROW 2 contains SUB-subcategories:")
    print("- These should become ADDITIONAL COLUMNS")
    print("- Each sub-subcategory is independent and connected to the grandparent (ROW 0)")
    
    print("\nEXAMPLE OF WHAT YOU WANT:")
    print("Number of persons working at the local unit | Up to 10 persons | 11 to 19 persons | 20 to 49 persons")
    print("Sector of economic activity | Primary | Secondary | Tertiary")
    print("Agriculture, forestry and fishing | Industry including energy | Construction | Trade, hotels and restaurants")

if __name__ == "__main__":
    debug_excel_structure()
