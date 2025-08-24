"""
Data Parser for LFS Annual Datasets
Extracts data and creates wide SDMX-compliant format
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LFSDataParser:
    """Parses LFS data into wide SDMX-compliant format"""
    
    def __init__(self):
        self.dimensions = {}
        self.data_records = []
        
    def parse_sheet(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse a sheet analysis into wide SDMX format
        
        Args:
            analysis: Result from AdvancedSheetAnalyzer
            
        Returns:
            DataFrame in wide SDMX format
        """
        try:
            logger.info(f"Parsing sheet '{analysis['sheet_name']}' into SDMX format")
            
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
            logger.error(f"Error parsing sheet: {e}")
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
            'region_col': 1,  # Region is always in column 1
            'column_mapping': self._create_column_mapping(analysis)
        }
        
        return headers
    
    def _create_column_mapping(self, analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Create mapping of columns to their categories"""
        mapping = {
            'total': [],      # Total population by age
            'males': [],      # Males by age
            'females': [],    # Females by age
            'nationality': [], # Nationality breakdown
            'marital': []     # Marital status breakdown
        }
        
        # Get both header rows from the analysis
        df = analysis['raw_dataframe']
        if len(df) > 1:
            row0 = df.iloc[0]  # Row 0: Main categories
            row1 = df.iloc[1]  # Row 1: Sub-categories
            
            # Based on the debug analysis, the structure is:
            # - Col 0: Year (Population category)
            # - Col 1: Region (no main category)
            # - Col 2: Population total (no sub-category)
            # - Col 3-9: Total population by age groups
            # - Col 10: Males total
            # - Col 11-17: Males by age groups
            # - Col 18: Females total
            # - Col 19-25: Females by age groups
            # - Col 26-28: Nationality breakdown
            # - Col 29-31: Marital status breakdown
            
            # Map Total population by age (columns 3-9)
            for col_idx in range(3, 10):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    age_group = str(row1.iloc[col_idx]).strip()
                    if self._is_age_group(age_group):
                        mapping['total'].append({
                            'column': col_idx,
                            'age_group': age_group,
                            'category': 'total'
                        })
            
            # Map Males by age (columns 11-17)
            for col_idx in range(11, 18):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    age_group = str(row1.iloc[col_idx]).strip()
                    if self._is_age_group(age_group):
                        mapping['males'].append({
                            'column': col_idx,
                            'age_group': age_group,
                            'category': 'males'
                        })
            
            # Map Females by age (columns 19-25)
            for col_idx in range(19, 26):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    age_group = str(row1.iloc[col_idx]).strip()
                    if self._is_age_group(age_group):
                        mapping['females'].append({
                            'column': col_idx,
                            'age_group': age_group,
                            'category': 'females'
                        })
            
            # Map Nationality (columns 26-28)
            nationality_columns = [26, 27, 28]
            nationality_names = ['Greek', 'EU country', 'Other']
            for col_idx, nat_name in zip(nationality_columns, nationality_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['nationality'].append({
                        'column': col_idx,
                        'nationality': nat_name
                    })
            
            # Map Marital status (columns 29-31)
            marital_columns = [29, 30, 31]
            marital_names = ['Single', 'Married', 'Widowed, divorced      or legally separated']
            for col_idx, marital_name in zip(marital_columns, marital_names):
                if col_idx < len(row1) and pd.notna(row1.iloc[col_idx]):
                    mapping['marital'].append({
                        'column': col_idx,
                        'marital_status': marital_name
                    })
        
        return mapping
    
    def _find_main_category_for_column(self, col_idx: int, category_columns: Dict[str, List[int]], row0: pd.Series) -> str:
        """Find which main category a column belongs to by looking at the column span"""
        for main_cat, col_indices in category_columns.items():
            if col_idx in col_indices:
                return main_cat
        
        # If not found in exact mapping, try to find the closest category
        # This handles cases where the main category spans multiple columns
        for main_cat, col_indices in category_columns.items():
            if col_indices and col_idx >= min(col_indices) and col_idx <= max(col_indices):
                return main_cat
        
        return 'Unknown'
    
    def _determine_age_category(self, df: pd.DataFrame, col_idx: int) -> Optional[str]:
        """Determine which category (total, males, females) an age group column belongs to"""
        if len(df) > 0:
            # Look at row 0 to see which main category this column belongs to
            main_category = df.iloc[0, col_idx]
            if pd.notna(main_category):
                main_cat_str = str(main_category).strip()
                if main_cat_str == 'Total':
                    return 'total'
                elif main_cat_str == 'Males':
                    return 'males'
                elif main_cat_str == 'Females':
                    return 'females'
        return None
    
    def _parse_data_row_breakdowns(self, row: pd.Series, headers: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a single data row into multiple records for different breakdowns"""
        records = []
        
        # Extract basic identifiers
        year = row.iloc[headers['year_col']]
        region = row.iloc[headers['region_col']]
        
        if pd.isna(year) or pd.isna(region):
            return records
        
        year_str = str(year)
        region_str = str(region)
        
        # Create records for each breakdown
        column_mapping = headers['column_mapping']
        
        # 0. TOTAL POPULATION (Column C - Population total)
        # This is the overall total for the Year+Region combination
        population_total_value = row.iloc[2]  # Column C
        if pd.notna(population_total_value) and self._is_numeric(str(population_total_value)):
            total_pop_record = self._create_base_record(year_str, region_str)
            total_pop_record['Sex'] = 'Total'
            total_pop_record['Age_Group'] = '_Z'
            total_pop_record['Nationality'] = '_Z'
            total_pop_record['Marital_Status'] = '_Z'
            total_pop_record['Value'] = float(population_total_value)
            records.append(total_pop_record)
        
        # 1. Total population by age
        for age_info in column_mapping['total']:
            record = self._create_base_record(year_str, region_str)
            record['Sex'] = 'Total'
            record['Age_Group'] = age_info['age_group']
            record['Nationality'] = '_Z'
            record['Marital_Status'] = '_Z'
            
            # Get the value
            value = row.iloc[age_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record['Value'] = float(value)
            else:
                record['Value'] = '_Z'
            
            records.append(record)
        
        # 2. Males by age
        for age_info in column_mapping['males']:
            record = self._create_base_record(year_str, region_str)
            record['Sex'] = 'Males'
            record['Age_Group'] = age_info['age_group']
            record['Nationality'] = '_Z'
            record['Marital_Status'] = '_Z'
            
            # Get the value
            value = row.iloc[age_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record['Value'] = float(value)
            else:
                record['Value'] = '_Z'
            
            records.append(record)
        
        # 3. Females by age
        for age_info in column_mapping['females']:
            record = self._create_base_record(year_str, region_str)
            record['Sex'] = 'Females'
            record['Age_Group'] = age_info['age_group']
            record['Nationality'] = '_Z'
            record['Marital_Status'] = '_Z'
            
            # Get the value
            value = row.iloc[age_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record['Value'] = float(value)
            else:
                record['Value'] = '_Z'
            
            records.append(record)
        
        # 4. Nationality breakdown (for total population)
        for nat_info in column_mapping['nationality']:
            record = self._create_base_record(year_str, region_str)
            record['Sex'] = 'Total'
            record['Age_Group'] = '_Z'
            record['Nationality'] = nat_info['nationality']
            record['Marital_Status'] = '_Z'
            
            # Get the value
            value = row.iloc[nat_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record['Value'] = float(value)
            else:
                record['Value'] = '_Z'
            
            records.append(record)
        
        # 5. Marital status breakdown (for total population)
        for marital_info in column_mapping['marital']:
            record = self._create_base_record(year_str, region_str)
            record['Sex'] = 'Total'
            record['Age_Group'] = '_Z'
            record['Nationality'] = '_Z'
            record['Marital_Status'] = marital_info['marital_status']
            
            # Get the value
            value = row.iloc[marital_info['column']]
            if pd.notna(value) and self._is_numeric(str(value)):
                record['Value'] = float(value)
            else:
                record['Value'] = '_Z'
            
            records.append(record)
        
        return records
    
    def _create_base_record(self, year: str, region: str) -> Dict[str, Any]:
        """Create a base record with common dimensions"""
        return {
            'Year': year,
            'Region': region
        }
    
    def _is_age_group(self, value: str) -> bool:
        """Check if a value represents an age group"""
        age_patterns = ['0-14', '15-19', '20-24', '25-29', '30-44', '45-64', '65+']
        return value in age_patterns
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def create_sdmx_template(self, analysis: Dict[str, Any]) -> pd.DataFrame:
        """Create a template DataFrame with all possible dimensions"""
        logger.info("Creating SDMX template with all dimensions")
        
        # Extract all possible dimension values
        dimensions = self._extract_all_dimensions(analysis)
        
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
            sex_values = ['Total', 'Males', 'Females']
            age_groups = ['0-14', '15-19', '20-24', '25-29', '30-44', '45-64', '65+']
            nationality_values = ['Greek', 'EU country', 'Other']
            marital_values = ['Single', 'Married', 'Widowed, divorced      or legally separated']
            
            # Create template records for all combinations
            for year in year_values:
                for region in region_values:
                    # Add total population record (Total, _Z, _Z, _Z)
                    record = self._create_template_record(year, region, 'Total', '_Z', '_Z', '_Z')
                    template_records.append(record)
                    
                    for sex in sex_values:
                        if sex == 'Total':
                            # For Total, we have age groups, nationality, and marital status
                            for age in age_groups:
                                record = self._create_template_record(year, region, sex, age, '_Z', '_Z')
                                template_records.append(record)
                            
                            for nationality in nationality_values:
                                record = self._create_template_record(year, region, sex, '_Z', nationality, '_Z')
                                template_records.append(record)
                            
                            for marital in marital_values:
                                record = self._create_template_record(year, region, sex, '_Z', '_Z', marital)
                                template_records.append(record)
                        else:
                            # For Males/Females, we only have age groups
                            for age in age_groups:
                                record = self._create_template_record(year, region, sex, age, '_Z', '_Z')
                                template_records.append(record)
        
        return pd.DataFrame(template_records)
    
    def _create_template_record(self, year: str, region: str, sex: str, age: str, nationality: str, marital: str) -> Dict[str, Any]:
        """Create a template record with specified dimensions"""
        return {
            'Year': str(year),
            'Region': str(region),
            'Sex': sex,
            'Age_Group': age,
            'Nationality': nationality,
            'Marital_Status': marital,
            'Value': '_Z'
        }
    
    def _extract_all_dimensions(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract all possible dimension values"""
        dimensions = {}
        
        data_struct = analysis['data_structure']
        if data_struct['data_start_row'] is not None:
            df = analysis['raw_dataframe']
            data_rows = df.iloc[data_struct['data_start_row']:data_struct['data_end_row']+1]
            
            # Extract dimensions from data
            if len(data_rows) > 0:
                # Year dimension
                dimensions['Year'] = data_rows.iloc[:, 0].dropna().unique().tolist()
                
                # Region dimension
                dimensions['Region'] = data_rows.iloc[:, 1].dropna().unique().tolist()
                
                # Sex dimension
                dimensions['Sex'] = ['Total', 'Males', 'Females']
                
                # Age groups
                dimensions['Age_Groups'] = ['0-14', '15-19', '20-24', '25-29', '30-44', '45-64', '65+']
                
                # Nationality
                dimensions['Nationality'] = ['Greek', 'EU country', 'Other']
                
                # Marital status
                dimensions['Marital_Status'] = ['Single', 'Married', 'Widowed, divorced      or legally separated']
        
        return dimensions
    
    def print_parsing_summary(self, df: pd.DataFrame, analysis: Dict[str, Any]):
        """Print a summary of the parsing results"""
        print(f"\n{'='*80}")
        print(f"DATA PARSING SUMMARY")
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
                count = len(df[df['Sex'] == sex])
                print(f"    {sex}: {count} records")
        
        if 'Age_Group' in df.columns:
            print(f"  Age group breakdown:")
            for age in df['Age_Group'].unique():
                if age != '_Z':
                    count = len(df[df['Age_Group'] == age])
                    print(f"    {age}: {count} records")
        
        if 'Nationality' in df.columns:
            print(f"  Nationality breakdown:")
            for nat in df['Nationality'].unique():
                if nat != '_Z':
                    count = len(df[df['Nationality'] == nat])
                    print(f"    {nat}: {count} records")
        
        if 'Marital_Status' in df.columns:
            print(f"  Marital status breakdown:")
            for marital in df['Marital_Status'].unique():
                if marital != '_Z':
                    count = len(df[df['Marital_Status'] == marital])
                    print(f"    {marital}: {count} records")
        
        print(f"\nSample data:")
        print(df.head(10).to_string())
        
        print(f"{'='*80}\n")
