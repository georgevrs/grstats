"""
STATUS-SexAge Sheet Parser
Specialized parser for the STATUS-SexAge sheet with employment status hierarchy and multiple units of measure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STATUSSexAgeParser:
    """Specialized parser for STATUS-SexAge sheet with employment status hierarchy and multiple units of measure"""
    
    def __init__(self):
        self.dimensions = {}
        self.data_records = []
        
    def parse_sheet(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse STATUS-SexAge sheet into wide SDMX format
        
        Args:
            analysis: Result from AdvancedSheetAnalyzer
            
        Returns:
            DataFrame in wide SDMX format
        """
        try:
            logger.info(f"Parsing STATUS-SexAge sheet '{analysis['sheet_name']}' into SDMX format")
            
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
            logger.error(f"Error parsing STATUS-SexAge sheet: {e}")
            raise
    
    def _parse_data_structure(self, data_rows: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the data structure into individual records"""
        records = []
        
        # Get the header structure
        headers = self._extract_headers(analysis)
        
        # Process each data row
        for row_idx, row in data_rows.iterrows():
            # Each row represents a Year+Sex+Age combination
            # We need to create multiple records for different breakdowns
            row_records = self._parse_data_row_breakdowns(row, headers, analysis)
            records.extend(row_records)
        
        return records
    
    def _extract_headers(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract header information from the analysis"""
        headers = {
            'year_col': 0,  # Year is always in column 0
            'sex_col': 1,   # Sex is in column 1
            'age_col': 2,   # Age group is in column 2
            'total_pop_col': 3,  # Total population aged 15+ is in column 3
            'column_mapping': self._create_column_mapping(analysis)
        }
        
        return headers
    
    def _create_column_mapping(self, analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Create mapping of columns to their categories"""
        mapping = {
            'labour_force': [],      # Labour Force breakdown
            'employed': [],          # Employed breakdown
            'unemployed': [],        # Unemployed breakdown
            'inactive': [],          # Inactive breakdown
            'inactive_reasons': []   # Reasons for not seeking employment
        }
        
        # Get the header rows from the analysis
        df = analysis['raw_dataframe']
        if len(df) > 2:
            row1 = df.iloc[1]  # Row 1: Main categories
            row2 = df.iloc[2]  # Row 2: Sub-categories
            
            # Map Labour Force (columns 4-6)
            labour_force_columns = [4, 5, 6]
            labour_force_names = ['persons', 'activity rate', '% aged 20-64']
            for col_idx, name in zip(labour_force_columns, labour_force_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['labour_force'].append({
                        'column': col_idx,
                        'category': name,
                        'unit': self._get_unit_of_measure(name)
                    })
            
            # Map Employed (columns 7-12)
            employed_columns = [7, 8, 9, 10, 11, 12]
            employed_names = ['persons', 'employment rate', '% aged 20-64', 'Employed, not undermployed', 'Undermployed part-time workers', 'persons']
            for col_idx, name in zip(employed_columns, employed_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['employed'].append({
                        'column': col_idx,
                        'category': name,
                        'unit': self._get_unit_of_measure(name)
                    })
            
            # Map Unemployed (columns 13-15)
            unemployed_columns = [13, 14, 15]
            unemployed_names = ['unemployment rate', '% aged 20-64', 'persons']
            for col_idx, name in zip(unemployed_columns, unemployed_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['unemployed'].append({
                        'column': col_idx,
                        'category': name,
                        'unit': self._get_unit_of_measure(name)
                    })
            
            # Map Inactive (columns 16-18)
            inactive_columns = [16, 17, 18]
            inactive_names = ['persons', '"% aged 15+\n(1981-97: 14+)"', '% aged 20-64']
            for col_idx, name in zip(inactive_columns, inactive_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['inactive'].append({
                        'column': col_idx,
                        'category': name,
                        'unit': self._get_unit_of_measure(name)
                    })
            
            # Map Inactive Reasons (columns 19-25)
            inactive_reason_columns = [19, 20, 21, 22, 23, 24, 25]
            inactive_reason_names = [
                'Seeking work but not immediately available',
                'Available to work but not seeking',
                'Other inactive',
                'Personal or family responsibilities',
                'Education or training',
                'Own ilness or disability',
                'Retirement',
                'Other reasons'
            ]
            for col_idx, name in zip(inactive_reason_columns, inactive_reason_names):
                if col_idx < len(row2) and pd.notna(row2.iloc[col_idx]):
                    mapping['inactive_reasons'].append({
                        'column': col_idx,
                        'category': name,
                        'unit': 'persons'  # All inactive reasons are in persons
                    })
        
        # If no mappings were created, create them manually based on the debug output
        if not any(mapping.values()):
            # Labour Force (columns 4-6)
            mapping['labour_force'] = [
                {'column': 4, 'category': 'persons', 'unit': 'persons'},
                {'column': 5, 'category': 'activity rate', 'unit': 'percentage'},
                {'column': 6, 'category': '% aged 20-64', 'unit': 'percentage'}
            ]
            
            # Employed (columns 7-12)
            mapping['employed'] = [
                {'column': 7, 'category': 'persons', 'unit': 'persons'},
                {'column': 8, 'category': 'employment rate', 'unit': 'percentage'},
                {'column': 9, 'category': '% aged 20-64', 'unit': 'percentage'},
                {'column': 10, 'category': 'Employed, not undermployed', 'unit': 'persons'},
                {'column': 11, 'category': 'Undermployed part-time workers', 'unit': 'persons'},
                {'column': 12, 'category': 'persons', 'unit': 'persons'}
            ]
            
            # Unemployed (columns 13-15)
            mapping['unemployed'] = [
                {'column': 13, 'category': 'unemployment rate', 'unit': 'percentage'},
                {'column': 14, 'category': '% aged 20-64', 'unit': 'percentage'},
                {'column': 15, 'category': 'persons', 'unit': 'persons'}
            ]
            
            # Inactive (columns 16-18)
            mapping['inactive'] = [
                {'column': 16, 'category': 'persons', 'unit': 'persons'},
                {'column': 17, 'category': '"% aged 15+\n(1981-97: 14+)"', 'unit': 'percentage'},
                {'column': 18, 'category': '% aged 20-64', 'unit': 'percentage'}
            ]
            
            # Inactive Reasons (columns 19-25)
            mapping['inactive_reasons'] = [
                {'column': 19, 'category': 'Seeking work but not immediately available', 'unit': 'persons'},
                {'column': 20, 'category': 'Available to work but not seeking', 'unit': 'persons'},
                {'column': 21, 'category': 'Other inactive', 'unit': 'persons'},
                {'column': 22, 'category': 'Personal or family responsibilities', 'unit': 'persons'},
                {'column': 23, 'category': 'Education or training', 'unit': 'persons'},
                {'column': 24, 'category': 'Own ilness or disability', 'unit': 'persons'},
                {'column': 25, 'category': 'Retirement', 'unit': 'persons'}
            ]
        
        return mapping
    
    def _get_unit_of_measure(self, category_name: str) -> str:
        """Determine the unit of measure for a given category"""
        if 'rate' in category_name.lower() or '%' in category_name:
            return 'percentage'
        elif 'persons' in category_name.lower():
            return 'persons'
        else:
            return 'persons'  # Default to persons
    
    def _parse_data_row_breakdowns(self, row: pd.Series, headers: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a single data row into multiple records for different breakdowns"""
        records = []
        
        # Extract basic identifiers
        year = row.iloc[headers['year_col']]
        sex = row.iloc[headers['sex_col']]
        age = row.iloc[headers['age_col']]
        total_pop = row.iloc[headers['total_pop_col']]
        
        if pd.isna(year) or pd.isna(sex) or pd.isna(age):
            return records
        
        year_str = str(year)
        sex_str = str(sex).strip()
        age_str = str(age).strip()
        
        # Create records for each breakdown
        column_mapping = headers['column_mapping']
        
        # 0. TOTAL POPULATION (Total population aged 15+)
        if pd.notna(total_pop) and self._is_numeric(str(total_pop)):
            total_pop_record = self._create_base_record(year_str, sex_str, age_str)
            total_pop_record['Labour_Force_Status'] = 'Total Population'
            total_pop_record['Labour_Force_Subcategory'] = '_Z'
            total_pop_record['Unit_of_Measure'] = 'persons'
            total_pop_record['Value'] = float(total_pop)
            records.append(total_pop_record)
        
        # 1. Labour Force breakdown
        for lf_info in column_mapping['labour_force']:
            value = row.iloc[lf_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, sex_str, age_str)
                record['Labour_Force_Status'] = 'Labour Force'
                record['Labour_Force_Subcategory'] = lf_info['category']
                record['Unit_of_Measure'] = lf_info['unit']
                record['Value'] = float(value)
                records.append(record)
        
        # 2. Employed breakdown
        for emp_info in column_mapping['employed']:
            value = row.iloc[emp_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, sex_str, age_str)
                record['Labour_Force_Status'] = 'Employed'
                record['Labour_Force_Subcategory'] = emp_info['category']
                record['Unit_of_Measure'] = emp_info['unit']
                record['Value'] = float(value)
                records.append(record)
        
        # 3. Unemployed breakdown
        for unemp_info in column_mapping['unemployed']:
            value = row.iloc[unemp_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, sex_str, age_str)
                record['Labour_Force_Status'] = 'Unemployed'
                record['Labour_Force_Subcategory'] = unemp_info['category']
                record['Unit_of_Measure'] = unemp_info['unit']
                record['Value'] = float(value)
                records.append(record)
        
        # 4. Inactive breakdown
        for inactive_info in column_mapping['inactive']:
            value = row.iloc[inactive_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, sex_str, age_str)
                record['Labour_Force_Status'] = 'Inactive'
                record['Labour_Force_Subcategory'] = inactive_info['category']
                record['Unit_of_Measure'] = inactive_info['unit']
                record['Value'] = float(value)
                records.append(record)
        
        # 5. Inactive Reasons breakdown
        for reason_info in column_mapping['inactive_reasons']:
            value = row.iloc[reason_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, sex_str, age_str)
                record['Labour_Force_Status'] = 'Reasons for not seeking employment (inactive)'
                record['Labour_Force_Subcategory'] = reason_info['category']
                record['Unit_of_Measure'] = reason_info['unit']
                record['Value'] = float(value)
                records.append(record)
        
        return records
    
    def _create_base_record(self, year: str, sex: str, age: str) -> Dict[str, Any]:
        """Create a base record with common dimensions"""
        return {
            'Year': year,
            'Sex': sex,
            'Age_Group': age
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
        logger.info("Creating SDMX template for STATUS-SexAge with all dimensions")
        
        # Create template records
        template_records = []
        
        # Get data structure
        data_struct = analysis['data_structure']
        if data_struct['data_start_row'] is not None:
            df = analysis['raw_dataframe']
            data_rows = df.iloc[data_struct['data_start_row']:data_struct['data_end_row']+1]
            
            # Extract unique values for each dimension
            year_values = data_rows.iloc[:, 0].dropna().unique()
            sex_values = data_rows.iloc[:, 1].dropna().unique()
            age_values = data_rows.iloc[:, 2].dropna().unique()
            
            # Define all possible dimension values
            labour_force_statuses = [
                'Total Population',
                'Labour Force',
                'Employed',
                'Unemployed',
                'Inactive',
                'Reasons for not seeking employment (inactive)'
            ]
            
            labour_force_subcategories = [
                # Labour Force
                'persons', 'activity rate', '% aged 20-64',
                # Employed
                'persons', 'employment rate', '% aged 20-64', 'Employed, not undermployed', 'Undermployed part-time workers',
                # Unemployed
                'unemployment rate', '% aged 20-64', 'persons',
                # Inactive
                'persons', '"% aged 15+\n(1981-97: 14+)"', '% aged 20-64',
                # Inactive Reasons
                'Seeking work but not immediately available', 'Available to work but not seeking', 'Other inactive',
                'Personal or family responsibilities', 'Education or training', 'Own ilness or disability', 'Retirement', 'Other reasons'
            ]
            
            units_of_measure = ['persons', 'percentage']
            
            # Create template records for all combinations
            for year in year_values:
                for sex in sex_values:
                    for age in age_values:
                        # Add total population record
                        record = self._create_template_record(
                            year, sex, age, 'Total Population', '_Z', 'persons'
                        )
                        template_records.append(record)
                        
                        # Add labour force status breakdowns
                        for status in labour_force_statuses:
                            if status != 'Total Population':
                                for subcategory in labour_force_subcategories:
                                    # Determine appropriate unit for this subcategory
                                    unit = self._get_unit_of_measure(subcategory)
                                    record = self._create_template_record(
                                        year, sex, age, status, subcategory, unit
                                    )
                                    template_records.append(record)
        
        return pd.DataFrame(template_records)
    
    def _create_template_record(self, year: str, sex: str, age: str,
                              labour_force_status: str, labour_force_subcategory: str,
                              unit_of_measure: str) -> Dict[str, Any]:
        """Create a template record with specified dimensions"""
        return {
            'Year': str(year),
            'Sex': sex,
            'Age_Group': age,
            'Labour_Force_Status': labour_force_status,
            'Labour_Force_Subcategory': labour_force_subcategory,
            'Unit_of_Measure': unit_of_measure,
            'Value': '_Z'
        }
    
    def print_parsing_summary(self, df: pd.DataFrame, analysis: Dict[str, Any]):
        """Print a summary of the parsing results"""
        print(f"\n{'='*80}")
        print(f"STATUS-SEXAGE DATA PARSING SUMMARY")
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
        if 'Sex' in df.columns:
            print(f"  Sex breakdown:")
            for sex in df['Sex'].unique():
                if sex != '_Z':
                    count = len(df[df['Sex'] == sex])
                    print(f"    {sex}: {count} records")
        
        if 'Age_Group' in df.columns:
            print(f"  Age Group breakdown:")
            for age in df['Age_Group'].unique():
                if age != '_Z':
                    count = len(df[df['Age_Group'] == age])
                    print(f"    {age}: {count} records")
        
        if 'Labour_Force_Status' in df.columns:
            print(f"  Labour Force Status breakdown:")
            for status in df['Labour_Force_Status'].unique():
                if status != '_Z':
                    count = len(df[df['Labour_Force_Status'] == status])
                    print(f"    {status}: {count} records")
        
        if 'Labour_Force_Subcategory' in df.columns:
            print(f"  Labour Force Subcategory breakdown:")
            for subcat in df['Labour_Force_Subcategory'].unique():
                if subcat != '_Z':
                    count = len(df[df['Labour_Force_Subcategory'] == subcat])
                    print(f"    {subcat}: {count} records")
        
        if 'Unit_of_Measure' in df.columns:
            print(f"  Unit of Measure breakdown:")
            for unit in df['Unit_of_Measure'].unique():
                if unit != '_Z':
                    count = len(df[df['Unit_of_Measure'] == unit])
                    print(f"    {unit}: {count} records")
        
        print(f"\nSample data:")
        print(df.head(10).to_string())
        
        print(f"{'='*80}\n")
