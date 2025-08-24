"""
EDUC-Regio Sheet Parser
Specialized parser for the EDUC-Regio sheet with education level structure organized by region
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EDUCRegioParser:
    """Specialized parser for EDUC-Regio sheet with education level structure organized by region"""
    
    def __init__(self):
        self.dimensions = {}
        self.data_records = []
        
    def parse_sheet(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse EDUC-Regio sheet into wide SDMX format
        
        Args:
            analysis: Result from AdvancedSheetAnalyzer
            
        Returns:
            DataFrame in wide SDMX format
        """
        try:
            logger.info(f"Parsing EDUC-Regio sheet '{analysis['sheet_name']}' into SDMX format")
            
            df = analysis['raw_dataframe']
            data_struct = analysis['data_structure']
            
            # Extract the actual data rows
            data_rows = df.iloc[data_struct['data_start_row']:data_struct['data_end_row']+1]
            
            # Parse the data structure
            parsed_data = self._parse_data_structure(data_rows, analysis)
            
            # Convert to DataFrame
            result_df = pd.DataFrame(parsed_data)
            
            logger.info(f"Parsing complete. Created {len(result_df)} records with {len(result_df.columns)} columns")
            return result_df
            
        except Exception as e:
            logger.error(f"Error parsing EDUC-Regio sheet: {e}")
            raise
    
    def _parse_data_structure(self, data_rows: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the data structure into individual records"""
        records = []
        
        # Get the header structure
        headers = self._extract_headers(analysis)
        
        # Process each data row
        for row_idx, row in data_rows.iterrows():
            # Each row represents a Year+Region combination
            # We need to create multiple records for different breakdowns
            row_records = self._parse_data_row_breakdowns(row, headers, analysis)
            records.extend(row_records)
        
        return records
    
    def _extract_headers(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract header information from the analysis"""
        headers = {
            'year_col': 0,  # Year is always in column 0
            'region_col': 1,  # Region is in column 1
            'total_pop_col': 2,  # Total population aged 15+ is in column 2
            'column_mapping': self._create_column_mapping(analysis)
        }
        
        return headers
    
    def _create_column_mapping(self, analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Create mapping of columns to their categories"""
        mapping = {
            'education_level': [],      # Education level breakdown
            'formal_informal': [],      # Formal/informal education breakdown
            'neet': [],                # NEET breakdown
            'tertiary_30_34': [],      # Tertiary attainment 30-34
            'lifelong_20_64': []      # Lifelong learning 20-64
        }
        
        # Get the header rows from the analysis
        df = analysis['raw_dataframe']
        if len(df) > 2:
            row1 = df.iloc[1]  # Row 1: Sub-categories
            row2 = df.iloc[2]  # Row 2: Sub-sub-categories
            
            # Map Education Level (columns 3-12)
            # Main categories from row 1
            education_main_categories = [
                'Attended no school / Did not complete primary education',
                'Primary',
                'Lower secondary',
                'Upper secondary & post secondary',
                'Tertiary',
                'Postgraduate degrees (including integrated Master\'s degrees)'
            ]
            
            # Sub-categories from row 2
            education_sub_categories = [
                'ekp1', 'ekp2', 'ekp3', 'ekp4', 'Upper secondary', 
                'Post secondary vocational', 'ekp7', 'University degree', 
                'Postgraduate degrees (Μaster / PhD)'
            ]
            
            # Map education level columns (3-12)
            for col_idx in range(3, 13):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    sub_cat = str(row2.iloc[col_idx]).strip()
                    # Find which main category this belongs to
                    main_cat = self._find_education_main_category(col_idx, education_main_categories)
                    mapping['education_level'].append({
                        'column': col_idx,
                        'main_category': main_cat,
                        'sub_category': sub_cat
                    })
            
            # Map Formal/Informal Education (columns 13-18)
            formal_informal_columns = [13, 14, 15, 16, 17, 18]
            formal_informal_names = [
                'Total', 'in formal education', 'in informal education',
                'of them Employed', 'of them Unemployed', 'of them Inactive'
            ]
            for col_idx, name in zip(formal_informal_columns, formal_informal_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['formal_informal'].append({
                        'column': col_idx,
                        'category': name
                    })
            
            # Map NEET (columns 19-23)
            neet_columns = [19, 20, 21, 22, 23]
            neet_names = [
                'Total', 'Unemployed', 'Seek job but not available',
                'Like to work but not seek job', 'Other'
            ]
            for col_idx, name in zip(neet_columns, neet_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['neet'].append({
                        'column': col_idx,
                        'category': name
                    })
            
            # Map Tertiary attainment 30-34 (column 24)
            if 24 < len(row2) and pd.notna(row2.iloc[24]):
                mapping['tertiary_30_34'].append({
                    'column': 24,
                    'category': 'Tertiary educational attainment aged 30-34'
                })
            
            # Map Lifelong learning 20-64 (column 25)
            if 25 < len(row2) and pd.notna(row2.iloc[25]):
                mapping['lifelong_20_64'].append({
                    'column': 25,
                    'category': 'Lifelong learning aged 20-64'
                })
        
        return mapping
    
    def _find_education_main_category(self, col_idx: int, main_categories: List[str]) -> str:
        """Find which main education category a column belongs to"""
        # This is a simplified mapping based on column position
        # In a real implementation, you might need more sophisticated logic
        if col_idx == 3:
            return 'Attended no school / Did not complete primary education'
        elif col_idx == 4:
            return 'Primary'
        elif col_idx == 5:
            return 'Lower secondary'
        elif col_idx in [6, 7, 8]:
            return 'Upper secondary & post secondary'
        elif col_idx in [9, 10, 11]:
            return 'Tertiary'
        elif col_idx == 12:
            return 'Postgraduate degrees (including integrated Master\'s degrees)'
        else:
            return 'Unknown'
    
    def _parse_data_row_breakdowns(self, row: pd.Series, headers: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a single data row into multiple records for different breakdowns"""
        records = []
        
        # Extract basic identifiers
        year = row.iloc[headers['year_col']]
        region = row.iloc[headers['region_col']]
        total_pop = row.iloc[headers['total_pop_col']]
        
        if pd.isna(year) or pd.isna(region):
            return records
        
        year_str = str(year)
        region_str = str(region).strip()
        
        # Create records for each breakdown
        column_mapping = headers['column_mapping']
        
        # 0. TOTAL POPULATION (Total population aged 15+)
        if pd.notna(total_pop) and self._is_numeric(str(total_pop)):
            total_pop_record = self._create_base_record(year_str, region_str)
            total_pop_record['Education_Level_Main'] = '_Z'
            total_pop_record['Education_Level_Sub'] = '_Z'
            total_pop_record['Formal_Informal_Education'] = '_Z'
            total_pop_record['NEET_Category'] = '_Z'
            total_pop_record['Tertiary_30_34'] = '_Z'
            total_pop_record['Lifelong_20_64'] = '_Z'
            total_pop_record['Value'] = float(total_pop)
            records.append(total_pop_record)
        
        # 1. Education Level breakdown
        for edu_info in column_mapping['education_level']:
            value = row.iloc[edu_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, region_str)
                record['Education_Level_Main'] = edu_info['main_category']
                record['Education_Level_Sub'] = edu_info['sub_category']
                record['Formal_Informal_Education'] = '_Z'
                record['NEET_Category'] = '_Z'
                record['Tertiary_30_34'] = '_Z'
                record['Lifelong_20_64'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 2. Formal/Informal Education breakdown
        for formal_info in column_mapping['formal_informal']:
            value = row.iloc[formal_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, region_str)
                record['Education_Level_Main'] = '_Z'
                record['Education_Level_Sub'] = '_Z'
                record['Formal_Informal_Education'] = formal_info['category']
                record['NEET_Category'] = '_Z'
                record['Tertiary_30_34'] = '_Z'
                record['Lifelong_20_64'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 3. NEET breakdown
        for neet_info in column_mapping['neet']:
            value = row.iloc[neet_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, region_str)
                record['Education_Level_Main'] = '_Z'
                record['Education_Level_Sub'] = '_Z'
                record['Formal_Informal_Education'] = '_Z'
                record['NEET_Category'] = neet_info['category']
                record['Tertiary_30_34'] = '_Z'
                record['Lifelong_20_64'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 4. Tertiary attainment 30-34
        for tertiary_info in column_mapping['tertiary_30_34']:
            value = row.iloc[tertiary_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, region_str)
                record['Education_Level_Main'] = '_Z'
                record['Education_Level_Sub'] = '_Z'
                record['Formal_Informal_Education'] = '_Z'
                record['NEET_Category'] = '_Z'
                record['Tertiary_30_34'] = tertiary_info['category']
                record['Lifelong_20_64'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 5. Lifelong learning 20-64
        for lifelong_info in column_mapping['lifelong_20_64']:
            value = row.iloc[lifelong_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, region_str)
                record['Education_Level_Main'] = '_Z'
                record['Education_Level_Sub'] = '_Z'
                record['Formal_Informal_Education'] = '_Z'
                record['NEET_Category'] = '_Z'
                record['Tertiary_30_34'] = '_Z'
                record['Lifelong_20_64'] = lifelong_info['category']
                record['Value'] = float(value)
                records.append(record)
        
        return records
    
    def _create_base_record(self, year: str, region: str) -> Dict[str, Any]:
        """Create a base record with common dimensions"""
        return {
            'Year': year,
            'Region': region
        }
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def create_sdmx_template(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """Create a template DataFrame with all possible dimensions"""
        logger.info("Creating SDMX template for EDUC-Regio with all dimensions")
        
        # Create template records
        template_records = []
        
        # Get data structure
        data_struct = analysis['data_structure']
        if data_struct['data_start_row'] is not None:
            df = analysis['raw_dataframe']
            data_rows = df.iloc[data_struct['data_start_row']:data_struct['data_end_row']+1]
            
            # Extract unique values for each dimension
            year_values = data_rows.iloc[:, 0].dropna().unique()
            region_values = data_rows.iloc[:, 1].dropna().unique()
            
            # Define all possible dimension values
            education_main_levels = [
                'Attended no school / Did not complete primary education',
                'Primary', 'Lower secondary', 'Upper secondary & post secondary',
                'Tertiary', 'Postgraduate degrees (including integrated Master\'s degrees)'
            ]
            education_sub_levels = [
                'ekp1', 'ekp2', 'ekp3', 'ekp4', 'Upper secondary', 
                'Post secondary vocational', 'ekp7', 'University degree', 
                'Postgraduate degrees (Μaster / PhD)'
            ]
            formal_informal_values = [
                'Total', 'in formal education', 'in informal education',
                'of them Employed', 'of them Unemployed', 'of them Inactive'
            ]
            neet_values = [
                'Total', 'Unemployed', 'Seek job but not available',
                'Like to work but not seek job', 'Other'
            ]
            tertiary_30_34_values = ['Tertiary educational attainment aged 30-34']
            lifelong_20_64_values = ['Lifelong learning aged 20-64']
            
            # Create template records for all combinations
            for year in year_values:
                for region in region_values:
                    # Add total population record
                    record = self._create_template_record(
                        year, region, '_Z', '_Z', '_Z', '_Z', '_Z', '_Z'
                    )
                    template_records.append(record)
                    
                    # Add education level breakdowns
                    for main_level in education_main_levels:
                        for sub_level in education_sub_levels:
                            record = self._create_template_record(
                                year, region, main_level, sub_level, '_Z', '_Z', '_Z', '_Z'
                            )
                            template_records.append(record)
                    
                    # Add formal/informal education breakdowns
                    for formal_cat in formal_informal_values:
                        record = self._create_template_record(
                            year, region, '_Z', '_Z', formal_cat, '_Z', '_Z', '_Z'
                        )
                        template_records.append(record)
                    
                    # Add NEET breakdowns
                    for neet_cat in neet_values:
                        record = self._create_template_record(
                            year, region, '_Z', '_Z', '_Z', neet_cat, '_Z', '_Z'
                        )
                        template_records.append(record)
                    
                    # Add tertiary attainment 30-34
                    for tertiary_cat in tertiary_30_34_values:
                        record = self._create_template_record(
                            year, region, '_Z', '_Z', '_Z', '_Z', tertiary_cat, '_Z'
                        )
                        template_records.append(record)
                    
                    # Add lifelong learning 20-64
                    for lifelong_cat in lifelong_20_64_values:
                        record = self._create_template_record(
                            year, region, '_Z', '_Z', '_Z', '_Z', '_Z', lifelong_cat
                        )
                        template_records.append(record)
        
        return pd.DataFrame(template_records)
    
    def _create_template_record(self, year: str, region: str, 
                              education_main: str, education_sub: str, 
                              formal_informal: str, neet: str, 
                              tertiary_30_34: str, lifelong_20_64: str) -> Dict[str, Any]:
        """Create a template record with specified dimensions"""
        return {
            'Year': str(year),
            'Region': region,
            'Education_Level_Main': education_main,
            'Education_Level_Sub': education_sub,
            'Formal_Informal_Education': formal_informal,
            'NEET_Category': neet,
            'Tertiary_30_34': tertiary_30_34,
            'Lifelong_20_64': lifelong_20_64,
            'Value': '_Z'
        }
    
    def print_parsing_summary(self, df: pd.DataFrame, analysis: Dict[str, Any]):
        """Print a summary of the parsing results"""
        print(f"\n{'='*80}")
        print(f"EDUC-REGIO DATA PARSING SUMMARY")
        print(f"{'='*80}")
        print(f"Sheet: {analysis['sheet_name']}")
        print(f"Records created: {len(df)}")
        print(f"Columns created: {len(df.columns)}")
        
        print(f"\nColumn structure:")
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            unique_count = df[col].nunique()
            print(f"  - {col}: {non_null_count} non-null, {unique_count} unique values")
        
        print(f"\nDimension breakdown:")
        if 'Region' in df.columns:
            print(f"  Region breakdown:")
            for region in df['Region'].unique():
                count = len(df[df['Region'] == region])
                print(f"    {region}: {count} records")
        
        if 'Education_Level_Main' in df.columns:
            print(f"  Education Level Main breakdown:")
            for level in df['Education_Level_Main'].unique():
                if level != '_Z':
                    count = len(df[df['Education_Level_Main'] == level])
                    print(f"    {level}: {count} records")
        
        if 'Education_Level_Sub' in df.columns:
            print(f"  Education Level Sub breakdown:")
            for level in df['Education_Level_Sub'].unique():
                if level != '_Z':
                    count = len(df[df['Education_Level_Sub'] == level])
                    print(f"    {level}: {count} records")
        
        if 'Formal_Informal_Education' in df.columns:
            print(f"  Formal/Informal Education breakdown:")
            for cat in df['Formal_Informal_Education'].unique():
                if cat != '_Z':
                    count = len(df[df['Formal_Informal_Education'] == cat])
                    print(f"    {cat}: {count} records")
        
        if 'NEET_Category' in df.columns:
            print(f"  NEET Category breakdown:")
            for cat in df['NEET_Category'].unique():
                if cat != '_Z':
                    count = len(df[df['NEET_Category'] == cat])
                    print(f"    {cat}: {count} records")
        
        if 'Tertiary_30_34' in df.columns:
            print(f"  Tertiary 30-34 breakdown:")
            for cat in df['Tertiary_30_34'].unique():
                if cat != '_Z':
                    count = len(df[df['Tertiary_30_34'] == cat])
                    print(f"    {cat}: {count} records")
        
        if 'Lifelong_20_64' in df.columns:
            print(f"  Lifelong Learning 20-64 breakdown:")
            for cat in df['Lifelong_20_64'].unique():
                if cat != '_Z':
                    count = len(df[df['Lifelong_20_64'] == cat])
                    print(f"    {cat}: {count} records")
        
        print(f"\nSample data:")
        print(df.head(10).to_string())
        
        print(f"{'='*80}\n")
