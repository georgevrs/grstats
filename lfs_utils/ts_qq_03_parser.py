#!/usr/bin/env python3
"""
TS QQ 03 Parser - Economic Activity by NACE Classification
Parses quarterly employment data by economic activity branches and aggregated sectors.
Handles both NACE Rev. 1 (2001-2007) and NACE Rev. 2 (2008-2025) classifications.
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

class TS_QQ_03_Parser:
    """Parser for TS QQ 03 - Economic Activity by NACE Classification"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parsed_data = None
        self.df = None
        
        # NACE Rev. 1 classifications (2001-2007)
        self.nace_rev1_activities = {
            'A': 'Agriculture, animal breeding, hunting and forestry',
            'B': 'Fishing',
            'C': 'Mining and quarrying',
            'D': 'Manufacturing',
            'E': 'Electricity, gas, steam and water supply',
            'F': 'Construction',
            'G': 'Wholesale and retail trade; repair of motor vehicles, motorcycles and personal and household goods',
            'H': 'Hotels and restaurants',
            'I': 'Transport, storage and communication',
            'J': 'Financial intermediation',
            'K': 'Real estate, renting and business activities',
            'L': 'Public administration and defence; compulsory social security',
            'M': 'Education',
            'N': 'Health and social work',
            'O': 'Other community, social and personal service activities',
            'P': 'Private households with employed persons',
            'Q': 'Extra-territorial organizations and bodies'
        }
        
        # NACE Rev. 2 classifications (2008-2025)
        self.nace_rev2_activities = {
            'A': 'Agriculture, forestry and fishing',
            'B': 'Mining and quarrying',
            'C': 'Manufacturing',
            'D': 'Electricity, gas, steam and air conditioning supply',
            'E': 'Water supply; sewerage, waste management and remediation activities',
            'F': 'Construction',
            'G': 'Wholesale and retail trade; repair of motor vehicles and motorcycles',
            'H': 'Transportation and storage',
            'I': 'Accommodation and food service activities',
            'J': 'Information and communication',
            'K': 'Financial and insurance activities',
            'L': 'Real estate activities',
            'M': 'Professional, scientific and technical activities',
            'N': 'Administrative and support service activities',
            'O': 'Public administration and defence; compulsory social security',
            'P': 'Education',
            'Q': 'Human health and social work activities',
            'R': 'Arts, entertainment and recreation',
            'S': 'Other service activities',
            'T': 'Activities of households as employers',
            'U': 'Activities of extraterritorial organisations and bodies'
        }
        
        # Aggregated sectors
        self.aggregated_sectors = {
            'Primary sector': 'Primary sector',
            'Secondary sector': 'Secondary sector',
            'Tertiary sector': 'Tertiary sector'
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
            'nace_rev1_branches': [],
            'nace_rev1_aggregated': [],
            'nace_rev2_branches': [],
            'nace_rev2_aggregated': []
        }
        
        for idx, row in self.df.iterrows():
            row_str = str(row[0]).strip()
            
            # Look for Greek letter Α (Alpha) - indicates branches section
            if row_str == 'Α':
                # Check if this is NACE Rev. 1 or Rev. 2 based on position
                # NACE Rev. 1 sections are in the first part of the file
                if idx < 90:  # Before the NOTE about NACE Rev. 2
                    sections['nace_rev1_branches'].append(idx)
                else:
                    sections['nace_rev2_branches'].append(idx)
            
            # Look for Greek letter Β (Beta) - indicates aggregated section
            elif row_str == 'Β':
                # Check if this is NACE Rev. 1 or Rev. 2 based on position
                if idx < 90:  # Before the NOTE about NACE Rev. 2
                    sections['nace_rev1_aggregated'].append(idx)
                else:
                    sections['nace_rev2_aggregated'].append(idx)
        
        logger.info(f"Identified sections: {sections}")
        return sections
    
    def extract_years_from_header(self, row_idx: int) -> List[Tuple[int, int]]:
        """Extract years and their column positions from header row"""
        years = []
        row = self.df.iloc[row_idx]
        
        for col_idx, cell in enumerate(row):
            if pd.notna(cell) and isinstance(cell, str):
                # Look for patterns like "1st quarter 2001", "2d quarter 2001", etc.
                quarter_year_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+quarter\s+(\d{4})', cell)
                if quarter_year_match:
                    quarter_num = int(quarter_year_match.group(1))
                    year = int(quarter_year_match.group(2))
                    if 2000 <= year <= 2030:
                        years.append((col_idx, year, quarter_num))
                        logger.info(f"Found {quarter_num} quarter {year} at column {col_idx}")
        
        return years
    
    def parse_nace_rev1_branches(self, section_start: int) -> List[Dict]:
        """Parse NACE Rev. 1 branches section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and str(self.df.iloc[idx, 0]).strip() in ['Α', 'Β']:
                section_end = idx
                break
        
        # Find year headers
        years = self.extract_years_from_header(section_start)
        if not years:
            logger.warning("No years found in NACE Rev. 1 branches section")
            return data_points
        
        # Process each row in the section
        for row_idx in range(section_start + 1, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[1]) or str(row[1]).strip() == '':
                continue
            
            # Check if this is an activity row - look in column 1
            activity_text = str(row[1]).strip()
            
            # Extract activity code (e.g., "A" from "A. Agriculture...")
            if activity_text.startswith('Total employed'):
                activity_code = 'Total employed'
                activity_name = 'Total employed'
            elif '.' in activity_text and activity_text[0] in self.nace_rev1_activities:
                activity_code = activity_text[0]  # Extract just the letter
                activity_name = self.nace_rev1_activities[activity_code]
            else:
                continue  # Skip rows that don't match our patterns
            
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
                            'ACTIVITY_CODE': activity_code,
                            'ACTIVITY_NAME': activity_name,
                            'NACE_VERSION': 'Rev. 1',
                            'SECTOR_TYPE': 'Branch',
                            'VALUE': value,
                            'UNIT': 'Thousands of persons',
                            'FREQ': 'Q'
                        })
                    except (ValueError, TypeError):
                        continue
        
        logger.info(f"Parsed {len(data_points)} data points from NACE Rev. 1 branches")
        return data_points
    
    def parse_nace_rev1_aggregated(self, section_start: int) -> List[Dict]:
        """Parse NACE Rev. 1 aggregated sectors section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and str(self.df.iloc[idx, 0]).strip() in ['Α', 'Β']:
                section_end = idx
                break
        
        # Find year headers
        years = self.extract_years_from_header(section_start)
        if not years:
            logger.warning("No years found in NACE Rev. 1 aggregated section")
            return data_points
        
        # Process each row in the section
        for row_idx in range(section_start + 1, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[1]) or str(row[1]).strip() == '':
                continue
            
            # Check if this is a sector row - look in column 1
            sector_name = str(row[1]).strip()
            if sector_name in self.aggregated_sectors or sector_name == 'Total employed':
                
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
                                'ACTIVITY_CODE': sector_name,
                                'ACTIVITY_NAME': sector_name,
                                'NACE_VERSION': 'Rev. 1',
                                'SECTOR_TYPE': 'Aggregated',
                                'VALUE': value,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from NACE Rev. 1 aggregated")
        return data_points
    
    def parse_nace_rev2_branches(self, section_start: int) -> List[Dict]:
        """Parse NACE Rev. 2 branches section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and str(self.df.iloc[idx, 0]).strip() in ['Α', 'Β']:
                section_end = idx
                break
        
        # Find year headers
        years = self.extract_years_from_header(section_start)
        if not years:
            logger.warning("No years found in NACE Rev. 2 branches section")
            return data_points
        
        # Process each row in the section
        for row_idx in range(section_start + 1, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[1]) or str(row[1]).strip() == '':
                continue
            
            # Check if this is an activity row - look in column 1
            activity_text = str(row[1]).strip()
            
            # Extract activity code (e.g., "A" from "A. Agriculture...")
            if activity_text.startswith('Total employed'):
                activity_code = 'Total employed'
                activity_name = 'Total employed'
            elif '.' in activity_text and activity_text[0] in self.nace_rev2_activities:
                activity_code = activity_text[0]  # Extract just the letter
                activity_name = self.nace_rev2_activities[activity_code]
            else:
                continue  # Skip rows that don't match our patterns
            
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
                            'ACTIVITY_CODE': activity_code,
                            'ACTIVITY_NAME': activity_name,
                            'NACE_VERSION': 'Rev. 2',
                            'SECTOR_TYPE': 'Branch',
                            'VALUE': value,
                            'UNIT': 'Thousands of persons',
                            'FREQ': 'Q'
                        })
                    except (ValueError, TypeError):
                        continue
        
        logger.info(f"Parsed {len(data_points)} data points from NACE Rev. 2 branches")
        return data_points
    
    def parse_nace_rev2_aggregated(self, section_start: int) -> List[Dict]:
        """Parse NACE Rev. 2 aggregated sectors section"""
        data_points = []
        
        # Find the next section or end of data
        section_end = len(self.df)
        for idx in range(section_start + 1, len(self.df)):
            if pd.notna(self.df.iloc[idx, 0]) and str(self.df.iloc[idx, 0]).strip() in ['Α', 'Β']:
                section_end = idx
                break
        
        # Find year headers
        years = self.extract_years_from_header(section_start)
        if not years:
            logger.warning("No years found in NACE Rev. 2 aggregated section")
            return data_points
        
        # Process each row in the section
        for row_idx in range(section_start + 1, section_end):
            row = self.df.iloc[row_idx]
            
            # Skip empty rows
            if pd.isna(row[1]) or str(row[1]).strip() == '':
                continue
            
            # Check if this is a sector row - look in column 1
            sector_name = str(row[1]).strip()
            if sector_name in self.aggregated_sectors or sector_name == 'Total employed':
                
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
                                'ACTIVITY_CODE': sector_name,
                                'ACTIVITY_NAME': sector_name,
                                'NACE_VERSION': 'Rev. 2',
                                'SECTOR_TYPE': 'Aggregated',
                                'VALUE': value,
                                'UNIT': 'Thousands of persons',
                                'FREQ': 'Q'
                            })
                        except (ValueError, TypeError):
                            continue
        
        logger.info(f"Parsed {len(data_points)} data points from NACE Rev. 2 aggregated")
        return data_points
    
    def parse(self) -> pd.DataFrame:
        """Main parsing method"""
        logger.info("Starting TS QQ 03 parsing...")
        
        # Load data
        self.load_data()
        
        # Identify sections
        sections = self.identify_sections()
        
        # Parse all sections
        all_data = []
        
        # Parse NACE Rev. 1 sections
        for section_start in sections['nace_rev1_branches']:
            data = self.parse_nace_rev1_branches(section_start)
            all_data.extend(data)
        
        for section_start in sections['nace_rev1_aggregated']:
            data = self.parse_nace_rev1_aggregated(section_start)
            all_data.extend(data)
        
        # Parse NACE Rev. 2 sections
        for section_start in sections['nace_rev2_branches']:
            data = self.parse_nace_rev2_branches(section_start)
            all_data.extend(data)
        
        for section_start in sections['nace_rev2_aggregated']:
            data = self.parse_nace_rev2_aggregated(section_start)
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
        
        # Sort by time and activity
        df_clean = df_clean.sort_values(['YEAR', 'QUARTER_NUM', 'ACTIVITY_CODE'])
        
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
        
        # Create dimension codes for SDMX
        sdmx_df['ACTIVITY_CODE_SDMX'] = sdmx_df['ACTIVITY_CODE'].map({
            'Total employed': 'TOT',
            'Primary sector': 'PRIM',
            'Secondary sector': 'SEC',
            'Tertiary sector': 'TERT',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'D': 'D',
            'E': 'E',
            'F': 'F',
            'G': 'G',
            'H': 'H',
            'I': 'I',
            'J': 'J',
            'K': 'K',
            'L': 'L',
            'M': 'M',
            'N': 'N',
            'O': 'O',
            'P': 'P',
            'Q': 'Q',
            'R': 'R',
            'S': 'S',
            'T': 'T',
            'U': 'U'
        })
        
        sdmx_df['NACE_VERSION_CODE'] = sdmx_df['NACE_VERSION'].map({
            'Rev. 1': 'NACE1',
            'Rev. 2': 'NACE2'
        })
        
        sdmx_df['SECTOR_TYPE_CODE'] = sdmx_df['SECTOR_TYPE'].map({
            'Branch': 'BRANCH',
            'Aggregated': 'AGG'
        })
        
        # Select SDMX columns
        sdmx_columns = [
            'TIME_PERIOD', 'YEAR', 'QUARTER', 'QUARTER_NUM',
            'ACTIVITY_CODE', 'ACTIVITY_CODE_SDMX', 'ACTIVITY_NAME',
            'NACE_VERSION', 'NACE_VERSION_CODE', 'SECTOR_TYPE', 'SECTOR_TYPE_CODE',
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
            'nace_versions': sorted(self.parsed_data['NACE_VERSION'].unique()),
            'sector_types': sorted(self.parsed_data['SECTOR_TYPE'].unique()),
            'activities': sorted(self.parsed_data['ACTIVITY_CODE'].unique()),
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
            output_path = "assets/prepared/lfs_ts_qq_03_parsed.xlsx"
        
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
    file_path = "assets/LFS/A0101_SJO01_TS_QQ_01_2001_01_2025_03_F_EN.xlsx"
    
    # Create parser
    parser = TS_QQ_03_Parser(file_path)
    
    # Parse data
    parsed_data = parser.parse()
    
    if not parsed_data.empty:
        # Get summary
        summary = parser.get_summary_stats()
        
        # Print summary
        print("\n=== TS QQ 03 PARSING SUMMARY ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # Show first few rows
        print("\n=== FIRST 20 ROWS ===")
        print(parsed_data.head(20))
        print(f"\nData shape: {parsed_data.shape}")
        
        # Save to Excel
        output_path = parser.save_to_excel()
        print(f"\nData saved to: {output_path}")
        
        print("\nTS QQ 03 parsing completed successfully!")
    else:
        print("Parsing failed - no data extracted")

if __name__ == "__main__":
    main()
