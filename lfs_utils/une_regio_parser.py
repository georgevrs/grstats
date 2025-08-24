"""
UNE-Regio Parser

Specialized parser for the UNE-Regio sheet from File 03.
This sheet has the same structure as JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge but groups by Region with unemployment characteristics.

Structure:
- ROW 0: Unemployment characteristics (Total Unemployed, Duration of unemployment, New unemployed, Professional status, Reason for leaving, Sector, Occupation, Type of employment sought, Situation before seeking employment, Education level)
- ROW 1: Subcategories (specific time periods, statuses, reasons, sectors, etc.)
- ROW 2: Sub-subcategories (specific codes and detailed breakdowns)
- DATA: Organized by Year + Region (NUTS II regions)

FOLLOWS THE PERFECT RATIONAL FROM JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge: Uses column range segmentation for perfect category mapping!
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple
from advanced_sheet_analyzer import AdvancedSheetAnalyzer

class UNERegioParser:
    """
    Parser for UNE-Regio sheet with unemployment characteristics organization.
    Uses the same parsing logic as JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge but adapted for unemployment characteristics grouping.
    FOLLOWS THE PERFECT RATIONAL: Column range segmentation for perfect category mapping!
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzer = AdvancedSheetAnalyzer()

    def parse_sheet(self, analysis: Dict) -> pd.DataFrame:
        """
        Parse the UNE-Regio sheet into SDMX wide format

        Args:
            analysis: Dictionary containing file_path and sheet_name

        Returns:
            DataFrame in SDMX wide format
        """
        file_path = analysis['file_path']
        sheet_name = analysis['sheet_name']

        self.logger.info(f"Starting UNE-Regio parsing for {sheet_name}")

        # Analyze the sheet structure
        print(f"Analyzing sheet structure for {sheet_name}...")
        sheet_analysis = self.analyzer.analyze_sheet(file_path, sheet_name)

        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # Extract the three levels correctly (same as JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge)
        row0_categories = df.iloc[0]
        row1_subcategories = df.iloc[1]
        row2_subsubcategories = df.iloc[2]

        # Create column mapping (same logic as JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge)
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

        self.logger.info(f"UNE-Regio parsing completed: {len(parsed_df)} records, wide format: {len(wide_df)} records")
        return wide_df  # Return wide format as primary output

    def _create_correct_column_mapping(self, row0_categories: pd.Series,
                                             row1_subcategories: pd.Series,
                                             row2_subsubcategories: pd.Series) -> List[Dict]:
        """
        Create CORRECT column mapping based on the actual Excel structure
        UNE-Regio has headers spread across columns, not continuous like JOB-SexAge
        FOLLOW THE PERFECT RATIONAL FROM JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge: USE COLUMN RANGES TO SEGMENT CATEGORIES!
        
        This is the CLEVER TRICK: We use column position ranges to determine the first category,
        exactly like JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge do, ensuring perfect category segmentation!
        """
        mapping = []

        print("Creating column mapping for ALL 47 columns using JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge CLEVER TRICK...")

        # Map each column based on the three-level hierarchy
        # FOLLOW JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge: USE COLUMN RANGES TO DETERMINE FIRST CATEGORY!

        # Use the EXACT column count from our analysis: 47 columns
        total_columns = 47
        
        for col_idx in range(total_columns):
            # Skip Year and Region columns (0, 1) - these are in row 2
            if col_idx in [0, 1]:
                continue

            # FOLLOW JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge CLEVER TRICK: Determine first category based on column position
            first_category = self._determine_category_by_position(col_idx, row0_categories)

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

    def _determine_category_by_position(self, col_idx: int, row0_categories: pd.Series) -> str:
        """
        Determine the first category based on column position using the CLEVER TRICK
        Based on actual Excel structure analysis - EXACT SAME LOGIC AS JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge!
        """
        # FOLLOW JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge CLEVER TRICK: Use column position ranges to determine category
        
        # Based on the debug analysis, here are the EXACT column ranges:
        if col_idx == 2:
            return 'Total Unemployed'
        elif col_idx in range(3, 7):
            return 'Duration of unemployment'
        elif col_idx == 7:
            return 'New unemployed (no previous employment experience)'
        elif col_idx == 8:
            return 'Worked in last 8 years'
        elif col_idx in range(9, 12):
            return 'Professional status in last job'
        elif col_idx in range(12, 15):
            return 'Reason for leaving last job or business'
        elif col_idx in range(15, 23):
            return 'Sector of economic activity of last job'
        elif col_idx in range(23, 28):
            return 'Type of occupation'
        elif col_idx in range(28, 32):
            return 'Type of employment sought (or found)'
        elif col_idx in range(32, 37):
            return 'Situation immediately before person started to seek employent'
        elif col_idx in range(37, 47):
            return 'E d u c a t I o n   l e v e l'
        else:
            # Fallback to actual value if exists
            if pd.notna(row0_categories.iloc[col_idx]):
                return str(row0_categories.iloc[col_idx]).strip()
            else:
                return 'Unknown'

    def _parse_data_with_correct_hierarchy(self, df: pd.DataFrame, column_mapping: List[Dict], analysis: Dict) -> pd.DataFrame:
        """
        Parse ALL data rows with correct hierarchy mapping
        UNE-Regio data starts from row 4 (after the 3 header rows)
        FOLLOWS JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge: Captures ALL data including zeros for perfect data integrity!
        """
        print("Parsing ALL data rows with correct hierarchy...")

        # Start from row 4 (after the 3 header rows) - same as JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge
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
                unemployment_characteristic = col_info['first_category']
                unemployment_subcategory = col_info['subcategory']
                unemployment_sub_subcategory = col_info['sub_subcategory']

                # Get the value from this column
                value = row_data.iloc[col_idx]

                # Skip if value is empty (but NOT if it's 0 - we want ALL data like JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge!)
                if pd.isna(value):
                    continue

                # Create record
                record = {
                    'Year': year,
                    'Region': region,
                    'Unemployment_Characteristic': unemployment_characteristic,
                    'Unemployment_Subcategory': unemployment_subcategory,
                    'Unemployment_Sub_Subcategory': unemployment_sub_subcategory,
                    'Value': value,
                    'Unit_of_Measure': 'persons'
                }

                data_rows.append(record)

        print(f"Extracted {len(data_rows)} data records from Excel")

        # Create DataFrame
        parsed_df = pd.DataFrame(data_rows)

        # Clean up - keep ALL data like JOB-SexAge/JOB-Regio/JOB-Occup/JOB-Sector/OCCUP-Demo/SECTOR-Demo/EMP-SexAge/EMP-Regio/UNE-SexAge (including zeros!)
        parsed_df = parsed_df.dropna(subset=['Value'])

        print(f"Final parsed data: {len(parsed_df)} records")

        return parsed_df

    def transform_to_sdmx_wide_format(self, df):
        """
        Transform the parsed data to SDMX wide format with proper column structure.
        Same logic as JOB-SexAge, JOB-Regio, JOB-Occup, JOB-Sector, OCCUP-Demo, SECTOR-Demo, EMP-SexAge, EMP-Regio, and UNE-SexAge but adapted for Year + Region grouping with unemployment characteristics.
        """
        print("Transforming to SDMX wide format...")

        print(f"Input data shape: {df.shape}")
        print(f"Input columns: {list(df.columns)}")

        # The parsed data already has the correct structure with these columns:
        # Year, Region, Unemployment_Characteristic, Unemployment_Subcategory, Unemployment_Sub_Subcategory, Unit_of_Measure, Value

        # We need to pivot this to wide format where:
        # - Unemployment_Characteristic becomes columns
        # - Unemployment_Subcategory becomes values in those columns
        # - Unemployment_Sub_Subcategory becomes _subcategory columns for two-level categories

        # First, identify which categories have sub-subcategories (two levels)
        two_level_categories = set()
        for category in df['Unemployment_Characteristic'].unique():
            category_data = df[df['Unemployment_Characteristic'] == category]
            has_subsubcategories = category_data['Unemployment_Sub_Subcategory'].notna().any() and \
                                 (category_data['Unemployment_Sub_Subcategory'] != '_Z').any()
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
                'Region': row['Region']  # Different from JOB-SexAge (Sex+Age), JOB-Regio (Region), JOB-Occup (Occupation), JOB-Sector (Sector), OCCUP-Demo (Occupation), SECTOR-Demo (Sector), EMP-SexAge (Sex+Age), EMP-Regio (Region), and UNE-SexAge (Sex+Age)
            }

            # Get the unemployment characteristic for this row
            une_char = row['Unemployment_Characteristic']
            une_sub = row['Unemployment_Subcategory']
            une_subsub = row['Unemployment_Sub_Subcategory']

            # Initialize all columns with _Z
            for category in df['Unemployment_Characteristic'].unique():
                if category in two_level_categories:
                    row_data[category] = '_Z'
                    row_data[f"{category}_subcategory"] = '_Z'
                else:
                    row_data[category] = '_Z'

            # Populate the specific unemployment characteristic for this row
            if une_char in two_level_categories:
                # TWO-LEVEL CATEGORY: Set both main and subcategory columns
                row_data[une_char] = une_sub if pd.notna(une_sub) and str(une_sub).strip() != '' else '_Z'
                row_data[f"{une_char}_subcategory"] = une_subsub if pd.notna(une_subsub) and str(une_subsub).strip() != '' else '_Z'
            else:
                # SINGLE-LEVEL CATEGORY: Set only main column
                row_data[une_char] = une_sub if pd.notna(une_sub) and str(une_sub).strip() != '' else '_Z'

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
            if isinstance(col, str) and 'Education level' in col:
                # Fix the "E d u c a t I o n   l e v e l" spacing issue
                wide_df[col] = wide_df[col].astype(str).str.replace('E d u c a t I o n   l e v e l', 'Education level')

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
