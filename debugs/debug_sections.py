import pandas as pd

# Read the Excel file
df = pd.read_excel('assets/MCI/A0511_DKT60_TS_MM_01_2000_06_2025_02_F_EN.xlsx', 
                   sheet_name='MATERIAL COST INDICES 2000-2025', header=None)

print("Finding all section headers:")
print("=" * 60)

sections = []
for i in range(len(df)):
    col0 = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
    col1 = str(df.iloc[i, 1]) if pd.notna(df.iloc[i, 1]) else ""
    
    # Look for section headers (patterns like "MONTHLY XX")
    if "MONTHLY" in col0 or "ANNUAL" in col0 or col0.startswith("Base"):
        sections.append((i, col0, col1))
        print(f"Row {i:3d}: '{col0}' | '{col1}'")

print(f"\nFound {len(sections)} sections")
