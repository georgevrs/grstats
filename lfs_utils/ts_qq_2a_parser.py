"""
TS QQ 2A Parser - Quarterly Demographic Employment Data Parser
Parses the A0101_SJO01_TS_QQ_01_2001_01_2025_2A_F_EN.xlsx file
which contains quarterly employment data by age groups and gender from 2001-2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TS_QQ_2A_Parser:
    """
    Parser for TS QQ 2A quarterly demographic employment data
    Handles both absolute numbers and percentages by age groups and gender
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self.parsed_data = None
        
    def load_excel(self) -> pd.DataFrame:
        """Load the Excel file and return raw data"""
        try:
            # Read the Excel file
            df = pd.read_excel(self.file_path, header=None)
            logger.info(f"Loaded Excel file with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            raise
    
    def identify_sections(self, df: pd.DataFrame) -> Dict[str, List[int]]:
        """Identify different sections in the data"""
        sections = {
            'absolute_numbers': [],
            'percentages': [],
            'year_headers': []
        }
        
        for idx, row in df.iterrows():
            row_text = ' '.join([str(cell) for cell in row if pd.notna(cell)])
            
            # Find section headers
            if 'ABSOLUTE NUMBERS' in row_text:
                sections['absolute_numbers'].append(idx)
            elif 'PERCENTAGES' in row_text:
                sections['percentages'].append(idx)
            elif 'Ι.' in row_text and 'ABSOLUTE NUMBERS' in row_text:
                sections['absolute_numbers'].append(idx)
            elif 'ΙΙ.' in row_text and 'PERCENTAGES' in row_text:
                sections['percentages'].append(idx)
            
            # Find year headers (they appear in row 3, 51, etc. - not in first column)
            # Years appear in columns 1, 3, 5, 7 of the header row
            if 'Age groups and gender' in row_text:
                # This is a header row with years
                for col in [1, 3, 5, 7]:
                    if col < len(row) and pd.notna(row[col]) and isinstance(row[col], (int, float)):
                        if 2000 <= row[col] <= 2030:
                            sections['year_headers'].append((idx, col, int(row[col])))
        
        logger.info(f"Found sections: {sections}")
        return sections
    
    def identify_age_gender_groups(self, df: pd.DataFrame) -> List[str]:
        """Identify age groups and gender categories"""
        age_gender_groups = []
        
        for idx, row in df.iterrows():
            if pd.notna(row[0]) and isinstance(row[0], str):
                cell_text = str(row[0]).strip()
                if cell_text in ['TOTAL', 'MALES', 'FEMALES', '15-19', '20-24', '25-29', '30-44', '45-64', '65 +']:
                    if cell_text not in age_gender_groups:
                        age_gender_groups.append(cell_text)
        
        logger.info(f"Found age/gender groups: {age_gender_groups}")
        return age_gender_groups
    
    def parse_quarterly_data(self, df: pd.DataFrame, sections: Dict[str, List[int]]) -> pd.DataFrame:
        """Parse quarterly data for both absolute numbers and percentages"""
        all_data = []
        
        # Parse absolute numbers sections
        for abs_section in sections['absolute_numbers']:
            data = self._parse_absolute_numbers_section(df, abs_section)
            all_data.extend(data)
        
        # Parse percentages sections
        for pct_section in sections['percentages']:
            data = self._parse_percentages_section(df, pct_section)
            all_data.extend(data)
        
        # Create DataFrame
        result_df = pd.DataFrame(all_data)
        logger.info(f"Parsed {len(result_df)} data points")
        return result_df
    
    def _parse_absolute_numbers_section(self, df: pd.DataFrame, section_start: int) -> List[Dict]:
        """Parse absolute numbers section"""
        data = []
        
        # Find the end of this section (next section or end of data)
        section_end = len(df)
        for idx in range(section_start + 1, len(df)):
            row_text = ' '.join([str(cell) for cell in df.iloc[idx] if pd.notna(cell)])
            if 'PERCENTAGES' in row_text or 'ABSOLUTE NUMBERS' in row_text:
                section_end = idx
                break
        
        # Find the header row (contains years and quarter labels)
        header_row = None
        for idx in range(section_start + 1, section_end):
            row_text = ' '.join([str(cell) for cell in df.iloc[idx] if pd.notna(cell)])
            if 'Age groups and gender' in row_text:
                header_row = idx
                break
        
        if header_row is None:
            logger.warning(f"No header row found in section starting at {section_start}")
            return data
        
        # Extract years and quarter structure from header row
        header = df.iloc[header_row]
        years = []
        for col in [1, 3, 5, 7]:
            if col < len(header) and pd.notna(header[col]) and isinstance(header[col], (int, float)):
                if 2000 <= header[col] <= 2030:
                    years.append((col, int(header[col])))
        
        logger.info(f"Found years in header row {header_row}: {years}")
        
        # Parse data rows (start after header row + 1 for column labels)
        data_start = header_row + 2
        
        for row_idx in range(data_start, section_end):
            row = df.iloc[row_idx]
            
            if pd.notna(row[0]) and isinstance(row[0], str):
                age_gender = str(row[0]).strip()
                if age_gender in ['TOTAL', 'MALES', 'FEMALES', '15-19', '20-24', '25-29', '30-44', '45-64', '65 +']:
                    logger.info(f"Processing {age_gender}")
                    
                    # Extract quarterly data for each year
                    for col, year in years:
                        quarters_data = self._extract_quarterly_absolute_data_for_year(row, col, year)
                        
                        # Create records for each quarter and indicator
                        for quarter_data in quarters_data:
                            quarter_data['AGE_GENDER'] = age_gender
                            data.append(quarter_data)
        
        logger.info(f"Total data points from absolute numbers section: {len(data)}")
        return data
    
    def _extract_quarterly_absolute_data_for_year(self, row: pd.Series, start_col: int, year: int) -> List[Dict]:
        """Extract quarterly absolute data for a specific year starting from a specific column"""
        quarters_data = []
        
        # Each quarter has 5 indicators: Population, Labour Force, Employed, Unemployed, Inactives
        # Quarters are consecutive: Q1, Q2, Q3, Q4
        quarters = [
            ('Q1', start_col, start_col + 4),      # 1st quarter: columns start_col to start_col+4
            ('Q2', start_col + 5, start_col + 9),  # 2nd quarter: columns start_col+5 to start_col+9
            ('Q3', start_col + 10, start_col + 14), # 3rd quarter: columns start_col+10 to start_col+14
            ('Q4', start_col + 15, start_col + 19)  # 4th quarter: columns start_col+15 to start_col+19
        ]
        
        for quarter_name, start, end in quarters:
            if end < len(row):
                # Extract data for this quarter
                population = row[start]
                labour_force = row[start + 1]
                employed = row[start + 2]
                unemployed = row[start + 3]
                inactives = row[start + 4]
                
                # Create records for each indicator
                indicators = [
                    ('Population', population, 'Thousands of persons'),
                    ('Labour Force', labour_force, 'Thousands of persons'),
                    ('Employed', employed, 'Thousands of persons'),
                    ('Unemployed', unemployed, 'Thousands of persons'),
                    ('Inactives', inactives, 'Thousands of persons')
                ]
                
                for indicator_name, value, unit in indicators:
                    quarters_data.append({
                        'TIME_PERIOD': f"{year}-{quarter_name}",
                        'YEAR': year,
                        'QUARTER': quarter_name,
                        'QUARTER_NUM': quarters.index((quarter_name, start, end)) + 1,
                        'INDICATOR': indicator_name,
                        'VALUE': value,
                        'UNIT': unit,
                        'DATA_TYPE': 'Absolute',
                        'FREQ': 'Q'
                    })
        
        return quarters_data
    
    def _parse_percentages_section(self, df: pd.DataFrame, section_start: int) -> List[Dict]:
        """Parse percentages section"""
        data = []
        
        # Find the end of this section
        section_end = len(df)
        for idx in range(section_start + 1, len(df)):
            row_text = ' '.join([str(cell) for cell in df.iloc[idx] if pd.notna(cell)])
            if 'ABSOLUTE NUMBERS' in row_text:
                section_end = idx
                break
        
        # Find the header row (contains years and quarter labels)
        header_row = None
        for idx in range(section_start + 1, section_end):
            row_text = ' '.join([str(cell) for cell in df.iloc[idx] if pd.notna(cell)])
            if 'Age groups and gender' in row_text:
                header_row = idx
                break
        
        if header_row is None:
            logger.warning(f"No header row found in percentages section starting at {section_start}")
            return data
        
        # Extract years and quarter structure from header row
        header = df.iloc[header_row]
        years = []
        for col in [1, 3, 5, 7]:
            if col < len(header) and pd.notna(header[col]) and isinstance(header[col], (int, float)):
                if 2000 <= header[col] <= 2030:
                    years.append((col, int(header[col])))
        
        logger.info(f"Found years in percentages header row {header_row}: {years}")
        
        # If no years found in header, try to find them in the data rows
        if not years:
            # Look for year headers in the data rows
            for row_idx in range(header_row + 1, section_end):
                row = df.iloc[row_idx]
                if pd.notna(row[0]) and isinstance(row[0], (int, float)):
                    if 2000 <= row[0] <= 2030:
                        years.append((0, int(row[0])))
                        logger.info(f"Found year {row[0]} in data row {row_idx}")
        
        # Parse data rows (start after header row + 1 for column labels)
        data_start = header_row + 2
        
        for row_idx in range(data_start, section_end):
            row = df.iloc[row_idx]
            
            if pd.notna(row[0]) and isinstance(row[0], str):
                age_gender = str(row[0]).strip()
                if age_gender in ['TOTAL', 'MALES', 'FEMALES', '15-19', '20-24', '25-29', '30-44', '45-64', '65 +']:
                    logger.info(f"Processing {age_gender} for percentages")
                    
                    # Extract quarterly percentage data for each year
                    for col, year in years:
                        quarters_data = self._extract_quarterly_percentage_data_for_year(row, col, year)
                        
                        # Create records for each quarter and indicator
                        for quarter_data in quarters_data:
                            quarter_data['AGE_GENDER'] = age_gender
                            data.append(quarter_data)
        
        logger.info(f"Total data points from percentages section: {len(data)}")
        return data
    
    def _extract_quarterly_percentage_data_for_year(self, row: pd.Series, start_col: int, year: int) -> List[Dict]:
        """Extract quarterly percentage data for a specific year starting from a specific column"""
        quarters_data = []
        
        # Each quarter has 2 indicators: Activity rate, Unemployment rate
        # Quarters are consecutive: Q1, Q2, Q3, Q4
        quarters = [
            ('Q1', start_col, start_col + 1),      # 1st quarter: columns start_col to start_col+1
            ('Q2', start_col + 2, start_col + 3),  # 2nd quarter: columns start_col+2 to start_col+3
            ('Q3', start_col + 4, start_col + 5),  # 3rd quarter: columns start_col+4 to start_col+5
            ('Q4', start_col + 6, start_col + 7)   # 4th quarter: columns start_col+6 to start_col+7
        ]
        
        for quarter_name, start, end in quarters:
            if end < len(row):
                # Extract data for this quarter
                activity_rate = row[start]
                unemployment_rate = row[start + 1]
                
                # Create records for each indicator
                indicators = [
                    ('Activity rate', activity_rate, 'Percentage'),
                    ('Unemployment rate', unemployment_rate, 'Percentage')
                ]
                
                for indicator_name, value, unit in indicators:
                    quarters_data.append({
                        'TIME_PERIOD': f"{year}-{quarter_name}",
                        'YEAR': year,
                        'QUARTER': quarter_name,
                        'QUARTER_NUM': quarters.index((quarter_name, start, end)) + 1,
                        'INDICATOR': indicator_name,
                        'VALUE': value,
                        'UNIT': unit,
                        'DATA_TYPE': 'Percentage',
                        'FREQ': 'Q'
                    })
        
        return quarters_data
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the parsed data"""
        # Remove rows with missing values
        df_clean = df.dropna(subset=['VALUE'])
        
        # Convert values to numeric
        df_clean['VALUE'] = pd.to_numeric(df_clean['VALUE'], errors='coerce')
        
        # Remove rows with invalid values
        df_clean = df_clean[df_clean['VALUE'].notna()]
        
        # Sort by time period
        df_clean = df_clean.sort_values(['YEAR', 'QUARTER_NUM', 'AGE_GENDER', 'INDICATOR'])
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        logger.info(f"Cleaned data: {len(df_clean)} valid data points")
        return df_clean
    
    def create_sdmx_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert to SDMX-compatible format"""
        sdmx_df = df.copy()
        
        # Add SDMX-specific columns
        sdmx_df['OBS_VALUE'] = sdmx_df['VALUE']
        sdmx_df['OBS_STATUS'] = 'A'  # Normal value
        sdmx_df['UNIT_MULT'] = 0  # Units (thousands/percentage)
        sdmx_df['DECIMALS'] = 2  # Decimal places
        
        # Split AGE_GENDER into separate AGE and SEX columns
        sdmx_df['AGE'] = sdmx_df['AGE_GENDER'].apply(self._extract_age)
        sdmx_df['SEX'] = sdmx_df['AGE_GENDER'].apply(self._extract_sex)
        
        # Create dimension columns for SDMX
        sdmx_df['AGE_CODE'] = sdmx_df['AGE'].map({
            'TOTAL': 'TOT',
            '15-19': '15_19',
            '20-24': '20_24',
            '25-29': '25_29',
            '30-44': '30_44',
            '45-64': '45_64',
            '65+': '65_PLUS'
        })
        
        sdmx_df['SEX_CODE'] = sdmx_df['SEX'].map({
            'TOTAL': 'TOT',
            'MALES': 'M',
            'FEMALES': 'F'
        })
        
        sdmx_df['INDICATOR_CODE'] = sdmx_df['INDICATOR'].map({
            'Population': 'POP',
            'Labour Force': 'LF',
            'Employed': 'EMP',
            'Unemployed': 'UNE',
            'Inactives': 'INACT',
            'Activity rate': 'AR',
            'Unemployment rate': 'UR'
        })
        
        sdmx_df['DATA_TYPE_CODE'] = sdmx_df['DATA_TYPE'].map({
            'Absolute': 'ABS',
            'Percentage': 'PCT'
        })
        
        # Select SDMX columns with separate AGE and SEX
        sdmx_columns = [
            'TIME_PERIOD', 'YEAR', 'QUARTER', 'QUARTER_NUM',
            'AGE', 'AGE_CODE', 'SEX', 'SEX_CODE', 'INDICATOR_CODE', 'DATA_TYPE_CODE',
            'OBS_VALUE', 'OBS_STATUS', 'UNIT_MULT', 'DECIMALS',
            'UNIT', 'FREQ'
        ]
        
        return sdmx_df[sdmx_columns]
    
    def _extract_age(self, age_gender: str) -> str:
        """Extract age group from AGE_GENDER string"""
        if age_gender in ['TOTAL', 'MALES', 'FEMALES']:
            return 'TOTAL'
        else:
            return age_gender
    
    def _extract_sex(self, age_gender: str) -> str:
        """Extract sex from AGE_GENDER string"""
        if age_gender in ['TOTAL', '15-19', '20-24', '25-29', '30-44', '45-64', '65 +']:
            if age_gender == 'TOTAL':
                return 'TOTAL'
            else:
                return 'TOTAL'  # Age groups represent total for that age group
        else:
            return age_gender  # MALES or FEMALES
    
    def parse(self) -> pd.DataFrame:
        """Main parsing method"""
        logger.info("Starting TS QQ 2A parsing...")
        
        # Load data
        self.data = self.load_excel()
        
        # Identify sections
        sections = self.identify_sections(self.data)
        
        # Parse quarterly data
        parsed_data = self.parse_quarterly_data(self.data, sections)
        
        # Clean data
        cleaned_data = self.clean_data(parsed_data)
        
        # Convert to SDMX format
        sdmx_data = self.create_sdmx_format(cleaned_data)
        
        self.parsed_data = sdmx_data
        logger.info("TS QQ 2A parsing completed successfully!")
        
        return sdmx_data
    
    def save_to_excel(self, output_path: str):
        """Save parsed data to Excel"""
        if self.parsed_data is not None:
            self.parsed_data.to_excel(output_path, index=False)
            logger.info(f"Data saved to: {output_path}")
        else:
            logger.warning("No parsed data to save")
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of parsed data"""
        if self.parsed_data is None:
            return {}
        
        summary = {
            'total_observations': len(self.parsed_data),
            'years_covered': sorted(self.parsed_data['YEAR'].unique()),
            'age_groups': sorted(self.parsed_data['AGE'].unique()),
            'sex_categories': sorted(self.parsed_data['SEX'].unique()),
            'indicators': sorted(self.parsed_data['INDICATOR_CODE'].unique()),
            'data_types': sorted(self.parsed_data['DATA_TYPE_CODE'].unique()),
            'date_range': {
                'start': self.parsed_data['TIME_PERIOD'].min(),
                'end': self.parsed_data['TIME_PERIOD'].max()
            }
        }
        
        return summary


def main():
    """Main function to test the parser"""
    file_path = "assets/LFS/A0101_SJO01_TS_QQ_01_2001_01_2025_2A_F_EN.xlsx"
    
    # Initialize parser
    parser = TS_QQ_2A_Parser(file_path)
    
    try:
        # Parse the data
        parsed_data = parser.parse()
        
        # Print summary
        summary = parser.get_summary_stats()
        print("\n=== TS QQ 2A PARSING SUMMARY ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # Save to Excel
        output_path = "assets/prepared/lfs_ts_qq_2a_parsed.xlsx"
        parser.save_to_excel(output_path)
        
        # Show first few rows
        print("\n=== FIRST 20 ROWS ===")
        print(parsed_data.head(20))
        
        # Show data shape
        print(f"\nData shape: {parsed_data.shape}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
