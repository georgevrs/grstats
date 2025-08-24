"""
Main LFS Processor
Orchestrates the processing of multiple LFS annual datasets
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Any
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lfs_utils.advanced_sheet_analyzer import AdvancedSheetAnalyzer
from lfs_utils.data_parser import LFSDataParser

class LFSMainProcessor:
    """Main processor for LFS annual datasets"""
    
    def __init__(self):
        self.analyzer = AdvancedSheetAnalyzer()
        self.parser = LFSDataParser()
        self.processed_sheets = {}
        self.combined_data = None
        
    def process_lfs_file(self, file_path: str, target_sheets: List[str] = None) -> Dict[str, Any]:
        """
        Process a single LFS file
        
        Args:
            file_path: Path to the LFS Excel file
            target_sheets: List of sheet names to process (None = all sheets)
            
        Returns:
            Dictionary containing processing results
        """
        print(f"\n{'='*80}")
        print(f"PROCESSING LFS FILE: {os.path.basename(file_path)}")
        print(f"{'='*80}")
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return {}
        
        # Get all sheets if none specified
        if target_sheets is None:
            excel_file = pd.ExcelFile(file_path)
            target_sheets = excel_file.sheet_names
            print(f"Found {len(target_sheets)} sheets: {target_sheets}")
        
        results = {}
        
        for sheet_name in target_sheets:
            try:
                print(f"\nProcessing sheet: {sheet_name}")
                print("-" * 50)
                
                # Analyze the sheet
                analysis = self.analyzer.analyze_sheet(file_path, sheet_name)
                
                # Parse the data
                parsed_df = self.parser.parse_sheet(analysis)
                
                # Create template
                template_df = self.parser.create_sdmx_template(analysis)
                
                # Store results
                results[sheet_name] = {
                    'analysis': analysis,
                    'parsed_data': parsed_df,
                    'template': template_df,
                    'file_path': file_path
                }
                
                print(f"✓ Sheet '{sheet_name}' processed successfully")
                print(f"  - Records: {len(parsed_df)}")
                print(f"  - Columns: {len(parsed_df.columns)}")
                
            except Exception as e:
                print(f"✗ Error processing sheet '{sheet_name}': {e}")
                continue
        
        return results
    
    def process_all_lfs_files(self, base_path: str = "assets/LFS") -> Dict[str, Any]:
        """
        Process all LFS annual files
        
        Args:
            base_path: Base path containing LFS files
            
        Returns:
            Dictionary containing all processing results
        """
        print(f"\n{'='*80}")
        print(f"PROCESSING ALL LFS ANNUAL FILES")
        print(f"{'='*80}")
        
        # Find LFS annual files (pattern: *TS_AN*)
        lfs_files = []
        for file in os.listdir(base_path):
            if file.endswith('.xlsx') and 'TS_AN' in file:
                lfs_files.append(os.path.join(base_path, file))
        
        print(f"Found {len(lfs_files)} LFS annual files:")
        for file in lfs_files:
            print(f"  - {os.path.basename(file)}")
        
        all_results = {}
        
        # Process each file
        for file_path in lfs_files:
            file_results = self.process_lfs_file(file_path)
            all_results[os.path.basename(file_path)] = file_results
        
        return all_results
    
    def combine_all_data(self, results: Dict[str, Any]) -> pd.DataFrame:
        """
        Combine all processed data into a single wide table
        
        Args:
            results: Results from processing
            
        Returns:
            Combined DataFrame
        """
        print(f"\n{'='*80}")
        print(f"COMBINING ALL DATA INTO WIDE TABLE")
        print(f"{'='*80}")
        
        all_dataframes = []
        
        for file_name, file_results in results.items():
            for sheet_name, sheet_results in file_results.items():
                df = sheet_results['parsed_data'].copy()
                
                # Add metadata columns
                df['Source_File'] = file_name
                df['Source_Sheet'] = sheet_name
                
                all_dataframes.append(df)
        
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            print(f"✓ Combined data created: {len(combined_df)} records x {len(combined_df.columns)} columns")
            
            # Save combined data
            output_file = "assets/prepared/lfs_combined_all_data.xlsx"
            combined_df.to_excel(output_file, index=False)
            print(f"✓ Combined data saved to: {output_file}")
            
            return combined_df
        else:
            print("✗ No data to combine")
            return pd.DataFrame()
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a summary report of all processing"""
        report = []
        report.append("LFS ANNUAL DATASETS PROCESSING SUMMARY")
        report.append("=" * 60)
        report.append("")
        
        total_sheets = 0
        total_records = 0
        
        for file_name, file_results in results.items():
            report.append(f"FILE: {file_name}")
            report.append("-" * 40)
            
            for sheet_name, sheet_results in file_results.items():
                df = sheet_results['parsed_data']
                records = len(df)
                columns = len(df.columns)
                
                report.append(f"  {sheet_name}: {records} records, {columns} columns")
                total_sheets += 1
                total_records += records
            
            report.append("")
        
        report.append(f"TOTAL: {total_sheets} sheets, {total_records} records")
        report.append("")
        report.append("Files saved to assets/prepared/")
        
        return "\n".join(report)

def main():
    """Main function to run the LFS processor"""
    
    processor = LFSMainProcessor()
    
    # Option 1: Process specific file and sheets
    print("OPTION 1: Process specific file and sheets")
    print("=" * 50)
    
    file_path = "assets/LFS/A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx"
    target_sheets = ["POPUL-Regio"]  # Add more sheets as needed
    
    results = processor.process_lfs_file(file_path, target_sheets)
    
    # Option 2: Process all LFS files (uncomment when ready)
    # print("\nOPTION 2: Process all LFS files")
    # print("=" * 50)
    # all_results = processor.process_all_lfs_files()
    
    # Combine data
    combined_df = processor.combine_all_data(results)
    
    # Generate summary
    summary = processor.generate_summary_report(results)
    print(f"\n{summary}")
    
    print(f"\n{'='*80}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Next steps:")
    print(f"1. Review the parsed data for accuracy")
    print(f"2. Add more sheets to target_sheets list")
    print(f"3. Uncomment Option 2 to process all files")
    print(f"4. Refine parsing logic as needed")

if __name__ == "__main__":
    main()
