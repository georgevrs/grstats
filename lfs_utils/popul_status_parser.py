"""
POPUL-Status Sheet Parser
Specialized parser for the POPUL-Status sheet with employment status hierarchy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class POPULStatusParser:
    """Specialized parser for POPUL-Status sheet with employment status hierarchy"""
    
    def __init__(self):
        self.dimensions = {}
        self.data_records = []
        
    def parse_sheet(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse POPUL-Status sheet into wide SDMX format
        
        Args:
            analysis: Result from AdvancedSheetAnalyzer
            
        Returns:
            DataFrame in wide SDMX format
        """
        try:
            logger.info(f"Parsing POPUL-Status sheet '{analysis['sheet_name']}' into SDMX format")
            
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
            logger.error(f"Error parsing POPUL-Status sheet: {e}")
            raise
    
    def _parse_data_structure(self, data_rows: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the data structure into individual records"""
        records = []
        
        # Get the header structure
        headers = self._extract_headers(analysis)
        
        # Process each data row
        for row_idx, row in data_rows.iterrows():
            # Each row represents a Year+Employment_Status combination
            # We need to create multiple records for different breakdowns
            row_records = self._parse_data_row_breakdowns(row, headers, analysis)
            records.extend(row_records)
        
        return records
    
    def _extract_headers(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract header information from the analysis"""
        headers = {
            'year_col': 0,  # Year is always in column 0
            'employment_status_col': 1,  # Employment status is in column 1
            'total_pop_col': 2,  # Total population aged 15+ is in column 2
            'column_mapping': self._create_column_mapping(analysis)
        }
        
        return headers
    
    def _create_column_mapping(self, analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Create mapping of columns to their categories"""
        mapping = {
            'sex': [],           # Sex breakdown (Males, Females)
            'age': [],           # Age groups
            'marital': [],       # Marital status
            'nationality': [],   # Nationality
            'urbanization': []   # Urbanization areas
        }
        
        # Get the header rows from the analysis
        df = analysis['raw_dataframe']
        if len(df) > 1:
            row1 = df.iloc[1]  # Row 1: Sub-categories
            
            # Map Sex breakdown (columns 3-4)
            sex_columns = [3, 4]
            sex_names = ['Males', 'Females']
            for col_idx, sex_name in zip(sex_columns, sex_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['sex'].append({
                        'column': col_idx,
                        'sex': sex_name
                    })
            
            # Map Age groups (columns 5-11)
            age_columns = [5, 6, 7, 8, 9, 10, 11]
            age_names = ['14', '15-19', '20-24', '25-29', '30-44', '45-64', '65+']
            for col_idx, age_name in zip(age_columns, age_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['age'].append({
                        'column': col_idx,
                        'age_group': age_name
                    })
            
            # Map Marital status (columns 12-14)
            marital_columns = [12, 13, 14]
            marital_names = ['Single', 'Married', 'Widowed, divorced          or legally separated']
            for col_idx, marital_name in zip(marital_columns, marital_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['marital'].append({
                        'column': col_idx,
                        'marital_status': marital_name
                    })
            
            # Map Nationality (columns 15-17)
            nationality_columns = [15, 16, 17]
            nationality_names = ['Greek', 'EU country', 'Other']
            for col_idx, nat_name in zip(nationality_columns, nationality_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['nationality'].append({
                        'column': col_idx,
                        'nationality': nat_name
                    })
            
            # Map Urbanization (columns 18-22)
            urbanization_columns = [18, 19, 20, 21, 22]
            urbanization_names = ['Athens agglomeration', 'Thessaloniki agglomeration', 'Other urban areas', 'Semi-urban areas', 'Rural areas']
            for col_idx, urban_name in zip(urbanization_columns, urbanization_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['urbanization'].append({
                        'column': col_idx,
                        'urbanization': urban_name
                    })
        
        return mapping
    
    def _parse_data_row_breakdowns(self, row: pd.Series, headers: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a single data row into multiple records for different breakdowns"""
        records = []
        
        # Extract basic identifiers
        year = row.iloc[headers['year_col']]
        employment_status = row.iloc[headers['employment_status_col']]
        total_pop = row.iloc[headers['total_pop_col']]
        
        if pd.isna(year) or pd.isna(employment_status):
            return records
        
        year_str = str(year)
        employment_status_str = str(employment_status).strip()
        
        # Determine main employment status and sub-category
        main_status, sub_status = self._parse_employment_status(employment_status_str)
        
        # Create records for each breakdown
        column_mapping = headers['column_mapping']
        
        # 0. TOTAL POPULATION (Total population aged 15+)
        if pd.notna(total_pop) and self._is_numeric(str(total_pop)):
            total_pop_record = self._create_base_record(year_str, main_status, sub_status)
            total_pop_record['Sex'] = '_Z'
            total_pop_record['Age_Group'] = '_Z'
            total_pop_record['Marital_Status'] = '_Z'
            total_pop_record['Nationality'] = '_Z'
            total_pop_record['Urbanization'] = '_Z'
            total_pop_record['Value'] = float(total_pop)
            records.append(total_pop_record)
        
        # 1. Sex breakdown
        for sex_info in column_mapping['sex']:
            value = row.iloc[sex_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, main_status, sub_status)
                record['Sex'] = sex_info['sex']
                record['Age_Group'] = '_Z'
                record['Marital_Status'] = '_Z'
                record['Nationality'] = '_Z'
                record['Urbanization'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 2. Age group breakdown
        for age_info in column_mapping['age']:
            value = row.iloc[age_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, main_status, sub_status)
                record['Sex'] = '_Z'
                record['Age_Group'] = age_info['age_group']
                record['Marital_Status'] = '_Z'
                record['Nationality'] = '_Z'
                record['Urbanization'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 3. Marital status breakdown
        for marital_info in column_mapping['marital']:
            value = row.iloc[marital_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, main_status, sub_status)
                record['Sex'] = '_Z'
                record['Age_Group'] = '_Z'
                record['Marital_Status'] = marital_info['marital_status']
                record['Nationality'] = '_Z'
                record['Urbanization'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 4. Nationality breakdown
        for nat_info in column_mapping['nationality']:
            value = row.iloc[nat_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, main_status, sub_status)
                record['Sex'] = '_Z'
                record['Age_Group'] = '_Z'
                record['Marital_Status'] = '_Z'
                record['Nationality'] = nat_info['nationality']
                record['Urbanization'] = '_Z'
                record['Value'] = float(value)
                records.append(record)
        
        # 5. Urbanization breakdown
        for urban_info in column_mapping['urbanization']:
            value = row.iloc[urban_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record = self._create_base_record(year_str, main_status, sub_status)
                record['Sex'] = '_Z'
                record['Age_Group'] = '_Z'
                record['Marital_Status'] = '_Z'
                record['Nationality'] = '_Z'
                record['Urbanization'] = urban_info['urbanization']
                record['Value'] = float(value)
                records.append(record)
        
        return records
    
    def _parse_employment_status(self, status_str: str) -> Tuple[str, str]:
        """
        Parse employment status string to extract main status and sub-category
        
        Args:
            status_str: Employment status string from the data
            
        Returns:
            Tuple of (main_status, sub_status)
        """
        status_str = status_str.strip()
        
        # Handle main employment statuses
        if status_str == 'Employed':
            return 'Employed', 'Total'
        elif status_str == 'Unemployed':
            return 'Unemployed', 'Total'
        elif status_str == 'Inactive':
            return 'Inactive', 'Total'
        elif status_str == 'TOTAL POPULATION AGED 15+':
            return 'TOTAL POPULATION AGED 15+', 'Total'
        
        # Handle sub-categories
        if status_str.startswith('- '):
            # Sub-category of Employed
            sub_status = status_str[2:]  # Remove "- "
            return 'Employed', sub_status
        elif status_str.startswith('-- '):
            # Sub-sub-category (e.g., "-- Permanent job")
            sub_sub_status = status_str[3:]  # Remove "-- "
            return 'Employed', sub_sub_status
        
        # Default case
        return status_str, 'Total'
    
    def _create_base_record(self, year: str, main_employment_status: str, sub_employment_status: str) -> Dict[str, Any]:
        """Create a base record with common dimensions"""
        return {
            'Year': year,
            'Main_Employment_Status': main_employment_status,
            'Sub_Employment_Status': sub_employment_status
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
        logger.info("Creating SDMX template for POPUL-Status with all dimensions")
        
        # Create template records
        template_records = []
        
        # Get data structure
        data_struct = analysis['data_structure']
        if data_struct['data_start_row'] is not None:
            df = analysis['raw_dataframe']
            data_rows = df.iloc[data_struct['data_start_row']:data_struct['data_end_row']+1]
            
            # Extract unique values for each dimension
            year_values = data_rows.iloc[:, 0].dropna().unique()
            
            # Define all possible dimension values
            main_employment_statuses = ['Employed', 'Unemployed', 'Inactive', 'TOTAL POPULATION AGED 15+']
            sub_employment_statuses = ['Total', 'Self employed', 'Family workers', 'Employees', 'Permanent job', 'Temporary job', 'Full-time employed', 'Part-time employed', 'New unemployed', 'Long-term unemployed']
            sex_values = ['Males', 'Females']
            age_groups = ['14', '15-19', '20-24', '25-29', '30-44', '45-64', '65+']
            marital_values = ['Single', 'Married', 'Widowed, divorced          or legally separated']
            nationality_values = ['Greek', 'EU country', 'Other']
            urbanization_values = ['Athens agglomeration', 'Thessaloniki agglomeration', 'Other urban areas', 'Semi-urban areas', 'Rural areas']
            
            # Create template records for all combinations
            for year in year_values:
                for main_status in main_employment_statuses:
                    for sub_status in sub_employment_statuses:
                        # Add total population record
                        record = self._create_template_record(year, main_status, sub_status, '_Z', '_Z', '_Z', '_Z', '_Z')
                        template_records.append(record)
                        
                        # Add sex breakdown
                        for sex in sex_values:
                            record = self._create_template_record(year, main_status, sub_status, sex, '_Z', '_Z', '_Z', '_Z')
                            template_records.append(record)
                        
                        # Add age group breakdown
                        for age in age_groups:
                            record = self._create_template_record(year, main_status, sub_status, '_Z', age, '_Z', '_Z', '_Z')
                            template_records.append(record)
                        
                        # Add marital status breakdown
                        for marital in marital_values:
                            record = self._create_template_record(year, main_status, sub_status, '_Z', '_Z', marital, '_Z', '_Z')
                            template_records.append(record)
                        
                        # Add nationality breakdown
                        for nationality in nationality_values:
                            record = self._create_template_record(year, main_status, sub_status, '_Z', '_Z', '_Z', nationality, '_Z')
                            template_records.append(record)
                        
                        # Add urbanization breakdown
                        for urbanization in urbanization_values:
                            record = self._create_template_record(year, main_status, sub_status, '_Z', '_Z', '_Z', '_Z', urbanization)
                            template_records.append(record)
        
        return pd.DataFrame(template_records)
    
    def _create_template_record(self, year: str, main_employment_status: str, sub_employment_status: str, 
                              sex: str, age_group: str, marital_status: str, nationality: str, urbanization: str) -> Dict[str, Any]:
        """Create a template record with specified dimensions"""
        return {
            'Year': str(year),
            'Main_Employment_Status': main_employment_status,
            'Sub_Employment_Status': sub_employment_status,
            'Sex': sex,
            'Age_Group': age_group,
            'Marital_Status': marital_status,
            'Nationality': nationality,
            'Urbanization': urbanization,
            'Value': '_Z'
        }
    
    def print_parsing_summary(self, df: pd.DataFrame, analysis: Dict[str, Any]):
        """Print a summary of the parsing results"""
        print(f"\n{'='*80}")
        print(f"POPUL-STATUS DATA PARSING SUMMARY")
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
        if 'Main_Employment_Status' in df.columns:
            print(f"  Main Employment Status breakdown:")
            for status in df['Main_Employment_Status'].unique():
                count = len(df[df['Main_Employment_Status'] == status])
                print(f"    {status}: {count} records")
        
        if 'Sub_Employment_Status' in df.columns:
            print(f"  Sub Employment Status breakdown:")
            for status in df['Sub_Employment_Status'].unique():
                if status != '_Z':
                    count = len(df[df['Sub_Employment_Status'] == status])
                    print(f"    {status}: {count} records")
        
        if 'Sex' in df.columns:
            print(f"  Sex breakdown:")
            for sex in df['Sex'].unique():
                if sex != '_Z':
                    count = len(df[df['Sex'] == sex])
                    print(f"    {sex}: {count} records")
        
        if 'Age_Group' in df.columns:
            print(f"  Age group breakdown:")
            for age in df['Age_Group'].unique():
                if age != '_Z':
                    count = len(df[df['Age_Group'] == age])
                    print(f"    {age}: {count} records")
        
        if 'Marital_Status' in df.columns:
            print(f"  Marital status breakdown:")
            for marital in df['Marital_Status'].unique():
                if marital != '_Z':
                    count = len(df[df['Marital_Status'] == marital])
                    print(f"    {marital}: {count} records")
        
        if 'Nationality' in df.columns:
            print(f"  Nationality breakdown:")
            for nat in df['Nationality'].unique():
                if nat != '_Z':
                    count = len(df[df['Nationality'] == nat])
                    print(f"    {nat}: {count} records")
        
        if 'Urbanization' in df.columns:
            print(f"  Urbanization breakdown:")
            for urban in df['Urbanization'].unique():
                if urban != '_Z':
                    count = len(df[df['Urbanization'] == urban])
                    print(f"    {urban}: {count} records")
        
        print(f"\nSample data:")
        print(df.head(10).to_string())
        
        print(f"{'='*80}\n")
