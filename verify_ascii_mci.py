import pandas as pd
import re
import os
from pathlib import Path

def is_ascii(text):
    """Check if a string contains only ASCII characters."""
    if pd.isna(text):
        return True
    
    # Handle numeric types (int, float)
    if isinstance(text, (int, float)):
        return True
    
    # Convert to string and check
    try:
        str(text).encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def find_non_ascii_chars(text):
    """Find non-ASCII characters in a string."""
    if pd.isna(text):
        return []
    
    non_ascii_chars = []
    for i, char in enumerate(str(text)):
        try:
            char.encode('ascii')
        except UnicodeEncodeError:
            non_ascii_chars.append((i, char, f"U+{ord(char):04X}"))
    
    return non_ascii_chars

def verify_excel_ascii(file_path):
    """Verify that all strings in an Excel file are ASCII."""
    print(f"Verifying ASCII characters in: {file_path}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Read the Excel file
        xl = pd.ExcelFile(file_path)
        print(f"✓ Successfully opened Excel file")
        print(f"✓ Sheets found: {xl.sheet_names}")
        print()
        
        total_non_ascii = 0
        all_issues = []
        
        for sheet_name in xl.sheet_names:
            print(f"Checking sheet: {sheet_name}")
            print("-" * 40)
            
            try:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"  ✓ Sheet loaded: {df.shape[0]} rows × {df.shape[1]} columns")
                
                sheet_issues = []
                
                # Check each cell in the dataframe
                for row_idx, row in df.iterrows():
                    for col_idx, value in enumerate(row):
                        if not is_ascii(value):
                            non_ascii_chars = find_non_ascii_chars(value)
                            if non_ascii_chars:
                                issue = {
                                    'sheet': sheet_name,
                                    'row': row_idx + 1,  # Excel is 1-indexed
                                    'column': df.columns[col_idx],
                                    'value': str(value),
                                    'non_ascii_chars': non_ascii_chars
                                }
                                sheet_issues.append(issue)
                                all_issues.append(issue)
                
                if sheet_issues:
                    print(f"  ❌ Found {len(sheet_issues)} non-ASCII issues in this sheet")
                    for issue in sheet_issues[:5]:  # Show first 5 issues
                        print(f"    Row {issue['row']}, Col '{issue['column']}:")
                        print(f"      Value: {issue['value']}")
                        print(f"      Non-ASCII chars: {issue['non_ascii_chars']}")
                        print()
                    if len(sheet_issues) > 5:
                        print(f"    ... and {len(sheet_issues) - 5} more issues")
                else:
                    print(f"  ✅ All strings in this sheet are ASCII")
                
                total_non_ascii += len(sheet_issues)
                print()
                
            except Exception as e:
                print(f"  ❌ Error reading sheet '{sheet_name}': {e}")
                print()
        
        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if total_non_ascii == 0:
            print("✅ SUCCESS: All strings in the Excel file are ASCII!")
        else:
            print(f"❌ ISSUES FOUND: {total_non_ascii} non-ASCII strings detected")
            print()
            print("Detailed issues:")
            for i, issue in enumerate(all_issues, 1):
                print(f"{i}. Sheet: {issue['sheet']}, Row: {issue['row']}, Column: {issue['column']}")
                print(f"   Value: {issue['value']}")
                print(f"   Non-ASCII characters: {issue['non_ascii_chars']}")
                print()
        
        # Save detailed report to file
        if all_issues:
            report_file = "mci_ascii_verification_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("MCI Excel File ASCII Verification Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"File: {file_path}\n")
                f.write(f"Total issues found: {total_non_ascii}\n\n")
                
                for i, issue in enumerate(all_issues, 1):
                    f.write(f"{i}. Sheet: {issue['sheet']}\n")
                    f.write(f"   Row: {issue['row']}\n")
                    f.write(f"   Column: {issue['column']}\n")
                    f.write(f"   Value: {issue['value']}\n")
                    f.write(f"   Non-ASCII characters: {issue['non_ascii_chars']}\n\n")
            
            print(f"📄 Detailed report saved to: {report_file}")
        
        return total_non_ascii == 0
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {e}")
        return False

def main():
    # Check if MCI.xlsx exists
    mci_file = Path("assets/prepared/MCI.xlsx")
    
    if not mci_file.exists():
        print(f"❌ MCI.xlsx not found at: {mci_file}")
        print("Please run strategy_mci.py first to generate the file.")
        return
    
    # Verify ASCII
    success = verify_excel_ascii(mci_file)
    
    if success:
        print("\n🎉 All strings are ASCII - your data is clean!")
    else:
        print("\n⚠️  Non-ASCII characters found - review the report above")

if __name__ == "__main__":
    main()
