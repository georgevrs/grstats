#!/usr/bin/env python3
"""
TS QQ 05 Parser - Occupational Status by Employment Type
Parses quarterly employment data by occupational status categories.
Handles both absolute numbers and percentages (base=100, 1st quarter 2001).
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

class TS_QQ_05_Parser:
    """Parser for TS QQ 05 - Occupational Status by Employment Type"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parsed_data = None
        self.df = None
        
        # Occupational status categories
        self.occupational_categories = {
            'Total': 'Total employed',
            'Employers': 'Employers',
            'Own account workers': 'Own account workers',
            'Salaried employees': 'Salaried employees',
            'Unpaid family workers': 'Unpaid family workers'
        }
        
        # Data types
        self.data_types = {
            'ABSOLUTE NUMBERS': 'Absolute',
            'PERCETANGES': 'Percentage'  # Note: typo in original data
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
            'absolute_numbers': [],
            'percentages': []
        }
        
        for idx, row in self.df.iterrows():
            row_str = str(row[0]).strip()
            
            # Look for Roman numeral Ι (Greek Iota) with spaces - indicates absolute numbers section
            if row_str.startswith('Ι.'):
                sections['absolute_numbers'].append(idx)
            
            # Look for Roman numeral II (Latin I) with spaces - indicates percentages section
            elif row_str.startswith('II.'):
                sections['percentages'].append(idx)
        
        logger.info(f"Identified sections: {sections}")
        return sections
    
    def extract_years_from_header(self, row_idx: int) -> List[Tuple[int, int]]:
        """Extract years and their column positions from header row"""
        years = []
        row = self.df.iloc[row_idx]
        
        for col_idx, cell in enumerate(row):
            if pd.notna(cell) and isinstance(cell, str):
                # Look for patterns like "1st quarter 2001", "2nd quarter 2001", etc.
                quarter_year_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+quarter\s+(\d{4})', cell)
                if quarter_year_match:
                    quarter_num = int(quarter_year_match.group(1))
                    year = int(quarter_year_match.group(2))
                    if 2000 <= year <= 2030:
                        years.append((col_idx, year, quarter_num))
                        logger.info(f"Found {quarter_num} quarter {year} at column {col_idx}")
        
        return years
    
    def parse_absolute_numbers_section(self, section_start: int) -> List[Dict]:
        """Parse absolute numbers section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and str(self.df.iloc[idx, 0]).strip().startswith(('Ι.', 'II.')):
                section_end = idx
                break
        
        # Find year headers - look in the row after "Occupational status"
        header_row = section_start + 1  # Row with "Occupational status"
        years = self.extract_years_from_header(header_row)
        if not years:
            logger.warning("No years found in absolute numbers section")
            return data_points
        
        # Process each row in the section, starting from row after the year header
        for row_idx in range(header_row + 1, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[0]) or str(row[0]).strip() == '':
                continue
            
            # Check if this is an occupational status row
            status_name = str(row[0]).strip()
            if status_name in self.occupational_categories:
                
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
                                'OCCUPATIONAL_STATUS': status_name,
                                'OCCUPATIONAL_STATUS_NAME': self.occupational_categories[status_name],
                                'DATA_TYPE': 'Absolute',
                                'VALUE': value,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from absolute numbers section")
        return data_points
    
    def parse_percentages_section(self, section_start: int) -> List[Dict]:
        """Parse percentages section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and str(self.df.iloc[idx, 0]).strip().startswith(('Ι.', 'II.')):
                section_end = idx
                break
        
        # For percentages sections, we need to find the corresponding absolute numbers section
        # to get the year/quarter column mapping
        # Look for the previous absolute numbers section
        year_mapping = None
        for abs_section in reversed([s for s in self.sections['absolute_numbers'] if s < section_start]):
            # Extract years from the absolute numbers section
            header_row = abs_section + 1  # Row with "Occupational status"
            year_mapping = self.extract_years_from_header(header_row)
            if year_mapping:
                logger.info(f"Using year mapping from absolute numbers section at row {abs_section}")
                break
        
        if not year_mapping:
            logger.warning("No year mapping found for percentages section")
            return data_points
        
        # Process each row in the section, starting from row after the section marker
        for row_idx in range(section_start + 1, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[0]) or str(row[0]).strip() == '':
                continue
            
            # Check if this is an occupational status row
            status_name = str(row[0]).strip()
            if status_name in self.occupational_categories:
                
                # Extract data for each year/quarter using the same column mapping
                for col_idx, year, quarter_num in year_mapping:
                    if col_idx < len(row) and pd.notna(row[col_idx]):
                        try:
                            value = float(row[col_idx])
                            quarter_name = f"Q{quarter_num}"
                            
                            data_points.append({
                                'YEAR': year,
                                'QUARTER': quarter_name,
                                'QUARTER_NUM': quarter_num,
                                'TIME_PERIOD': f"{year}-{quarter_name}",
                                'OCCUPATIONAL_STATUS': status_name,
                                'OCCUPATIONAL_STATUS_NAME': self.occupational_categories[status_name],
                                'DATA_TYPE': 'Percentage',
                                'VALUE': value,
                                'UNIT': 'Percentage (base=100, Q1 2001)',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from percentages section")
        return data_points
    
    def parse(self) -> pd.DataFrame:
        """Main parsing method"""
        logger.info("Starting TS QQ 05 parsing...")
        
        # Load data
        self.load_data()
        
        # Identify sections
        self.sections = self.identify_sections()
        
        # Parse all sections
        all_data = []
        
        # Parse absolute numbers sections
        for section_start in self.sections['absolute_numbers']:
            data = self.parse_absolute_numbers_section(section_start)
            all_data.extend(data)
        
        # Parse percentages sections
        for section_start in self.sections['percentages']:
            data = self.parse_percentages_section(section_start)
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
        
        # Sort by time and occupational status
        df_clean = df_clean.sort_values(['YEAR', 'QUARTER_NUM', 'OCCUPATIONAL_STATUS'])
        
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
        sdmx_df['OCCUPATIONAL_STATUS_CODE'] = sdmx_df['OCCUPATIONAL_STATUS'].map({
            'Total': 'TOT',
            'Employers': 'EMP',
            'Own account workers': 'OAW',
            'Salaried employees': 'SAL',
            'Unpaid family workers': 'UFW'
        })
        
        sdmx_df['DATA_TYPE_CODE'] = sdmx_df['DATA_TYPE'].map({
            'Absolute': 'ABS',
            'Percentage': 'PCT'
        })
        
        # Select SDMX columns
        sdmx_columns = [
            'TIME_PERIOD', 'YEAR', 'QUARTER', 'QUARTER_NUM',
            'OCCUPATIONAL_STATUS', 'OCCUPATIONAL_STATUS_CODE', 'OCCUPATIONAL_STATUS_NAME',
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
            'occupational_statuses': sorted(self.parsed_data['OCCUPATIONAL_STATUS'].unique()),
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
            output_path = "assets/prepared/lfs_ts_qq_05_parsed.xlsx"
        
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
    file_path = "assets/LFS/A0101_SJO01_TS_QQ_01_2001_01_2025_05_F_EN.xlsx"
    
    # Create parser
    parser = TS_QQ_05_Parser(file_path)
    
    # Parse data
    parsed_data = parser.parse()
    
    if not parsed_data.empty:
        # Get summary
        summary = parser.get_summary_stats()
        
        # Print summary
        print("\n=== TS QQ 05 PARSING SUMMARY ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # Show first few rows
        print("\n=== FIRST 20 ROWS ===")
        print(parsed_data.head(20))
        print(f"\nData shape: {parsed_data.shape}")
        
        # Save to Excel
        output_path = parser.save_to_excel()
        print(f"\nData saved to: {output_path}")
        
        print("\nTS QQ 05 parsing completed successfully!")
    else:
        print("Parsing failed - no data extracted")

if __name__ == "__main__":
    main()
