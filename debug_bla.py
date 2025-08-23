import pandas as pd

# Load the Excel file
xl = pd.ExcelFile("assets/BLA/A1302_SOP03_TS_MM_12_2007_03_2025_01_F_Bl.xlsx")
sheet = xl.parse(xl.sheet_names[0], header=None)

print("Sheet shape:", sheet.shape)
print("First 100 rows (all columns):")
for i in range(min(100, len(sheet))):
    row = sheet.iloc[i]
    print(f"Row {i}: {[row[j] for j in range(len(row))]} | Types: {[type(row[j]) for j in range(len(row))]}") 