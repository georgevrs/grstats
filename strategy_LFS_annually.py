#!/usr/bin/env python3
"""
CORRECTED PROFESSIONAL ANNUAL LFS DATA ENGINEERING SOLUTION
Based on ACTUAL data model discovered through thorough analysis.
"""

import pandas as pd
import os
import logging
import re
from collections import defaultdict
from datetime import datetime
import numpy as np
from typing import List, Dict, Any, Tuple

# Set up professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('annual_lfs_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CORRECTED SDMX MAPPING BASED ON ACTUAL DATA MODEL
REGIONS_MAPPING = {
    'Anatoliki Makedonia-Thraki': 'EL51',
    'Kentriki Makedonia': 'EL52', 
    'Dytiki Makedonia': 'EL53',
    'Ipeiros': 'EL54',
    'Thessalia': 'EL61',
    'Ionia Nissia': 'EL62',
    'Dytiki Ellada': 'EL63',
    'Sterea Ellada': 'EL64',
    'Attiki': 'EL30',
    'Peloponnisos': 'EL65',
    'Voreio Aigaio': 'EL41',
    'Notio Aigaio': 'EL42',
    'Kriti': 'EL43',
    'COUNTRY TOTAL': 'GR',
    'GREECE, TOTAL': 'GR'
}

ECONOMIC_SECTORS_MAPPING = {
    'NACE rev2: Agriculture, forestry and fishing': 'A',
    'NACE rev2: Mining and quarrying': 'B',
    'NACE rev2: Manufacturing': 'C',
    'NACE rev2: Electricity, gas, steam and air conditioning supply': 'D',
    'NACE rev2: Water supply; sewerage, waste management and remediation activities': 'E',
    'NACE rev2: Construction': 'F',
    'NACE rev2: Wholesale and retail trade; repair of motor vehicles and motorcycles': 'G',
    'NACE rev2: Transportation and storage': 'H',
    'NACE rev2: Accommodation and food service activities': 'I',
    'NACE rev2: Information and communication': 'J',
    'NACE rev2: Financial and insurance activities': 'K',
    'NACE rev2: Real estate activities': 'L',
    'NACE rev2: Professional, scientific and technical activities': 'M',
    'NACE rev2: Administrative and support service activities': 'N',
    'NACE rev2: Public administration and defence; compulsory social security': 'O',
    'NACE rev2: Education': 'P',
    'NACE rev2: Human health and social work activities': 'Q',
    'NACE rev2: Arts, entertainment and recreation': 'R',
    'NACE rev2: Other service activities': 'S',
    'NACE rev2: Activities of households as employers; undifferentiated goods- and services-producing activities of households': 'T',
    'NACE rev2: Activities of extraterritorial organisations and bodies': 'U',
    'Agriculture, forestry, animal husbandry, fishing': 'A',
    'Industry including energy': 'C',
    'Trade, hotels and restaurants, transport and communication': 'G',
    'Financial, real estate, renting and business activities': 'K',
    'Other service activities': 'S'
}

OCCUPATIONS_MAPPING = {
    'ISCO-08: Managers': '1',
    'ISCO-08: Professionals': '2',
    'ISCO-08: Technicians and associate professionals': '3',
    'ISCO-08: Clerical support workers': '4',
    'ISCO-08: Service and sales workers': '5',
    'ISCO-08: Skilled agricultural, forestry and fishery workers': '6',
    'ISCO-08: Craft and related trades workers': '7',
    'ISCO-08: Plant and machine operators and assemblers': '8',
    'ISCO-08: Elementary occupations': '9',
    'ISCO-08: Not possible to classify': 'X',
    'ISCO-08: Did not answer': 'Z',
    'Highly skilled non- manual': '1-3',
    'Low skilled non-manual': '4-5',
    'Skilled manual': '6-8'
}

AGE_GROUPS_MAPPING = {
    '15-19': '15-19',
    '20-24': '20-24', 
    '25-29': '25-29',
    '30-44': '30-44',
    '45-64': '45-64',
    '65+': '65+',
    'Total': 'TOTAL'
}

GENDER_MAPPING = {
    'Males': 'M',
    'Females': 'F',
    'Men': 'M',
    'Women': 'W',
    'Total': 'TOTAL'
}

EDUCATION_MAPPING = {
    'Attended no school / Did not complete primary education': 'PRIMARY',
    'Primary': 'PRIMARY',
    'Upper secondary': 'SECONDARY',
    'Post secondary vocational': 'POST_SEC',
    'Tertiary': 'TERTIARY'
}

EMPLOYMENT_STATUS_MAPPING = {
    'POP': 'POPULATION',
    'EMP': 'EMPLOYED',
    'UNE': 'UNEMPLOYED',
    'INA': 'INACTIVE',
    'LF': 'LABOUR_FORCE',
    'Total': 'TOTAL'
}

NATIONALITY_MAPPING = {
    'Greek': 'GR',
    'Non-Greek': 'NON_GR',
    'Total': 'TOTAL'
}

URBANIZATION_MAPPING = {
    'Urban': 'URBAN',
    'Rural': 'RURAL',
    'Total': 'TOTAL'
}

class CorrectedAnnualLFSParser:
    """CORRECTED Annual LFS Parser based on actual data model."""
    
    def __init__(self):
        self.all_data = []
        self.dimension_cache = {}
        
    def extract_time_periods_corrected(self, sheet: pd.DataFrame, file_name: str) -> List[int]:
        """CORRECTED time period extraction from Column 0."""
        logger.info(f"    🔍 CORRECTED time period extraction from {file_name}")
        
        time_periods = []
        
        # Look for years in Column 0 (first column) starting from Row 3
        for row_idx in range(3, min(100, len(sheet))):
            cell_value = sheet.iloc[row_idx, 0]
            
            if isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                time_periods.append(int(cell_value))
                logger.info(f"      ✅ Found year: {int(cell_value)} at row {row_idx}")
            elif isinstance(cell_value, str):
                # Check for year patterns in strings
                year_match = re.search(r'19[8-9][0-9]|20[0-2][0-9]', str(cell_value))
                if year_match:
                    year = int(year_match.group())
                    time_periods.append(year)
                    logger.info(f"      ✅ Found year: {year} at row {row_idx}")
        
        # Remove duplicates and sort
        time_periods = sorted(list(set(time_periods)))
        logger.info(f"      📅 Total unique time periods: {len(time_periods)}")
        
        return time_periods
    
    def extract_dimensions_corrected(self, sheet: pd.DataFrame, file_name: str) -> Dict[str, List[str]]:
        """CORRECTED dimension extraction from Column 1."""
        logger.info(f"    🔍 CORRECTED dimension extraction from {file_name}")
        
        dimensions = {
            'regions': [],
            'economic_sectors': [],
            'age_groups': [],
            'genders': [],
            'education_levels': [],
            'nationality': [],
            'urbanization_levels': [],
            'occupations': [],
            'employment_statuses': []
        }
        
        # CRITICAL FIX: Extract dimensions from Column 1 (second column) starting from Row 3
        for row_idx in range(3, min(200, len(sheet))):
            if sheet.shape[1] > 1:  # Make sure we have at least 2 columns
                cell_value = sheet.iloc[row_idx, 1]
                
                if pd.notna(cell_value) and isinstance(cell_value, str):
                    cell_str = str(cell_value).strip()
                    
                    # Skip totals and empty values
                    if cell_str in ['TOTAL', 'TOTAL EMPLOYED', 'YEAR TOTAL', 'COUNTRY TOTAL']:
                        continue
                    
                    # Classify the dimension value
                    if any(region in cell_str for region in REGIONS_MAPPING.keys()):
                        dimensions['regions'].append(cell_str)
                        logger.info(f"      🌍 Found region: {cell_str}")
                    elif any(sector in cell_str for sector in ECONOMIC_SECTORS_MAPPING.keys()):
                        dimensions['economic_sectors'].append(cell_str)
                        logger.info(f"      🏭 Found economic sector: {cell_str}")
                    elif any(occ in cell_str for occ in OCCUPATIONS_MAPPING.keys()):
                        dimensions['occupations'].append(cell_str)
                        logger.info(f"      👷 Found occupation: {cell_str}")
                    elif any(age in cell_str for age in AGE_GROUPS_MAPPING.keys()):
                        dimensions['age_groups'].append(cell_str)
                        logger.info(f"      👥 Found age group: {cell_str}")
                    elif any(gender in cell_str for gender in GENDER_MAPPING.keys()):
                        dimensions['genders'].append(cell_str)
                        logger.info(f"      👫 Found gender: {cell_str}")
                    elif any(edu in cell_str for edu in EDUCATION_MAPPING.keys()):
                        dimensions['education_levels'].append(cell_str)
                        logger.info(f"      🎓 Found education: {edu}")
                    elif any(status in cell_str for status in EMPLOYMENT_STATUS_MAPPING.keys()):
                        dimensions['employment_statuses'].append(cell_str)
                        logger.info(f"      💼 Found employment status: {cell_str}")
                    else:
                        # Try to infer from context
                        if 'region' in cell_str.lower() or any(region_word in cell_str.lower() for region_word in ['makedonia', 'thraki', 'attiki', 'kriti', 'aigaio']):
                            dimensions['regions'].append(cell_str)
                            logger.info(f"      🌍 Inferred region: {cell_str}")
                        elif any(sector_word in cell_str.lower() for sector_word in ['agriculture', 'manufacturing', 'construction', 'services', 'trade', 'transport']):
                            dimensions['economic_sectors'].append(cell_str)
                            logger.info(f"      🏭 Inferred economic sector: {cell_str}")
                        elif any(occ_word in cell_str.lower() for occ_word in ['managers', 'professionals', 'technicians', 'clerks', 'service', 'skilled', 'unskilled']):
                            dimensions['occupations'].append(cell_str)
                            logger.info(f"      👷 Inferred occupation: {cell_str}")
        
        # Remove duplicates
        for key in dimensions:
            dimensions[key] = list(set(dimensions[key]))
            logger.info(f"      📊 {key}: {len(dimensions[key])} unique values")
        
        return dimensions
    
    def parse_data_with_corrected_context(self, sheet: pd.DataFrame, sheet_name: str, file_name: str) -> List[Dict[str, Any]]:
        """CORRECTED data parsing based on actual structure."""
        logger.info(f"    🔍 CORRECTED data parsing for {sheet_name}")
        
        data_records = []
        
        # Get time periods
        time_periods = self.extract_time_periods_corrected(sheet, file_name)
        if not time_periods:
            logger.warning(f"      ⚠️ No time periods found in {sheet_name}")
            return []
        
        # Get dimensions
        dimensions = self.extract_dimensions_corrected(sheet, file_name)
        
        # Parse data rows starting from Row 3
        for row_idx in range(3, len(sheet)):
            row_data = sheet.iloc[row_idx]
            
            # Skip rows with insufficient data
            if pd.isna(row_data.iloc[0]) or pd.isna(row_data.iloc[1]):
                continue
            
            # Extract year from Column 0
            year_cell = row_data.iloc[0]
            if not isinstance(year_cell, (int, float)) or not (1900 < year_cell < 2030):
                continue
            
            year = int(year_cell)
            
            # Extract dimension value from Column 1
            dimension_cell = row_data.iloc[1]
            if pd.isna(dimension_cell):
                continue
            
            dimension_value = str(dimension_cell).strip()
            
            # Skip totals
            if dimension_value in ['TOTAL', 'TOTAL EMPLOYED', 'YEAR TOTAL', 'COUNTRY TOTAL']:
                continue
            
            # Extract data values from Column 2+
            for col_idx in range(2, min(20, sheet.shape[1])):
                data_cell = row_data.iloc[col_idx]
                
                if pd.notna(data_cell) and isinstance(data_cell, (int, float)) and data_cell > 0:
                    # Create data record
                    record = self.create_corrected_data_record(
                        year, dimension_value, data_cell, col_idx, 
                        sheet_name, file_name, dimensions
                    )
                    
                    if record:
                        data_records.append(record)
        
        logger.info(f"      📊 Extracted {len(data_records)} data records")
        return data_records
    
    def create_corrected_data_record(self, year: int, dimension_value: str, data_value: float, 
                                   col_idx: int, sheet_name: str, file_name: str, 
                                   dimensions: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create corrected data record with proper dimension mapping."""
        
        # Determine the main dimension type based on the dimension value
        dimension_type = self.classify_dimension_type(dimension_value, dimensions)
        
        # Map the dimension value to standard codes
        mapped_value = self.map_dimension_value(dimension_value, dimension_type)
        
        # Determine indicator based on sheet name
        indicator = self.infer_indicator_from_sheet(sheet_name)
        
        # Determine unit measure based on context
        unit_measure = self.infer_unit_from_context(sheet_name, data_value)
        
        # Create the record
        record = {
            'time_period': year,
            'freq': 'A',
            'value': data_value,
            'ref_area': 'GR',
            'source_agency': 'ELSTAT',
            'unit_measure': unit_measure,
            'file_source': file_name,
            'sheet_name': sheet_name,
            'indicator': indicator,
            'region': mapped_value if dimension_type == 'region' else 'TOTAL',
            'economic_sector': mapped_value if dimension_type == 'economic_sector' else 'TOTAL',
            'age_group': mapped_value if dimension_type == 'age_group' else 'TOTAL',
            'gender': mapped_value if dimension_type == 'gender' else 'TOTAL',
            'education': mapped_value if dimension_type == 'education' else 'TOTAL',
            'nationality': mapped_value if dimension_type == 'nationality' else 'TOTAL',
            'urbanization': mapped_value if dimension_type == 'urbanization' else 'TOTAL',
            'occupation': mapped_value if dimension_type == 'occupation' else 'TOTAL',
            'employment_status': mapped_value if dimension_type == 'employment_status' else 'TOTAL'
        }
        
        return record
    
    def classify_dimension_type(self, dimension_value: str, dimensions: Dict[str, List[str]]) -> str:
        """Classify the dimension type based on the value."""
        
        if dimension_value in dimensions['regions']:
            return 'region'
        elif dimension_value in dimensions['economic_sectors']:
            return 'economic_sector'
        elif dimension_value in dimensions['occupations']:
            return 'occupation'
        elif dimension_value in dimensions['age_groups']:
            return 'age_group'
        elif dimension_value in dimensions['genders']:
            return 'gender'
        elif dimension_value in dimensions['education_levels']:
            return 'education'
        elif dimension_value in dimensions['employment_statuses']:
            return 'employment_status'
        elif dimension_value in dimensions['nationality']:
            return 'nationality'
        elif dimension_value in dimensions['urbanization_levels']:
            return 'urbanization'
        else:
            # Try to infer from the value content
            if any(region_word in dimension_value.lower() for region_word in ['makedonia', 'thraki', 'attiki', 'kriti', 'aigaio']):
                return 'region'
            elif any(sector_word in dimension_value.lower() for sector_word in ['agriculture', 'manufacturing', 'construction', 'services', 'trade', 'transport']):
                return 'economic_sector'
            elif any(occ_word in dimension_value.lower() for occ_word in ['managers', 'professionals', 'technicians', 'clerks', 'service', 'skilled', 'unskilled']):
                return 'occupation'
            else:
                return 'unknown'
    
    def map_dimension_value(self, dimension_value: str, dimension_type: str) -> str:
        """Map dimension value to standard codes."""
        
        if dimension_type == 'region':
            return REGIONS_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'economic_sector':
            return ECONOMIC_SECTORS_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'occupation':
            return OCCUPATIONS_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'age_group':
            return AGE_GROUPS_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'gender':
            return GENDER_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'education':
            return EDUCATION_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'employment_status':
            return EMPLOYMENT_STATUS_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'nationality':
            return NATIONALITY_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        elif dimension_type == 'urbanization':
            return URBANIZATION_MAPPING.get(dimension_value, f"CUSTOM_{dimension_value[:20]}")
        else:
            return f"CUSTOM_{dimension_value[:20]}"
    
    def infer_indicator_from_sheet(self, sheet_name: str) -> str:
        """Infer indicator from sheet name."""
        if 'POPUL' in sheet_name:
            return 'POPULATION'
        elif 'EMP' in sheet_name:
            return 'EMPLOYMENT'
        elif 'UNE' in sheet_name:
            return 'UNEMPLOYMENT'
        elif 'JOB' in sheet_name:
            return 'EMPLOYMENT_CHARACTERISTICS'
        elif 'SECTOR' in sheet_name:
            return 'ECONOMIC_SECTOR'
        elif 'OCCUP' in sheet_name:
            return 'OCCUPATION'
        elif 'EDUC' in sheet_name:
            return 'EDUCATION'
        elif 'STATUS' in sheet_name:
            return 'EMPLOYMENT_STATUS'
        else:
            return 'LFS_INDICATOR'
    
    def infer_unit_from_context(self, sheet_name: str, data_value: float) -> str:
        """Infer unit measure from context."""
        if data_value > 1000:
            return 'THOUSANDS'
        elif data_value > 100:
            return 'HUNDREDS'
        else:
            return 'UNITS'
    
    def extract_all_data_from_sheet_corrected(self, sheet: pd.DataFrame, sheet_name: str, file_name: str) -> List[Dict[str, Any]]:
        """CORRECTED extraction of all data from a sheet."""
        logger.info(f"    📊 CORRECTED extraction from sheet: {sheet_name}")
        
        try:
            # Parse data with corrected context
            data_records = self.parse_data_with_corrected_context(sheet, sheet_name, file_name)
            
            if data_records:
                logger.info(f"      ✅ Successfully extracted {len(data_records)} records")
            else:
                logger.warning(f"      ⚠️ No data records extracted from {sheet_name}")
            
            return data_records
            
        except Exception as e:
            logger.error(f"      ❌ Error extracting data from {sheet_name}: {e}")
            return []
    
    def parse_all_annual_lfs_files_corrected(self) -> pd.DataFrame:
        """CORRECTED parsing of all annual LFS files."""
        logger.info("🚀 STARTING CORRECTED ANNUAL LFS DATA EXTRACTION")
        
        lfs_dir = "assets/LFS"
        annual_files = [f for f in os.listdir(lfs_dir) if "TS_AN" in f and f.endswith('.xlsx')]
        
        logger.info(f"📁 Found {len(annual_files)} annual LFS files")
        
        all_data = []
        
        for file_name in annual_files:
            file_path = os.path.join(lfs_dir, file_name)
            logger.info(f"📊 Processing file: {file_name}")
            
            try:
                # Read all sheets
                xl_file = pd.ExcelFile(file_path)
                sheet_names = xl_file.sheet_names
                
                logger.info(f"  📋 Found {len(sheet_names)} sheets: {sheet_names}")
                
                # Process each sheet
                for sheet_name in sheet_names:
                    if sheet_name.lower() in ['contents', 'notes', 'metadata']:
                        continue
                    
                    logger.info(f"  🔍 Processing sheet: {sheet_name}")
                    
                    # Read sheet in chunks for memory efficiency
                    chunk_size = 1000
                    for chunk_start in range(0, 10000, chunk_size):  # Limit to first 10k rows
                        try:
                            chunk = pd.read_excel(file_path, sheet_name=sheet_name, 
                                                header=None, skiprows=chunk_start, 
                                                nrows=chunk_size)
                            
                            if chunk.empty:
                                break
                            
                            # Extract data from this chunk
                            chunk_data = self.extract_all_data_from_sheet_corrected(
                                chunk, sheet_name, file_name
                            )
                            
                            if chunk_data:
                                all_data.extend(chunk_data)
                            
                            # If we got less than chunk_size rows, we've reached the end
                            if len(chunk) < chunk_size:
                                break
                                
                        except Exception as e:
                            logger.warning(f"    ⚠️ Error reading chunk starting at row {chunk_start}: {e}")
                            continue
                
            except Exception as e:
                logger.error(f"  ❌ Error processing file {file_name}: {e}")
                continue
        
        logger.info(f"📊 Total data records extracted: {len(all_data)}")
        
        if all_data:
            # Convert to DataFrame
            df = pd.DataFrame(all_data)
            
            # Remove duplicates
            initial_count = len(df)
            df = df.drop_duplicates()
            final_count = len(df)
            duplicates_removed = initial_count - final_count
            
            logger.info(f"🧹 Removed {duplicates_removed} duplicate records")
            logger.info(f"📊 Final dataset: {len(df)} records")
            
            return df
        else:
            logger.error("❌ No data extracted from any files!")
            return pd.DataFrame()
    
    def remove_duplicates_smartly_corrected(self, df: pd.DataFrame) -> pd.DataFrame:
        """CORRECTED smart duplicate removal."""
        logger.info("🧹 CORRECTED smart duplicate removal")
        
        initial_count = len(df)
        
        # Remove exact duplicates
        df = df.drop_duplicates()
        
        # Remove duplicates based on core identifiers but preserve different dimension combinations
        core_cols = ['time_period', 'value', 'indicator', 'sheet_name']
        df = df.drop_duplicates(subset=core_cols, keep='first')
        
        final_count = len(df)
        removed_count = initial_count - final_count
        
        logger.info(f"  🧹 Removed {removed_count} duplicates")
        logger.info(f"  📊 Final count: {final_count} records")
        
        return df

def main():
    """Main execution function."""
    logger.info("🎯 CORRECTED ANNUAL LFS DATA ENGINEERING SOLUTION")
    logger.info("=" * 80)
    
    # Create parser instance
    parser = CorrectedAnnualLFSParser()
    
    # Parse all annual LFS files
    df = parser.parse_all_annual_lfs_files_corrected()
    
    if not df.empty:
        # Remove duplicates
        df = parser.remove_duplicates_smartly_corrected(df)
        
        # Save to file
        output_file = "assets/prepared/LFS_annual_CORRECTED_FINAL.xlsx"
        df.to_excel(output_file, index=False)
        
        logger.info(f"💾 CORRECTED dataset saved to: {output_file}")
        logger.info(f"📊 Final dataset statistics:")
        logger.info(f"  Total records: {len(df):,}")
        logger.info(f"  Unique time periods: {df['time_period'].nunique()}")
        logger.info(f"  Unique regions: {df['region'].nunique()}")
        logger.info(f"  Unique economic sectors: {df['economic_sector'].nunique()}")
        logger.info(f"  Unique occupations: {df['occupation'].nunique()}")
        logger.info(f"  Unique age groups: {df['age_group'].nunique()}")
        logger.info(f"  Unique genders: {df['gender'].nunique()}")
        logger.info(f"  Unique education levels: {df['education'].nunique()}")
        logger.info(f"  Unique employment statuses: {df['employment_status'].nunique()}")
        
        logger.info("🎉 CORRECTED ANNUAL LFS DATA ENGINEERING COMPLETE!")
    else:
        logger.error("❌ FAILED to extract any data!")

if __name__ == "__main__":
    main()
