"""
Test POPUL-Status Parsing Script
Tests the specialized POPUL-Status parser on the POPUL-Status sheet
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lfs_utils.advanced_sheet_analyzer import AdvancedSheetAnalyzer
from lfs_utils.popul_status_parser import POPULStatusParser

def main():
    """Main function to test POPUL-Status parsing"""
    
    # File path for the first LFS annual file (01)
    file_path = "assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx"
    sheet_name = "POPUL-Status"
    
    print(f"Testing POPUL-Status parsing for sheet '{sheet_name}' from file '{file_path}'")
    print("="*80)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    
    try:
        # Step 1: Advanced Analysis
        print("STEP 1: Advanced Analysis")
        print("-" * 40)
        analyzer = AdvancedSheetAnalyzer()
        analysis = analyzer.analyze_sheet(file_path, sheet_name)
        analyzer.print_advanced_analysis(analysis)
        
        # Step 2: Create SDMX Template
        print("STEP 2: Creating SDMX Template")
        print("-" * 40)
        parser = POPULStatusParser()
        template_df = parser.create_sdmx_template(analysis)
        print(f"Template created: {len(template_df)} records x {len(template_df.columns)} columns")
        
        # Step 3: Parse Actual Data
        print("STEP 3: Parsing Actual Data")
        print("-" * 40)
        parsed_df = parser.parse_sheet(analysis)
        parser.print_parsing_summary(parsed_df, analysis)
        
        # Step 4: Show Template Structure
        print("STEP 4: SDMX Template Structure")
        print("-" * 40)
        print("Template columns:")
        for col in template_df.columns:
            print(f"  - {col}")
        
        print(f"\nTemplate sample (first 3 records):")
        print(template_df.head(3).to_string())
        
        # Step 5: Show Parsed Data Structure
        print("STEP 5: Parsed Data Structure")
        print("-" * 40)
        print("Parsed columns:")
        for col in parsed_df.columns:
            print(f"  - {col}")
        
        print(f"\nParsed data sample (first 10 records):")
        print(parsed_df.head(10).to_string())
        
        # Step 6: Save Results
        print("STEP 6: Saving Results")
        print("-" * 40)
        
        # Save template
        template_file = "assets/prepared/lfs_popul_status_template.xlsx"
        template_df.to_excel(template_file, index=False)
        print(f"Template saved to: {template_file}")
        
        # Save parsed data
        parsed_file = "assets/prepared/lfs_popul_status_parsed.xlsx"
        parsed_df.to_excel(parsed_file, index=False)
        print(f"Parsed data saved to: {parsed_file}")
        
        # Step 7: Summary
        print("STEP 7: Summary")
        print("-" * 40)
        print(f"✓ Analysis complete: {len(analysis['dimensions'])} dimensions identified")
        print(f"✓ Template created: {len(template_df)} template records")
        print(f"✓ Data parsed: {len(parsed_df)} actual records")
        print(f"✓ Files saved to assets/prepared/")
        
        print(f"\nNext steps:")
        print(f"1. Review the template structure")
        print(f"2. Verify the parsed data accuracy")
        print(f"3. Refine the parsing logic if needed")
        print(f"4. Proceed to next sheet when ready")
        
    except Exception as e:
        print(f"ERROR during POPUL-Status parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
