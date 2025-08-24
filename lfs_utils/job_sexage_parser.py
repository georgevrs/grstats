"""
JOB-SexAge Parser - FINAL CORRECTED VERSION
Correctly maps the three-level hierarchy structure from Excel
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Tuple

class JOBSexAgeParser:
    """
    Parser for JOB-SexAge sheet with CORRECT three-level hierarchy mapping
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse_sheet(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse the JOB-SexAge sheet with CORRECT hierarchy mapping
        """
        self.logger.info("Starting JOB-SexAge parsing with CORRECT hierarchy")
        
        file_path = analysis['file_path']
        sheet_name = analysis['sheet_name']
        
        # Read Excel without headers to see actual structure
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Extract the three levels correctly
        # Row 0: First Category (main job characteristics)
        # Row 1: Subcategories
        # Row 2: Sub-subcategories
        row0_categories = df.iloc[0]  # First Category
        row1_subcategories = df.iloc[1]  # Subcategories
        row2_subsubcategories = df.iloc[2]  # Sub-subcategories
        
        # Create the correct column mapping
        column_mapping = self._create_correct_column_mapping(
            row0_categories, row1_subcategories, row2_subsubcategories
        )
        
        # Create SDMX template
        template_df = self._create_sdmx_template(column_mapping)
        
        # Parse actual data
        parsed_df = self._parse_data_with_correct_hierarchy(
            df, column_mapping, analysis
        )
        
        self.logger.info(f"JOB-SexAge parsing completed: {len(parsed_df)} records")
        return parsed_df
    
    def _create_correct_column_mapping(self, row0_categories: pd.Series, 
                                     row1_subcategories: pd.Series, 
                                     row2_subsubcategories: pd.Series) -> List[Dict]:
        """
        Create CORRECT column mapping based on the actual Excel structure
        """
        mapping = []
        
        # Map each column based on the three-level hierarchy
        # We need to check ALL columns (0-74) and capture ANY that have data
        
        for col_idx in range(75):  # Check all 75 columns
            # Skip Year, Sex, Age columns (0, 1, 2)
            if col_idx in [0, 1, 2]:
                continue
                
            # Check if ANY of the three levels have data
            has_first_category = col_idx < len(row0_categories) and pd.notna(row0_categories.iloc[col_idx])
            has_subcategory = col_idx < len(row1_subcategories) and pd.notna(row1_subcategories.iloc[col_idx])
            has_sub_subcategory = col_idx < len(row2_subsubcategories) and pd.notna(row2_subsubcategories.iloc[col_idx])
            
            if has_first_category or has_subcategory or has_sub_subcategory:
                # Determine the first category based on column position
                if col_idx == 3:
                    first_category = 'Total Employed'
                elif col_idx in range(4, 9):
                    first_category = 'Number of persons working at the local unit'
                elif col_idx in range(9, 11):
                    first_category = 'Business ownership'
                elif col_idx in range(11, 20):
                    first_category = 'Sector of economic activity'
                elif col_idx in range(20, 25):
                    first_category = 'Type of occupation'
                elif col_idx in range(25, 29):
                    first_category = 'Status in employment'
                elif col_idx in range(29, 31):
                    first_category = 'Employment distinction'
                elif col_idx in range(31, 36):
                    first_category = 'Reasons for the part-time work'
                elif col_idx in range(36, 41):
                    first_category = 'Permanency of the job (for employees)'
                elif col_idx in range(41, 45):
                    first_category = 'Reasons for having a temporary job'
                elif col_idx in range(45, 57):
                    first_category = 'Hours actually worked during reference week'
                elif col_idx in range(57, 63):
                    first_category = 'Hours actually worked in reference week related to usual hours'
                elif col_idx in range(63, 75):
                    first_category = 'Atypical work'
                else:
                    first_category = 'Unknown'
                
                # Get the actual values from the rows
                subcategory = row1_subcategories.iloc[col_idx] if has_subcategory else '_Z'
                sub_subcategory = row2_subsubcategories.iloc[col_idx] if has_sub_subcategory else '_Z'
                
                mapping.append({
                    'column': col_idx,
                    'first_category': first_category,
                    'subcategory': subcategory,
                    'sub_subcategory': sub_subcategory,
                    'unit': 'persons'
                })
        
        self.logger.info(f"Created column mapping with {len(mapping)} entries")
        return mapping
    
    def _create_sdmx_template(self, column_mapping: List[Dict]) -> pd.DataFrame:
        """
        Create SDMX template with CORRECT hierarchy
        """
        self.logger.info("Creating SDMX template with CORRECT hierarchy")
        
        # Get all unique values for each level
        first_categories = set()
        subcategories = set()
        sub_subcategories = set()
        
        for entry in column_mapping:
            if entry['first_category'] != '_Z':
                first_categories.add(entry['first_category'])
            if entry['subcategory'] != '_Z':
                subcategories.add(entry['subcategory'])
            if entry['sub_subcategory'] != '_Z':
                sub_subcategories.add(entry['sub_subcategory'])
        
        # Create template records
        template_records = []
        
        # Add Total Employed (no subcategories or sub-subcategories)
        template_records.append({
            'Job_Characteristic': 'Total Employed',
            'Job_Subcategory': '_Z',
            'Job_Sub_Subcategory': '_Z'
        })
        
        # Add all other combinations
        for first_cat in sorted(first_categories):
            if first_cat != 'Total Employed':
                for subcat in sorted(subcategories):
                    for subsubcat in sorted(sub_subcategories):
                        template_records.append({
                            'Job_Characteristic': first_cat,
                            'Job_Subcategory': subcat,
                            'Job_Sub_Subcategory': subsubcat
                        })
        
        template_df = pd.DataFrame(template_records)
        self.logger.info(f"Created SDMX template with {len(template_df)} records")
        return template_df
    
    def _parse_data_with_correct_hierarchy(self, df: pd.DataFrame, 
                                         column_mapping: List[Dict], 
                                         analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse data with CORRECT hierarchy mapping
        """
        self.logger.info("Parsing data with CORRECT hierarchy")
        
        # Get demographic dimensions
        year_col = 0
        sex_col = 1
        age_col = 2
        
        # Data starts from row 4
        data_start_row = 4
        
        parsed_records = []
        
        # Process each data row
        for row_idx in range(data_start_row, len(df)):
            row_data = df.iloc[row_idx]
            
            # Extract demographic dimensions
            year = row_data.iloc[year_col]
            sex = row_data.iloc[sex_col]
            age = row_data.iloc[age_col]
            
            # Skip if missing key dimensions
            if pd.isna(year) or pd.isna(sex) or pd.isna(age):
                continue
            
            # Process each mapped column
            for entry in column_mapping:
                col_idx = entry['column']
                
                if col_idx < len(row_data):
                    value = row_data.iloc[col_idx]
                    
                    if pd.notna(value) and value != '':
                        record = {
                            'Year': year,
                            'Sex': sex,
                            'Age_Group': age,
                            'Job_Characteristic': entry['first_category'],
                            'Job_Subcategory': entry['subcategory'],
                            'Job_Sub_Subcategory': entry['sub_subcategory'],
                            'Unit_of_Measure': entry['unit'],
                            'Value': value
                        }
                        parsed_records.append(record)
        
        parsed_df = pd.DataFrame(parsed_records)
        self.logger.info(f"Parsed {len(parsed_df)} records with CORRECT hierarchy")
        return parsed_df
    
    def print_parsing_summary(self, parsed_df: pd.DataFrame, analysis: Dict[str, Any]):
        """
        Print parsing summary
        """
        print("\n" + "="*80)
        print("JOB-SexAge PARSING SUMMARY (CORRECTED)")
        print("="*80)
        
        print(f"Total records parsed: {len(parsed_df)}")
        print(f"Years covered: {sorted(parsed_df['Year'].unique())}")
        print(f"Sex categories: {sorted(parsed_df['Sex'].unique())}")
        print(f"Age groups: {sorted(parsed_df['Age_Group'].unique())}")
        
        print(f"\nJob Characteristics (Level 1): {len(parsed_df['Job_Characteristic'].unique())}")
        for char in sorted(parsed_df['Job_Characteristic'].unique()):
            count = len(parsed_df[parsed_df['Job_Characteristic'] == char])
            print(f"  - {char}: {count} records")
        
        print(f"\nJob Subcategories (Level 2): {len(parsed_df['Job_Subcategory'].unique())}")
        for subcat in sorted(parsed_df['Job_Subcategory'].unique()):
            if subcat != '_Z':
                count = len(parsed_df[parsed_df['Job_Subcategory'] == subcat])
                print(f"  - {subcat}: {count} records")
        
        print(f"\nJob Sub-Subcategories (Level 3): {len(parsed_df['Job_Sub_Subcategory'].unique())}")
        for subsubcat in sorted(parsed_df['Job_Sub_Subcategory'].unique()):
            if subsubcat != '_Z':
                count = len(parsed_df[parsed_df['Job_Sub_Subcategory'] == subsubcat])
                print(f"  - {subsubcat}: {count} records")
        
        # Check for missing values
        z_count_characteristic = len(parsed_df[parsed_df['Job_Characteristic'] == '_Z'])
        z_count_subcategory = len(parsed_df[parsed_df['Job_Subcategory'] == '_Z'])
        z_count_sub_subcategory = len(parsed_df[parsed_df['Job_Sub_Subcategory'] == '_Z'])
        
        print(f"\nMissing value analysis:")
        print(f"  Records with '_Z' in Job_Characteristic: {z_count_characteristic}")
        print(f"  Records with '_Z' in Job_Subcategory: {z_count_subcategory}")
        print(f"  Records with '_Z' in Job_Sub_Subcategory: {z_count_sub_subcategory}")
        
        # Records with all three levels populated
        non_z_records = parsed_df[
            (parsed_df['Job_Characteristic'] != '_Z') & 
            (parsed_df['Job_Subcategory'] != '_Z') & 
            (parsed_df['Job_Sub_Subcategory'] != '_Z')
        ]
        
        print(f"\nRecords with ALL three levels populated: {len(non_z_records)}")
        
        print("\n" + "="*80)
