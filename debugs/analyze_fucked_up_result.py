"""
Analyze what I actually created vs what was requested
"""

import pandas as pd

def analyze_what_i_created():
    """Analyze the fucked up result I created"""
    
    print("="*80)
    print("ANALYZING WHAT I ACTUALLY CREATED (THE FUCKED UP RESULT)")
    print("="*80)
    
    # Read the file I created
    df = pd.read_excel('assets/prepared/lfs_job_sexage_parsed.xlsx')
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    print()
    
    print("COLUMNS I CREATED:")
    for i, col in enumerate(df.columns):
        print(f"{i:2d}: {col}")
    
    print("\n" + "="*80)
    print("UNIQUE VALUES IN NON-NUMERIC COLUMNS:")
    print("="*80)
    
    for col in df.columns:
        if col not in ['Year', 'Total_Employed']:
            unique_vals = df[col].unique()
            print(f"\n{col}:")
            if len(unique_vals) <= 10:
                for val in unique_vals:
                    print(f"  - {val}")
            else:
                for val in unique_vals[:10]:
                    print(f"  - {val}")
                print(f"  ... and {len(unique_vals) - 10} more")
    
    print("\n" + "="*80)
    print("WHAT I FUCKED UP:")
    print("="*80)
    
    print("1. I created columns like 'Primary_subcategories' with comma-separated values")
    print("2. I created 'Unknown_' columns for sub-subcategories without proper subcategories")
    print("3. I did NOT create the proper one-hot encoding structure you asked for")
    print("4. The result is completely irrelevant to what you requested")
    
    print("\nWHAT YOU ACTUALLY WANTED:")
    print("1. Each Job_Characteristic becomes a COLUMN")
    print("2. Each Job_Subcategory becomes a VALUE in that column")
    print("3. Each Job_Sub_Subcategory becomes an ADDITIONAL COLUMN")
    print("4. Total_Employed becomes _T (numeric values)")
    print("5. _Z where not applicable")
    
    print("\nEXAMPLE OF WHAT YOU WANTED:")
    print("Number of persons working at the local unit | Up to 10 persons | 11 to 19 persons | 20 to 49 persons | 50 persons or more | Do not know but more than 10 person")
    print("Sector of economic activity | Primary | Secondary | Tertiary")
    print("Sector of economic activity subcategories | Agriculture, forestry and fishing | Secondary sector total | Industry including energy | Construction | Tertiary sector total | Trade, hotels and restaurants, transport and communication | Financial, real estate, renting and business activities | Other service activities | Did no answer")

if __name__ == "__main__":
    analyze_what_i_created()
