#!/usr/bin/env python3
"""
THOROUGH ANNUAL LFS SHEET STRUCTURE ANALYSIS
This script will analyze ALL annual sheets to understand the actual data model.
"""

import pandas as pd
import os
import re
from pathlib import Path

def analyze_annual_sheet_structure():
    """Thoroughly analyze the structure of ALL annual LFS sheets."""
    print("🔍 THOROUGH ANNUAL LFS SHEET STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Find all annual LFS files
    lfs_dir = Path("assets/LFS")
    annual_files = [f for f in lfs_dir.glob("*.xlsx") if "TS_AN" in f.name]
    
    print(f"📁 Found {len(annual_files)} annual LFS files:")
    for f in annual_files:
        print(f"  - {f.name}")
    
    print("\n" + "="*80)
    
    # Analyze each file and sheet
    for file_path in annual_files:
        print(f"\n📊 ANALYZING FILE: {file_path.name}")
        print("-" * 60)
        
        try:
            # Get all sheet names
            xl_file = pd.ExcelFile(file_path)
            sheet_names = xl_file.sheet_names
            
            print(f"📋 Sheets found: {len(sheet_names)}")
            for sheet_name in sheet_names:
                print(f"  - {sheet_name}")
            
            # Analyze each sheet in detail
            for sheet_name in sheet_names:
                print(f"\n🔍 ANALYZING SHEET: {sheet_name}")
                print("-" * 40)
                
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                print(f"  Shape: {df.shape}")
                
                # Analyze first 30 rows to understand structure
                print(f"  📋 First 30 rows analysis:")
                
                # Look for headers and data patterns
                for row_idx in range(min(30, len(df))):
                    row_data = df.iloc[row_idx]
                    
                    # Skip completely empty rows
                    if row_data.isna().all():
                        continue
                    
                    # Look for meaningful content
                    non_null_cells = row_data.dropna()
                    if len(non_null_cells) > 0:
                        print(f"    Row {row_idx}: {list(non_null_cells.head(10))}")
                        
                        # Check if this looks like a header row
                        if any(isinstance(cell, str) and any(keyword in str(cell).upper() for keyword in 
                               ['YEAR', 'REGION', 'AGE', 'SEX', 'GENDER', 'EDUCATION', 'SECTOR', 'OCCUPATION', 'STATUS']) 
                               for cell in non_null_cells):
                            print(f"      🎯 POTENTIAL HEADER ROW - Contains dimension keywords!")
                        
                        # Check if this looks like data
                        if any(isinstance(cell, (int, float)) and cell > 1900 and cell < 2030 for cell in non_null_cells):
                            print(f"      📅 POTENTIAL DATA ROW - Contains year-like values!")
                
                # Look for specific patterns in the sheet
                print(f"  🔍 Pattern analysis:")
                
                # Check for year patterns
                year_pattern = re.compile(r'19[8-9][0-9]|20[0-2][0-9]')
                years_found = []
                for row_idx in range(min(100, len(df))):
                    for col_idx in range(min(20, df.shape[1])):
                        cell_value = df.iloc[row_idx, col_idx]
                        if isinstance(cell_value, str) and year_pattern.search(str(cell_value)):
                            years_found.append((row_idx, col_idx, cell_value))
                        elif isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                            years_found.append((row_idx, col_idx, cell_value))
                
                if years_found:
                    print(f"    📅 Years found: {len(years_found)} instances")
                    for row, col, year in years_found[:5]:
                        print(f"      Row {row}, Col {col}: {year}")
                
                # Check for region patterns
                region_keywords = ['REGION', 'NUTS', 'MAKEDONIA', 'THRAKI', 'ATTIKI', 'KRITI', 'PELLOPONNISOS']
                regions_found = []
                for row_idx in range(min(100, len(df))):
                    for col_idx in range(min(20, df.shape[1])):
                        cell_value = df.iloc[row_idx, col_idx]
                        if isinstance(cell_value, str):
                            for keyword in region_keywords:
                                if keyword.upper() in str(cell_value).upper():
                                    regions_found.append((row_idx, col_idx, cell_value))
                                    break
                
                if regions_found:
                    print(f"    🌍 Regions found: {len(regions_found)} instances")
                    for row, col, region in regions_found[:5]:
                        print(f"      Row {row}, Col {col}: {region}")
                
                # Check for demographic patterns
                demo_keywords = ['MALE', 'FEMALE', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']
                demo_found = []
                for row_idx in range(min(100, len(df))):
                    for col_idx in range(min(20, df.shape[1])):
                        cell_value = df.iloc[row_idx, col_idx]
                        if isinstance(cell_value, str):
                            for keyword in demo_keywords:
                                if keyword.upper() in str(cell_value).upper():
                                    demo_found.append((row_idx, col_idx, cell_value))
                                    break
                
                if demo_found:
                    print(f"    👥 Demographics found: {len(demo_found)} instances")
                    for row, col, demo in demo_found[:5]:
                        print(f"      Row {row}, Col {col}: {demo}")
                
                # Check for economic sector patterns
                sector_keywords = ['AGRICULTURE', 'INDUSTRY', 'SERVICES', 'CONSTRUCTION', 'MINING', 'MANUFACTURING', 'TRADE', 'TRANSPORT', 'FINANCE']
                sectors_found = []
                for row_idx in range(min(100, len(df))):
                    for col_idx in range(min(20, df.shape[1])):
                        cell_value = df.iloc[row_idx, col_idx]
                        if isinstance(cell_value, str):
                            for keyword in sector_keywords:
                                if keyword.upper() in str(cell_value).upper():
                                    sectors_found.append((row_idx, col_idx, cell_value))
                                    break
                
                if sectors_found:
                    print(f"    🏭 Economic sectors found: {len(sectors_found)} instances")
                    for row, col, sector in sectors_found[:5]:
                        print(f"      Row {row}, Col {col}: {sector}")
                
                # Check for occupation patterns
                occ_keywords = ['MANAGERS', 'PROFESSIONALS', 'TECHNICIANS', 'CLERKS', 'SERVICE', 'SKILLED', 'UNSKILLED', 'ARMY']
                occ_found = []
                for row_idx in range(min(100, len(df))):
                    for col_idx in range(min(20, df.shape[1])):
                        cell_value = df.iloc[row_idx, col_idx]
                        if isinstance(cell_value, str):
                            for keyword in occ_keywords:
                                if keyword.upper() in str(cell_value).upper():
                                    occ_found.append((row_idx, col_idx, cell_value))
                                    break
                
                if occ_found:
                    print(f"    👷 Occupations found: {len(occ_found)} instances")
                    for row, col, occ in occ_found[:5]:
                        print(f"      Row {row}, Col {col}: {occ}")
                
                # Look for data structure patterns
                print(f"  📊 Data structure analysis:")
                
                # Check if this is a vertical time series (years in rows)
                vertical_years = 0
                for row_idx in range(min(100, len(df))):
                    if isinstance(df.iloc[row_idx, 0], (int, float)) and 1900 < df.iloc[row_idx, 0] < 2030:
                        vertical_years += 1
                
                if vertical_years > 0:
                    print(f"    📈 Vertical time series detected: {vertical_years} year rows found")
                
                # Check if this is a horizontal time series (years in columns)
                horizontal_years = 0
                for col_idx in range(min(20, df.shape[1])):
                    if isinstance(df.iloc[0, col_idx], (int, float)) and 1900 < df.iloc[0, col_idx] < 2030:
                        horizontal_years += 1
                
                if horizontal_years > 0:
                    print(f"    📊 Horizontal time series detected: {horizontal_years} year columns found")
                
                # Check for pivot table structure
                if len(df) > 10 and len(df.columns) > 5:
                    # Look for totals and subtotals
                    total_rows = 0
                    for row_idx in range(min(100, len(df))):
                        row_str = ' '.join(str(cell) for cell in df.iloc[row_idx] if pd.notna(cell))
                        if 'TOTAL' in row_str.upper():
                            total_rows += 1
                    
                    if total_rows > 0:
                        print(f"    📋 Pivot table structure detected: {total_rows} total rows found")
                
                print(f"  ✅ Sheet analysis complete")
                
        except Exception as e:
            print(f"  ❌ ERROR analyzing {file_path.name}: {e}")
            continue
    
    print(f"\n🏁 COMPLETE ANNUAL SHEET STRUCTURE ANALYSIS FINISHED")
    print("=" * 80)

if __name__ == "__main__":
    analyze_annual_sheet_structure()
