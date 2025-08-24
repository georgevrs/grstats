"""
TS MM 01A Parser - Monthly Employment Data Parser
Parses the A0101_SJO02_TS_MM_01_2004_05_2025_01A_F_EN.xlsx file
which contains monthly employment data from 2004-2025
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

class TS_MM_01A_Parser:
    """
    Parser for TS MM 01A monthly employment data
    Handles both unadjusted and seasonally adjusted estimates
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self.parsed_data = None
        
    def load_excel(self) -> pd.DataFrame:
        """Load the Excel file and return raw data"""
        try:
            # Read the Excel file
            df = pd.read_excel(self.file_path, sheet_name='TABLE 1Α', header=None)
            logger.info(f"Loaded Excel file with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            raise
    
    def identify_year_rows(self, df: pd.DataFrame) -> List[int]:
        """Identify rows that contain year headers"""
        year_rows = []
        for idx, row in df.iterrows():
            # Check if first column contains a year (2004-2025)
            if pd.notna(row[0]) and isinstance(row[0], (int, float)):
                if 2000 <= row[0] <= 2030:
                    year_rows.append(idx)
        logger.info(f"Found {len(year_rows)} year headers at rows: {year_rows}")
        return year_rows
    
    def parse_monthly_data(self, df: pd.DataFrame, year_rows: List[int]) -> pd.DataFrame:
        """Parse monthly data for each year"""
        all_data = []
        
        for i, year_row in enumerate(year_rows):
            year = int(df.iloc[year_row, 0])
            
            # Determine the range for this year's data
            if i < len(year_rows) - 1:
                next_year_row = year_rows[i + 1]
                data_range = range(year_row + 1, next_year_row)
            else:
                # For the last year, go until the end or until we hit non-month data
                data_range = range(year_row + 1, len(df))
            
            # Parse each month in this year
            for row_idx in data_range:
                row = df.iloc[row_idx]
                
                # Check if this is a month row
                if pd.notna(row[0]) and isinstance(row[0], str):
                    month_name = str(row[0]).strip()
                    if month_name in ['January', 'February', 'March', 'April', 'May', 'June',
                                    'July', 'August', 'September', 'October', 'November', 'December']:
                        
                        # Extract data for both unadjusted and seasonally adjusted
                        month_num = self._month_name_to_number(month_name)
                        
                        # Unadjusted estimates (columns 1-4)
                        unadj_employed = row[1]
                        unadj_unemployed = row[2]
                        unadj_outside_labour = row[3]
                        unadj_unemployment_rate = row[4]
                        
                        # Seasonally adjusted estimates (columns 5-8)
                        sa_employed = row[5]
                        sa_unemployed = row[6]
                        sa_outside_labour = row[7]
                        sa_unemployment_rate = row[8]
                        
                        # Create records for each indicator
                        records = [
                            # Unadjusted estimates
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Unadjusted',
                                'INDICATOR': 'Employed',
                                'VALUE': unadj_employed,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'M'
                            },
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Unadjusted',
                                'INDICATOR': 'Unemployed',
                                'VALUE': unadj_unemployed,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'M'
                            },
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Unadjusted',
                                'INDICATOR': 'Outside labour force',
                                'VALUE': unadj_outside_labour,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'M'
                            },
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Unadjusted',
                                'INDICATOR': 'Unemployment rate',
                                'VALUE': unadj_unemployment_rate,
                                'UNIT': 'Percentage',
                                'FREQ': 'M'
                            },
                            # Seasonally adjusted estimates
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Seasonally adjusted',
                                'INDICATOR': 'Employed',
                                'VALUE': sa_employed,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'M'
                            },
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Seasonally adjusted',
                                'INDICATOR': 'Unemployed',
                                'VALUE': sa_unemployed,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'M'
                            },
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Seasonally adjusted',
                                'INDICATOR': 'Outside labour force',
                                'VALUE': sa_outside_labour,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'M'
                            },
                            {
                                'TIME_PERIOD': f"{year}-{month_num:02d}",
                                'YEAR': year,
                                'MONTH': month_num,
                                'MONTH_NAME': month_name,
                                'ADJUSTMENT': 'Seasonally adjusted',
                                'INDICATOR': 'Unemployment rate',
                                'VALUE': sa_unemployment_rate,
                                'UNIT': 'Percentage',
                                'FREQ': 'M'
                            }
                        ]
                        
                        all_data.extend(records)
        
        # Create DataFrame
        result_df = pd.DataFrame(all_data)
        logger.info(f"Parsed {len(result_df)} data points")
        return result_df
    
    def _month_name_to_number(self, month_name: str) -> int:
        """Convert month name to number (1-12)"""
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        return month_map.get(month_name, 0)
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the parsed data"""
        # Remove rows with missing values
        df_clean = df.dropna(subset=['VALUE'])
        
        # Convert values to numeric
        df_clean['VALUE'] = pd.to_numeric(df_clean['VALUE'], errors='coerce')
        
        # Remove rows with invalid values
        df_clean = df_clean[df_clean['VALUE'].notna()]
        
        # Sort by time period
        df_clean = df_clean.sort_values(['YEAR', 'MONTH', 'ADJUSTMENT', 'INDICATOR'])
        
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
        sdmx_df['UNIT_MULT'] = 0  # Units (thousands)
        sdmx_df['DECIMALS'] = 2  # Decimal places
        
        # Create dimension columns for SDMX
        sdmx_df['ADJUSTMENT_TYPE'] = sdmx_df['ADJUSTMENT'].map({
            'Unadjusted': 'UNADJ',
            'Seasonally adjusted': 'SA'
        })
        
        sdmx_df['INDICATOR_CODE'] = sdmx_df['INDICATOR'].map({
            'Employed': 'EMP',
            'Unemployed': 'UNE',
            'Outside labour force': 'OLF',
            'Unemployment rate': 'UNR'
        })
        
        # Select SDMX columns
        sdmx_columns = [
            'TIME_PERIOD', 'YEAR', 'MONTH', 'MONTH_NAME',
            'ADJUSTMENT_TYPE', 'INDICATOR_CODE', 'OBS_VALUE',
            'OBS_STATUS', 'UNIT_MULT', 'DECIMALS', 'UNIT', 'FREQ'
        ]
        
        return sdmx_df[sdmx_columns]
    
    def parse(self) -> pd.DataFrame:
        """Main parsing method"""
        logger.info("Starting TS MM 01A parsing...")
        
        # Load data
        self.data = self.load_excel()
        
        # Identify year rows
        year_rows = self.identify_year_rows(self.data)
        
        # Parse monthly data
        parsed_data = self.parse_monthly_data(self.data, year_rows)
        
        # Clean data
        cleaned_data = self.clean_data(parsed_data)
        
        # Convert to SDMX format
        sdmx_data = self.create_sdmx_format(cleaned_data)
        
        self.parsed_data = sdmx_data
        logger.info("TS MM 01A parsing completed successfully!")
        
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
            'indicators': sorted(self.parsed_data['INDICATOR_CODE'].unique()),
            'adjustment_types': sorted(self.parsed_data['ADJUSTMENT_TYPE'].unique()),
            'date_range': {
                'start': self.parsed_data['TIME_PERIOD'].min(),
                'end': self.parsed_data['TIME_PERIOD'].max()
            }
        }
        
        return summary


def main():
    """Main function to test the parser"""
    file_path = "assets/LFS/A0101_SJO02_TS_MM_01_2004_05_2025_01A_F_EN.xlsx"
    
    # Initialize parser
    parser = TS_MM_01A_Parser(file_path)
    
    try:
        # Parse the data
        parsed_data = parser.parse()
        
        # Print summary
        summary = parser.get_summary_stats()
        print("\n=== TS MM 01A PARSING SUMMARY ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # Save to Excel
        output_path = "assets/prepared/lfs_ts_mm_01a_parsed.xlsx"
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
