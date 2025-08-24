#!/usr/bin/env python3
"""
TS QQ 06 Parser - Unemployment Duration by Search Period
Parses quarterly unemployment data by duration of unemployment search.
Handles both absolute numbers and percentages.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TS_QQ_06_Parser:
    """Parser for TS QQ 06 - Unemployment Duration by Search Period"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parsed_data = None
        self.df = None
        
        # Duration of unemployment categories
        self.duration_categories = {
            'TOTAL': 'Total unemployed',
            'Will start now searching for employment': 'Will start now searching for employment',
            'Less than a month': 'Less than a month',
            '1 - 2 months': '1 - 2 months',
            '3 - 5 months': '3 - 5 months',
            '6 - 11 months': '6 - 11 months',
            '12 months and over': '12 months and over',
            '"New unemployed" in Labour market': 'New unemployed in Labour market',
            'Percentage (%) of "New unemployed" in Labour market': 'Percentage of New unemployed in Labour market',
            'Percentage (%) of long term unemployed': 'Percentage of long term unemployed'
        }
        
        # Data types
        self.data_types = {
            'absolute': 'Absolute',
            'percentage': 'Percentage'
        }
    
    def load_data(self) -> pd.DataFrame:
        """Load Excel file"""
        try:
            logger.info(f"Loading file: {self.file_path}")
            self.df = pd.read_excel(self.file_path, header=None)
            logger.info(f"Loaded data with shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise
    
    def identify_sections(self) -> Dict:
        """Identify different sections in the data"""
        sections = {
            'data_sections': []
        }
        
        # Look for rows that contain "Duration of search for employment"
        for idx, row in self.df.iterrows():
            row_str = str(row[0]).strip()
            if pd.notna(row[0]) and 'Duration of search for employment' in row_str:
                sections['data_sections'].append(idx)
        
        logger.info(f"Identified {len(sections['data_sections'])} data sections")
        return sections
    
    def extract_years_from_header(self, row_idx: int) -> List[Tuple[int, int]]:
        """Extract years and their column positions from header row"""
        years = []
        row = self.df.iloc[row_idx]
        
        logger.info(f"Extracting years from row {row_idx}: {row[0]}")
        
        for col_idx, cell in enumerate(row):
            if pd.notna(cell) and isinstance(cell, str):
                logger.info(f"Checking column {col_idx}: '{cell}'")
                # Look for patterns like "1st quarter 2001", "2nd quarter 2001", etc.
                quarter_year_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+quarter\s+(\d{4})', cell)
                if quarter_year_match:
                    quarter_num = int(quarter_year_match.group(1))
                    year = int(quarter_year_match.group(2))
                    if 2000 <= year <= 2030:
                        years.append((col_idx, year, quarter_num))
                        logger.info(f"Found {quarter_num} quarter {year} at column {col_idx}")
                else:
                    logger.info(f"No quarter pattern found in '{cell}'")
        
        logger.info(f"Total years found: {len(years)}")
        return years
    
    def parse_data_section(self, section_start: int) -> List[Dict]:
        """Parse a data section (absolute numbers or percentages)"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and 'Duration of search for employment' in str(self.df.iloc[idx, 0]):
                section_end = idx
                break
        
        # Find year headers - look in the row with "Duration of search for employment"
        years = self.extract_years_from_header(section_start)
        if not years:
            logger.warning("No years found in data section")
            return data_points
        
        # Determine if this is a percentage section
        is_percentage = False
        for row_idx in range(section_start + 2, section_end):
            row = self.df.iloc[row_idx]
            if pd.notna(row[0]) and 'Percentage' in str(row[0]):
                is_percentage = True
                break
        
        # Process each row in the section, starting from row after the year header
        for row_idx in range(section_start + 2, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[0]) or str(row[0]).strip() == '':
                continue
            
            # Check if this is a duration category row
            category_name = str(row[0]).strip()
            if category_name in self.duration_categories:
                
                # Determine data type
                if is_percentage or 'Percentage' in category_name:
                    data_type = 'Percentage'
                    unit = 'Percentage'
                else:
                    data_type = 'Absolute'
                    unit = 'Thousands of persons'
                
                # Extract data for each year/quarter
                for col_idx, year, quarter_num in years:
                    if col_idx < len(row) and pd.notna(row[col_idx]):
                        try:
                            value = float(row[col_idx])
                            quarter_name = f"Q{quarter_num}"
                            
                            data_points.append({
                                'YEAR': year,
                                'QUARTER': quarter_name,
                                'QUARTER_NUM': quarter_num,
                                'TIME_PERIOD': f"{year}-{quarter_name}",
                                'DURATION_CATEGORY': category_name,
                                'DURATION_CATEGORY_NAME': self.duration_categories[category_name],
                                'DATA_TYPE': data_type,
                                'VALUE': value,
                                'UNIT': unit,
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from data section")
        return data_points
    
    def parse(self) -> pd.DataFrame:
        """Main parsing method"""
        logger.info("Starting TS QQ 06 parsing...")
        
        # Load data
        self.load_data()
        
        # Identify sections
        sections = self.identify_sections()
        
        # Parse all sections
        all_data = []
        
        # Parse each data section
        for section_start in sections['data_sections']:
            data = self.parse_data_section(section_start)
            all_data.extend(data)
        
        # Create DataFrame
        if all_data:
            self.parsed_data = pd.DataFrame(all_data)
            logger.info(f"Parsed {len(self.parsed_data)} data points")
            
            # Clean and validate data
            self.parsed_data = self.clean_data(self.parsed_data)
            
            # Convert to SDMX format
            self.parsed_data = self.create_sdmx_format(self.parsed_data)
            
            return self.parsed_data
        else:
            logger.error("No data parsed")
            return pd.DataFrame()
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate parsed data"""
        logger.info(f"Cleaning data: {len(df)} data points")
        
        # Remove rows with missing values
        df_clean = df.dropna(subset=['VALUE'])
        
        # Convert VALUE to numeric
        df_clean['VALUE'] = pd.to_numeric(df_clean['VALUE'], errors='coerce')
        
        # Remove invalid values
        df_clean = df_clean[df_clean['VALUE'] >= 0]
        
        # Sort by time and duration category
        df_clean = df_clean.sort_values(['YEAR', 'QUARTER_NUM', 'DURATION_CATEGORY'])
        
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
        
        # Create dimension codes for SDMX
        sdmx_df['DURATION_CATEGORY_CODE'] = sdmx_df['DURATION_CATEGORY'].map({
            'TOTAL': 'TOT',
            'Will start now searching for employment': 'START_NOW',
            'Less than a month': 'LESS_1M',
            '1 - 2 months': '1_2M',
            '3 - 5 months': '3_5M',
            '6 - 11 months': '6_11M',
            '12 months and over': '12M_PLUS',
            '"New unemployed" in Labour market': 'NEW_UNEMP',
            'Percentage (%) of "New unemployed" in Labour market': 'PCT_NEW_UNEMP',
            'Percentage (%) of long term unemployed': 'PCT_LONG_TERM'
        })
        
        sdmx_df['DATA_TYPE_CODE'] = sdmx_df['DATA_TYPE'].map({
            'Absolute': 'ABS',
            'Percentage': 'PCT'
        })
        
        # Select SDMX columns
        sdmx_columns = [
            'TIME_PERIOD', 'YEAR', 'QUARTER', 'QUARTER_NUM',
            'DURATION_CATEGORY', 'DURATION_CATEGORY_CODE', 'DURATION_CATEGORY_NAME',
            'DATA_TYPE', 'DATA_TYPE_CODE',
            'OBS_VALUE', 'OBS_STATUS', 'UNIT_MULT', 'DECIMALS',
            'UNIT', 'FREQ'
        ]
        
        return sdmx_df[sdmx_columns]
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of parsed data"""
        if self.parsed_data is None:
            return {}
        
        summary = {
            'total_observations': len(self.parsed_data),
            'years_covered': sorted(self.parsed_data['YEAR'].unique()),
            'duration_categories': sorted(self.parsed_data['DURATION_CATEGORY'].unique()),
            'data_types': sorted(self.parsed_data['DATA_TYPE'].unique()),
            'date_range': {
                'start': self.parsed_data['TIME_PERIOD'].min(),
                'end': self.parsed_data['TIME_PERIOD'].max()
            }
        }
        
        return summary
    
    def save_to_excel(self, output_path: str = None) -> str:
        """Save parsed data to Excel"""
        if self.parsed_data is None:
            raise ValueError("No data to save. Run parse() first.")
        
        if output_path is None:
            output_path = "assets/prepared/lfs_ts_qq_06_parsed.xlsx"
        
        # Create output directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to Excel
        self.parsed_data.to_excel(output_path, index=False)
        logger.info(f"Data saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    # File path
    file_path = "assets/LFS/A0101_SJO01_TS_QQ_01_2001_01_2025_06_F_EN.xlsx"
    
    # Create parser
    parser = TS_QQ_06_Parser(file_path)
    
    # Parse data
    parsed_data = parser.parse()
    
    if not parsed_data.empty:
        # Get summary
        summary = parser.get_summary_stats()
        
        # Print summary
        print("\n=== TS QQ 06 PARSING SUMMARY ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # Show first few rows
        print("\n=== FIRST 20 ROWS ===")
        print(parsed_data.head(20))
        print(f"\nData shape: {parsed_data.shape}")
        
        # Save to Excel
        output_path = parser.save_to_excel()
        print(f"\nData saved to: {output_path}")
        
        print("\nTS QQ 06 parsing completed successfully!")
    else:
        print("Parsing failed - no data extracted")

if __name__ == "__main__":
    main()
