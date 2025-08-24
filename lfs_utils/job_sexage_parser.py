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
        
        # Parse actual data
        parsed_df = self._parse_data_with_correct_hierarchy(
            df, column_mapping, analysis
        )
        
        # Transform to wide SDMX format
        wide_df = self.transform_to_sdmx_wide_format(parsed_df)
        
        # Save both formats
        self._save_parsed_data(parsed_df, wide_df, analysis)
        
        self.logger.info(f"JOB-SexAge parsing completed: {len(parsed_df)} records, wide format: {len(wide_df)} records")
        return wide_df  # Return wide format as primary output
    
    def _create_correct_column_mapping(self, row0_categories: pd.Series, 
                                     row1_subcategories: pd.Series, 
                                     row2_subsubcategories: pd.Series) -> List[Dict]:
        """
        Create CORRECT column mapping based on the actual Excel structure
        """
        mapping = []
        
        print("Creating column mapping for ALL columns...")
        
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
                
                # Clean up the values
                if pd.notna(subcategory):
                    subcategory = str(subcategory).strip()
                else:
                    subcategory = '_Z'
                    
                if pd.notna(sub_subcategory):
                    sub_subcategory = str(sub_subcategory).strip()
                else:
                    sub_subcategory = '_Z'
                
                mapping.append({
                    'column': col_idx,
                    'first_category': first_category,
                    'subcategory': subcategory,
                    'sub_subcategory': sub_subcategory
                })
                
                print(f"  Column {col_idx}: {first_category} -> {subcategory} -> {sub_subcategory}")
        
        print(f"Created mapping for {len(mapping)} columns")
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
    
    def _parse_data_with_correct_hierarchy(self, df: pd.DataFrame, column_mapping: List[Dict], analysis: Dict) -> pd.DataFrame:
        """
        Parse ALL data rows with correct hierarchy mapping
        """
        print("Parsing ALL data rows with correct hierarchy...")
        
        # Start from row 3 (after the 3 header rows)
        data_start_row = 3
        
        # Get all data rows
        data_rows = []
        
        # Process each row in the Excel data
        for row_idx in range(data_start_row, len(df)):
            row_data = df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row_data.iloc[0]) or str(row_data.iloc[0]).strip() == '':
                continue
            
            # Extract basic dimensions (Year, Sex, Age_Group)
            year = row_data.iloc[0]
            sex = row_data.iloc[1] 
            age_group = row_data.iloc[2]
            
            # Skip if basic dimensions are missing
            if pd.isna(year) or pd.isna(sex) or pd.isna(age_group):
                continue
            
            # Process each column mapping to extract ALL values
            for mapping in column_mapping:
                col_idx = mapping['column']
                first_category = mapping['first_category']
                subcategory = mapping['subcategory']
                sub_subcategory = mapping['sub_subcategory']
                
                # Get the actual numeric value from this row/column
                if col_idx < len(row_data):
                    value = row_data.iloc[col_idx]
                    
                    # Only process if we have a valid numeric value
                    if pd.notna(value) and str(value).strip() != '':
                        try:
                            # Try to convert to numeric
                            numeric_value = float(value)
                            
                            # Create a record for this data point
                            record = {
                                'Year': year,
                                'Sex': sex,
                                'Age_Group': age_group,
                                'Job_Characteristic': first_category,
                                'Job_Subcategory': subcategory if pd.notna(subcategory) and str(subcategory).strip() != '' else '_Z',
                                'Job_Sub_Subcategory': sub_subcategory if pd.notna(sub_subcategory) and str(sub_subcategory).strip() != '' else '_Z',
                                'Value': numeric_value,
                                'Unit_of_Measure': 'persons'  # Default unit, can be enhanced later
                            }
                            
                            data_rows.append(record)
                            
                        except (ValueError, TypeError):
                            # Skip non-numeric values
                            continue
        
        print(f"Extracted {len(data_rows)} data records from Excel")
        
        # Create DataFrame
        parsed_df = pd.DataFrame(data_rows)
        
        # Clean up the data
        parsed_df = parsed_df.dropna(subset=['Value'])
        parsed_df = parsed_df[parsed_df['Value'] != 0]  # Remove zero values
        
        print(f"Final parsed data: {len(parsed_df)} records")
        
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
                count = len(parsed_df[df['Job_Sub_Subcategory'] == subsubcat])
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

    def transform_to_sdmx_wide_format(self, df):
        """
        Transform the parsed data to SDMX wide format with proper column structure.
        The parsed data already has the correct structure, we just need to reshape it.
        """
        print("Transforming to SDMX wide format...")
        
        print(f"Input data shape: {df.shape}")
        print(f"Input columns: {list(df.columns)}")
        
        # The parsed data already has the correct structure with these columns:
        # Year, Sex, Age_Group, Job_Characteristic, Job_Subcategory, Job_Sub_Subcategory, Unit_of_Measure, Value
        
        # We need to pivot this to wide format where:
        # - Job_Characteristic becomes columns
        # - Job_Subcategory becomes values in those columns
        # - Job_Sub_Subcategory becomes _subcategory columns for two-level categories
        
        # First, identify which categories have sub-subcategories (two levels)
        two_level_categories = set()
        for category in df['Job_Characteristic'].unique():
            category_data = df[df['Job_Characteristic'] == category]
            has_subsubcategories = category_data['Job_Sub_Subcategory'].notna().any() and \
                                 (category_data['Job_Sub_Subcategory'] != '_Z').any()
            if has_subsubcategories:
                two_level_categories.add(category)
                print(f"  {category} -> TWO-LEVEL (has sub-subcategories)")
            else:
                print(f"  {category} -> SINGLE-LEVEL (no sub-subcategories)")
        
        # Create the wide format by pivoting the data
        wide_rows = []
        
        # Process each record in the parsed data
        for idx, row in df.iterrows():
            row_data = {
                'Year': row['Year'],
                'Sex': row['Sex'],
                'Age_Group': row['Age_Group']
            }
            
            # Get the job characteristic for this row
            job_char = row['Job_Characteristic']
            job_sub = row['Job_Subcategory']
            job_subsub = row['Job_Sub_Subcategory']
            
            # Initialize all columns with _Z
            for category in df['Job_Characteristic'].unique():
                if category in two_level_categories:
                    row_data[category] = '_Z'
                    row_data[f"{category}_subcategory"] = '_Z'
                else:
                    row_data[category] = '_Z'
            
            # Populate the specific job characteristic for this row
            if job_char in two_level_categories:
                # TWO-LEVEL CATEGORY: Set both main and subcategory columns
                row_data[job_char] = job_sub if pd.notna(job_sub) and str(job_sub).strip() != '' else '_Z'
                row_data[f"{job_char}_subcategory"] = job_subsub if pd.notna(job_subsub) and str(job_subsub).strip() != '' else '_Z'
            else:
                # SINGLE-LEVEL CATEGORY: Set only main column
                row_data[job_char] = job_sub if pd.notna(job_sub) and str(job_sub).strip() != '' else '_Z'
            
            # Add Unit of Measure and Value
            row_data['Unit_of_Measure'] = row['Unit_of_Measure'] if pd.notna(row['Unit_of_Measure']) else '_Z'
            row_data['Value'] = row['Value'] if pd.notna(row['Value']) else 0
            
            wide_rows.append(row_data)
        
        # Create the wide DataFrame
        wide_df = pd.DataFrame(wide_rows)
        
        # Clean column names (remove extra spaces)
        wide_df.columns = [col.strip() if isinstance(col, str) else col for col in wide_df.columns]
        
        # Clean data values - fix spacing issues
        for col in wide_df.columns:
            if isinstance(col, str) and 'Type of occupation' in col:
                # Fix the "Highly skilled non- manual" spacing issue
                wide_df[col] = wide_df[col].astype(str).str.replace('non- manual', 'non-manual')
        
        # General data cleaning - remove extra spaces in all text columns
        for col in wide_df.columns:
            if wide_df[col].dtype == 'object':  # Text columns
                wide_df[col] = wide_df[col].astype(str).str.strip()
                # Replace multiple spaces with single space
                wide_df[col] = wide_df[col].str.replace(r'\s+', ' ', regex=True)
        
        print(f"Created wide format with {len(wide_df)} rows and {len(wide_df.columns)} columns")
        print(f"Columns: {list(wide_df.columns)}")
        
        return wide_df

    def _save_parsed_data(self, parsed_df: pd.DataFrame, wide_df: pd.DataFrame, analysis: Dict[str, Any]):
        """
        Save both long and wide format data
        """
        self.logger.info("Saving parsed data in both formats")
        
        # Save long format (original)
        long_file = "assets/prepared/lfs_job_sexage_parsed_long.xlsx"
        parsed_df.to_excel(long_file, index=False)
        self.logger.info(f"Long format saved: {long_file}")
        
        # Save wide format (SDMX)
        wide_file = "assets/prepared/lfs_job_sexage_parsed.xlsx"
        wide_df.to_excel(wide_file, index=False)
        self.logger.info(f"Wide format saved: {wide_file}")
        
        # Also save wide format as CSV for easier inspection
        csv_file = "assets/prepared/lfs_job_sexage_parsed.csv"
        wide_df.to_csv(csv_file, index=False)
        self.logger.info(f"Wide format CSV saved: {csv_file}")
