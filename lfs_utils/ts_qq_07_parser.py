#!/usr/bin/env python3
"""
TS QQ 07 Parser - Full-time vs Part-time Employment
Parses quarterly employment data by work schedule (full-time vs part-time) and reasons.
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

class TS_QQ_07_Parser:
    """Parser for TS QQ 07 - Full-time vs Part-time Employment"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parsed_data = None
        self.df = None
        
        # Employment categories
        self.employment_categories = {
            'TOTAL': 'Total employed',
            'a) Full time': 'Full time employment',
            'b) Part time , because': 'Part time employment'
        }
        
        # Part-time reason categories (these may vary by time period)
        self.part_time_reasons = {
            'Looking after children or incapacitated adults': 'Looking after children or incapacitated adults',
            'Person is undergoing school education or training': 'Person is undergoing school education or training',
            'Of own illness or disability': 'Of own illness or disability',
            'Person could not find full time job': 'Person could not find full time job',
            'Person did not want full time job': 'Person did not want full time job',
            'Of other reasons': 'Of other reasons',
            'No reason declared': 'No reason declared'
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
            'absolute_sections': [],
            'percentage_sections': []
        }
        
        # Look for section markers
        for idx, row in self.df.iterrows():
            row_str = str(row[0]).strip()
            if pd.notna(row[0]):
                if 'Ι.  ABSOLUTE NUMBERS' in row_str or 'Ι. ABSOLUTE NUMBERS' in row_str:
                    sections['absolute_sections'].append(idx)
                elif 'II, PERCENTAGES' in row_str or 'II. PERCENTAGES' in row_str:
                    sections['percentage_sections'].append(idx)
        
        logger.info(f"Identified {len(sections['absolute_sections'])} absolute sections and {len(sections['percentage_sections'])} percentage sections")
        return sections
    
    def extract_years_from_header(self, row_idx: int) -> List[Tuple[int, int]]:
        """Extract years and their column positions from header row"""
        years = []
        row = self.df.iloc[row_idx]
        
        logger.info(f"Extracting years from row {row_idx}: {row[0]}")
        
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
        
        logger.info(f"Total years found: {len(years)}")
        return years
    
    def parse_absolute_section(self, section_start: int) -> List[Dict]:
        """Parse an absolute numbers section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and any(marker in str(self.df.iloc[idx, 0]) for marker in ['Ι.', 'II,', 'II.']):
                section_end = idx
                break
        
        # Find year headers - look in the row after the section marker
        years = self.extract_years_from_header(section_start + 1)
        if not years:
            logger.warning("No years found in absolute section")
            return data_points
        
        # Process each row in the section, starting from row after the year header
        for row_idx in range(section_start + 2, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[0]) or str(row[0]).strip() == '':
                continue
            
            # Check if this is an employment category row
            category_name = str(row[0]).strip()
            if category_name in self.employment_categories:
                
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
                                'EMPLOYMENT_CATEGORY': category_name,
                                'EMPLOYMENT_CATEGORY_NAME': self.employment_categories[category_name],
                                'PART_TIME_REASON': 'N/A',
                                'PART_TIME_REASON_NAME': 'N/A',
                                'DATA_TYPE': 'Absolute',
                                'VALUE': value,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
            
            # Check if this is a part-time reason row (indented)
            elif category_name in self.part_time_reasons:
                
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
                                'EMPLOYMENT_CATEGORY': 'b) Part time , because',
                                'EMPLOYMENT_CATEGORY_NAME': 'Part time employment',
                                'PART_TIME_REASON': category_name,
                                'PART_TIME_REASON_NAME': self.part_time_reasons[category_name],
                                'DATA_TYPE': 'Absolute',
                                'VALUE': value,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from absolute section")
        return data_points
    
    def parse_percentage_section(self, section_start: int) -> List[Dict]:
        """Parse a percentage section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and any(marker in str(self.df.iloc[idx, 0]) for marker in ['Ι.', 'II,', 'II.']):
                section_end = idx
                break
        
        # Find year headers - look in the row after the section marker
        years = self.extract_years_from_header(section_start + 1)
        if not years:
            logger.warning("No years found in percentage section")
            return data_points
        
        # Process each row in the section, starting from row after the year header
        for row_idx in range(section_start + 2, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[0]) or str(row[0]).strip() == '':
                continue
            
            # Check if this is an employment category row
            category_name = str(row[0]).strip()
            if category_name in self.employment_categories:
                
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
                                'EMPLOYMENT_CATEGORY': category_name,
                                'EMPLOYMENT_CATEGORY_NAME': self.employment_categories[category_name],
                                'PART_TIME_REASON': 'N/A',
                                'PART_TIME_REASON_NAME': 'N/A',
                                'DATA_TYPE': 'Percentage',
                                'VALUE': value,
                                'UNIT': 'Percentage',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from percentage section")
        return data_points
    
    def parse(self) -> pd.DataFrame:
        """Main parsing method"""
        logger.info("Starting TS QQ 07 parsing...")
        
        # Load data
        self.load_data()
        
        # Identify sections
        sections = self.identify_sections()
        
        # Parse all sections
        all_data = []
        
        # Parse absolute sections
        for section_start in sections['absolute_sections']:
            data = self.parse_absolute_section(section_start)
            all_data.extend(data)
        
        # Parse percentage sections
        for section_start in sections['percentage_sections']:
            data = self.parse_percentage_section(section_start)
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
        
        # Sort by time and category
        df_clean = df_clean.sort_values(['YEAR', 'QUARTER_NUM', 'EMPLOYMENT_CATEGORY', 'PART_TIME_REASON'])
        
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
        sdmx_df['EMPLOYMENT_CATEGORY_CODE'] = sdmx_df['EMPLOYMENT_CATEGORY'].map({
            'TOTAL': 'TOT',
            'a) Full time': 'FULL_TIME',
            'b) Part time , because': 'PART_TIME'
        })
        
        sdmx_df['PART_TIME_REASON_CODE'] = sdmx_df['PART_TIME_REASON'].map({
            'N/A': 'N/A',
            'Looking after children or incapacitated adults': 'CHILDCARE',
            'Person is undergoing school education or training': 'EDUCATION',
            'Of own illness or disability': 'ILLNESS',
            'Person could not find full time job': 'NO_FULL_TIME',
            'Person did not want full time job': 'PREFERENCE',
            'Of other reasons': 'OTHER',
            'No reason declared': 'NO_REASON'
        })
        
        sdmx_df['DATA_TYPE_CODE'] = sdmx_df['DATA_TYPE'].map({
            'Absolute': 'ABS',
            'Percentage': 'PCT'
        })
        
        # Select SDMX columns
        sdmx_columns = [
            'TIME_PERIOD', 'YEAR', 'QUARTER', 'QUARTER_NUM',
            'EMPLOYMENT_CATEGORY', 'EMPLOYMENT_CATEGORY_CODE', 'EMPLOYMENT_CATEGORY_NAME',
            'PART_TIME_REASON', 'PART_TIME_REASON_CODE', 'PART_TIME_REASON_NAME',
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
            'employment_categories': sorted(self.parsed_data['EMPLOYMENT_CATEGORY'].unique()),
            'part_time_reasons': sorted(self.parsed_data['PART_TIME_REASON'].unique()),
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
            output_path = "assets/prepared/lfs_ts_qq_07_parsed.xlsx"
        
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
    file_path = "assets/LFS/A0101_SJO01_TS_QQ_01_2001_01_2025_07_F_EN.xlsx"
    
    # Create parser
    parser = TS_QQ_07_Parser(file_path)
    
    # Parse data
    parsed_data = parser.parse()
    
    if not parsed_data.empty:
        # Get summary
        summary = parser.get_summary_stats()
        
        # Print summary
        print("\n=== TS QQ 07 PARSING SUMMARY ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # Show first few rows
        print("\n=== FIRST 20 ROWS ===")
        print(parsed_data.head(20))
        print(f"\nData shape: {parsed_data.shape}")
        
        # Save to Excel
        output_path = parser.save_to_excel()
        print(f"\nData saved to: {output_path}")
        
        print("\nTS QQ 07 parsing completed successfully!")
    else:
        print("Parsing failed - no data extracted")

if __name__ == "__main__":
    main()
