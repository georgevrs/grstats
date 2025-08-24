"""
JOB-Regio Parser

Specialized parser for the JOB-Regio sheet from File 02.
This sheet has the same structure as JOB-SexAge but groups by Region instead of Sex+Age.

Structure:
- ROW 0: Job characteristics (Total Employed, Business ownership, Sector of economic activity, etc.)
- ROW 1: Subcategories (Up to 10 persons, Public sector, Primary, etc.)
- ROW 2: Sub-subcategories (Agriculture, forestry and fishing, Industry including energy, etc.)
- DATA: Organized by Year + Region instead of Year + Sex + Age

FOLLOWS THE PERFECT RATIONAL FROM JOB-SexAge: Uses column range segmentation for perfect category mapping!
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple
from advanced_sheet_analyzer import AdvancedSheetAnalyzer

class JOBRegioParser:
    """
    Parser for JOB-Regio sheet with regional organization instead of demographic organization.
    Uses the same parsing logic as JOB-SexAge but adapted for regional grouping.
    FOLLOWS THE PERFECT RATIONAL: Column range segmentation for perfect category mapping!
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzer = AdvancedSheetAnalyzer()

    def parse_sheet(self, analysis: Dict) -> pd.DataFrame:
        """
        Parse the JOB-Regio sheet into SDMX wide format

        Args:
            analysis: Dictionary containing file_path and sheet_name

        Returns:
            DataFrame in SDMX wide format
        """
        file_path = analysis['file_path']
        sheet_name = analysis['sheet_name']

        self.logger.info(f"Starting JOB-Regio parsing for {sheet_name}")

        # Analyze the sheet structure
        print(f"Analyzing sheet structure for {sheet_name}...")
        sheet_analysis = self.analyzer.analyze_sheet(file_path, sheet_name)

        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # Extract the three levels correctly (same as JOB-SexAge)
        row0_categories = df.iloc[0]
        row1_subcategories = df.iloc[1]
        row2_subsubcategories = df.iloc[2]

        # Create column mapping (same logic as JOB-SexAge)
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

        self.logger.info(f"JOB-Regio parsing completed: {len(parsed_df)} records, wide format: {len(wide_df)} records")
        return wide_df  # Return wide format as primary output

    def _create_correct_column_mapping(self, row0_categories: pd.Series,
                                             row1_subcategories: pd.Series,
                                             row2_subsubcategories: pd.Series) -> List[Dict]:
        """
        Create CORRECT column mapping based on the actual Excel structure
        JOB-Regio has headers spread across columns, not continuous like JOB-SexAge
        FOLLOW THE PERFECT RATIONAL FROM JOB-SexAge: USE COLUMN RANGES TO SEGMENT CATEGORIES!
        
        This is the CLEVER TRICK: We use column position ranges to determine the first category,
        exactly like JOB-SexAge does, ensuring perfect category segmentation!
        """
        mapping = []

        print("Creating column mapping for ALL 74 columns using JOB-SexAge CLEVER TRICK...")

        # Map each column based on the three-level hierarchy
        # FOLLOW JOB-SexAge: USE COLUMN RANGES TO DETERMINE FIRST CATEGORY!

        for col_idx in range(74):  # Check all 74 columns
            # Skip Year and Region columns (0, 1) - these are in row 2
            if col_idx in [0, 1]:
                continue

            # FOLLOW JOB-SexAge CLEVER TRICK: Determine first category based on column position
            if col_idx == 2:
                first_category = 'Total Employed'
            elif col_idx in range(3, 8):
                first_category = 'Number of persons working at the local unit'
            elif col_idx in range(8, 10):
                first_category = 'Business ownership'
            elif col_idx in range(10, 19):
                first_category = 'Sector of economic activity'
            elif col_idx in range(19, 24):
                first_category = 'Type of occupation'
            elif col_idx in range(24, 28):
                first_category = 'Status in employment'
            elif col_idx in range(28, 30):
                first_category = 'Employment distinction'
            elif col_idx in range(30, 35):
                first_category = 'Reasons for the part-time work'
            elif col_idx in range(35, 40):
                first_category = 'Permanency of the job (for employees)'
            elif col_idx in range(40, 44):
                first_category = 'Reasons for having a temporary job'
            elif col_idx in range(44, 56):
                first_category = 'Hours actually worked during reference week'
            elif col_idx in range(56, 62):
                first_category = 'Hours actually worked in reference week related to usual hours'
            elif col_idx in range(62, 74):
                first_category = 'Atypical work'
            else:
                first_category = 'Unknown'

            # Get the actual values from the rows
            subcategory = row1_subcategories.iloc[col_idx] if pd.notna(row1_subcategories.iloc[col_idx]) else '_Z'
            sub_subcategory = row2_subsubcategories.iloc[col_idx] if pd.notna(row2_subsubcategories.iloc[col_idx]) else '_Z'

            # Clean up the values
            if pd.notna(subcategory):
                subcategory = str(subcategory).strip()
            else:
                subcategory = '_Z'
                
            if pd.notna(sub_subcategory):
                sub_subcategory = str(sub_subcategory).strip()
            else:
                sub_subcategory = '_Z'

            # Create mapping entry
            mapping.append({
                'column': col_idx,
                'first_category': first_category,
                'subcategory': subcategory,
                'sub_subcategory': sub_subcategory
            })

            print(f"  Column {col_idx}: {first_category} -> {subcategory} -> {sub_subcategory}")

        print(f"Created mapping for {len(mapping)} columns")
        return mapping

    def _parse_data_with_correct_hierarchy(self, df: pd.DataFrame, column_mapping: List[Dict], analysis: Dict) -> pd.DataFrame:
        """
        Parse ALL data rows with correct hierarchy mapping
        JOB-Regio data starts from row 4 (not row 3 like JOB-SexAge)
        FOLLOWS JOB-SexAge: Captures ALL data including zeros for perfect data integrity!
        """
        print("Parsing ALL data rows with correct hierarchy...")

        # Start from row 4 (after the 3 header rows) - different from JOB-SexAge
        data_start_row = 4

        # Get all data rows
        data_rows = []

        # Process each row in the Excel data
        for row_idx in range(data_start_row, len(df)):
            row_data = df.iloc[row_idx]

            # Skip empty rows
            if pd.isna(row_data.iloc[0]) or str(row_data.iloc[0]).strip() == '':
                continue

            # Extract Year and Region (columns 0 and 1)
            year = row_data.iloc[0]
            region = row_data.iloc[1]

            # Skip if year or region is empty
            if pd.isna(year) or pd.isna(region):
                continue

            # Process each column mapping
            for col_info in column_mapping:
                col_idx = col_info['column']
                job_characteristic = col_info['first_category']
                job_subcategory = col_info['subcategory']
                job_sub_subcategory = col_info['sub_subcategory']

                # Get the value from this column
                value = row_data.iloc[col_idx]

                # Skip if value is empty (but NOT if it's 0 - we want ALL data like JOB-SexAge!)
                if pd.isna(value):
                    continue

                # Create record
                record = {
                    'Year': year,
                    'Region': region,
                    'Job_Characteristic': job_characteristic,
                    'Job_Subcategory': job_subcategory,
                    'Job_Sub_Subcategory': job_sub_subcategory,
                    'Value': value,
                    'Unit_of_Measure': 'persons'
                }

                data_rows.append(record)

        print(f"Extracted {len(data_rows)} data records from Excel")

        # Create DataFrame
        parsed_df = pd.DataFrame(data_rows)

        # Clean up - keep ALL data like JOB-SexAge (including zeros!)
        parsed_df = parsed_df.dropna(subset=['Value'])

        print(f"Final parsed data: {len(parsed_df)} records")

        return parsed_df

    def transform_to_sdmx_wide_format(self, df):
        """
        Transform the parsed data to SDMX wide format with proper column structure.
        Same logic as JOB-SexAge but adapted for Year + Region grouping.
        """
        print("Transforming to SDMX wide format...")

        print(f"Input data shape: {df.shape}")
        print(f"Input columns: {list(df.columns)}")

        # The parsed data already has the correct structure with these columns:
        # Year, Region, Job_Characteristic, Job_Subcategory, Job_Sub_Subcategory, Unit_of_Measure, Value

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
                'Region': row['Region']  # Different from JOB-SexAge which had Sex and Age_Group
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

    def _save_parsed_data(self, parsed_df: pd.DataFrame, wide_df: pd.DataFrame, analysis: Dict):
        """Save the parsed data to Excel files"""
        file_path = analysis['file_path']
        sheet_name = analysis['sheet_name']

        # Create output filename
        output_filename = f"lfs_{sheet_name.lower().replace('-', '_')}_parsed.xlsx"
        output_path = f"assets/prepared/{output_filename}"

        # Save both formats - WIDE FORMAT AS PRIMARY SHEET!
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            wide_df.to_excel(writer, sheet_name='Sheet1', index=False)  # Primary sheet with wide format
            parsed_df.to_excel(writer, sheet_name='Parsed_Data', index=False)  # Long format as secondary sheet

        print(f"Saved parsed data to: {output_path}")
        print(f"  - Parsed data: {len(parsed_df)} records")
        print(f"  - Wide format: {len(wide_df)} records")
