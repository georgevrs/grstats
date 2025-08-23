import pandas as pd

# Read the Excel file
df = pd.read_excel('assets/MCI/A0511_DKT60_TS_MM_01_2000_06_2025_02_F_EN.xlsx', 
                   sheet_name='MATERIAL COST INDICES 2000-2025', header=None)

print("Examining MCI structure v1 for year identification:")
print("=" * 60)
print("Row | Col0       | Col1")
print("-" * 60)

for i in range(30, 70):
    col0 = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else "NaN"
    col1 = str(df.iloc[i, 1]) if pd.notna(df.iloc[i, 1]) else "NaN"
    print(f"{i:3d} | {col0[:10]:10s} | {col1[:40]:40s}")
