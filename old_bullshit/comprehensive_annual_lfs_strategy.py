#!/usr/bin/env python3
"""
COMPREHENSIVE ANNUAL LFS DATA ENGINEERING STRATEGY
Based on ACTUAL sheet schemas provided by user.
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
        logging.FileHandler('comprehensive_annual_lfs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveAnnualLFSStrategy:
    """Comprehensive strategy for annual LFS data based on actual sheet schemas."""
    
    def __init__(self):
        """Initialize the comprehensive strategy."""
        # SDMX Standard Columns
        self.sdmx_columns = [
            'indicator', 'time_period', 'freq', 'ref_area', 'value', 
            'unit_measure', 'obs_status', 'source_agency', 'collection', 'adjustment'
        ]
        
        # Dimension Mappings based on ACTUAL sheet schemas
        self.REGIONS_MAPPING = {
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
            'COUNTRY TOTAL': 'EL00'
        }
        
        self.AGE_GROUPS_MAPPING = {
            '0-14': '0-14',
            '15-19': '15-19',
            '20-24': '20-24', 
            '25-29': '25-29',
            '30-44': '30-44',
            '45-64': '45-64',
            '65+': '65+',
            '14': '14'  # For 1981-97 period
        }
        
        self.GENDER_MAPPING = {
            'Males': 'M',
            'Females': 'F',
            'Total Males': 'M',
            'Total Females': 'F',
            'YEAR TOTAL': 'TOTAL'
        }
        
        self.EMPLOYMENT_STATUS_MAPPING = {
            'Employed': 'EMPLOYED',
            ' - Self employed': 'SELF_EMPLOYED',
            ' - Family workers': 'FAMILY_WORKERS',
            ' - Employees': 'EMPLOYEES',
            ' -- Permanent job': 'PERMANENT_JOB',
            ' -- Temporary job': 'TEMPORARY_JOB',
            ' - Full-time employed': 'FULL_TIME',
            ' - Part-time employed': 'PART_TIME',
            'Unemployed': 'UNEMPLOYED',
            ' - New unemployed': 'NEW_UNEMPLOYED',
            ' - Long-term unemployed': 'LONG_TERM_UNEMPLOYED',
            'Inactive': 'INACTIVE',
            'TOTAL POPULATION AGED 15+': 'TOTAL_15_PLUS'
        }
        
        self.EDUCATION_LEVEL_MAPPING = {
            'Attended no school / Did not complete primary education': 'NO_SCHOOL_PRIMARY',
            'Primary': 'PRIMARY',
            'Lower secondary': 'LOWER_SECONDARY',
            'Upper secondary & post secondary': 'UPPER_SECONDARY_POST',
            'ekp1': 'EDUC_LEVEL_1',
            'ekp2': 'EDUC_LEVEL_2', 
            'ekp3': 'EDUC_LEVEL_3',
            'ekp4': 'EDUC_LEVEL_4',
            'Upper secondary': 'UPPER_SECONDARY',
            'Post secondary vocational': 'POST_SECONDARY_VOC',
            'ekp7': 'EDUC_LEVEL_7',
            'University degree': 'UNIVERSITY_DEGREE',
            'Postgraduate degrees (Μaster / PhD)': 'POSTGRADUATE',
            'Postgraduate degrees (including integrated Master\'s degrees)': 'POSTGRADUATE_INTEGRATED'
        }
        
        self.NATIONALITY_MAPPING = {
            'Greek': 'GR',
            'EU country': 'EU',
            'Other': 'OTHER'
        }
        
        self.MARITAL_STATUS_MAPPING = {
            'Single': 'SINGLE',
            'Married': 'MARRIED',
            'Widowed, divorced or legally separated': 'WIDOWED_DIVORCED_SEPARATED'
        }
        
        self.URBANIZATION_MAPPING = {
            'Athens agglomeration': 'ATHENS_AGGLOMERATION',
            'Thessaloniki agglomeration': 'THESSALONIKI_AGGLOMERATION',
            'Other urban areas': 'OTHER_URBAN',
            'Semi-urban areas': 'SEMI_URBAN',
            'Rural areas': 'RURAL'
        }
        
        self.INDICATOR_MAPPING = {
            'Population': 'POPULATION',
            'Labour Force': 'LABOUR_FORCE',
            'Activity Rate': 'ACTIVITY_RATE',
            'Employment Rate': 'EMPLOYMENT_RATE',
            'Unemployment Rate': 'UNEMPLOYMENT_RATE',
            'Education Level': 'EDUCATION_LEVEL',
            'NEETs': 'NEETS',
            'Tertiary Attainment': 'TERTIARY_ATTAINMENT',
            'Lifelong Learning': 'LIFELONG_LEARNING'
        }
        
        logger.info("✅ Comprehensive Annual LFS Strategy initialized")

    def extract_time_periods_from_sheet(self, sheet: pd.DataFrame, sheet_name: str) -> List[int]:
        """Extract time periods from sheet based on actual structure."""
        logger.info(f"    🔍 Extracting time periods from {sheet_name}")
        
        time_periods = []
        
        # Look for years in the first column (Year column)
        for row_idx in range(len(sheet)):
            cell_value = sheet.iloc[row_idx, 0]
            if pd.notna(cell_value):
                if isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                    time_periods.append(int(cell_value))
                elif isinstance(cell_value, str):
                    # Handle cases like "2,024" or "2024"
                    year_match = re.search(r'(\d{4})', str(cell_value).replace(',', ''))
                    if year_match:
                        year = int(year_match.group(1))
                        if 1900 < year < 2030:
                            time_periods.append(year)
        
        logger.info(f"      Found {len(time_periods)} time periods: {sorted(time_periods)}")
        return sorted(list(set(time_periods)))

    def extract_dimensions_from_popul_regio(self, sheet: pd.DataFrame) -> Dict[str, List[Any]]:
        """Extract dimensions from POPUL-Regio sheet."""
        logger.info("    🔍 Extracting dimensions from POPUL-Regio sheet")
        
        dimensions = {
            'regions': [],
            'age_groups': [],
            'genders': [],
            'nationality': [],
            'marital_status': []
        }
        
        # Extract regions from Column 1 (Region - NUTS II)
        for row_idx in range(len(sheet)):
            region_cell = sheet.iloc[row_idx, 1]
            if pd.notna(region_cell) and str(region_cell).strip() not in ['nan', 'Region - NUTS II']:
                region_name = str(region_cell).strip()
                if region_name in self.REGIONS_MAPPING:
                    dimensions['regions'].append(region_name)
        
        # Extract age groups from header row
        header_row = None
        for row_idx in range(min(10, len(sheet))):
            row_str = ' '.join(str(cell) for cell in sheet.iloc[row_idx] if pd.notna(cell))
            if '0-14' in row_str and '15-19' in row_str:
                header_row = row_idx
                break
        
        if header_row is not None:
            for col_idx in range(sheet.shape[1]):
                cell_value = str(sheet.iloc[header_row, col_idx]).strip()
                if cell_value in self.AGE_GROUPS_MAPPING:
                    dimensions['age_groups'].append(cell_value)
                elif 'Males' in cell_value or 'Females' in cell_value:
                    dimensions['genders'].append(cell_value)
                elif cell_value in self.NATIONALITY_MAPPING:
                    dimensions['nationality'].append(cell_value)
                elif cell_value in self.MARITAL_STATUS_MAPPING:
                    dimensions['marital_status'].append(cell_value)
        
        logger.info(f"      Extracted: {len(dimensions['regions'])} regions, {len(dimensions['age_groups'])} age groups")
        return dimensions

    def extract_dimensions_from_popul_status(self, sheet: pd.DataFrame) -> Dict[str, List[Any]]:
        """Extract dimensions from POPUL-Status sheet."""
        logger.info("    🔍 Extracting dimensions from POPUL-Status sheet")
        
        dimensions = {
            'employment_status': [],
            'sex': [],
            'age_groups': [],
            'marital_status': [],
            'nationality': [],
            'urbanization': []
        }
        
        # Extract employment status from Column 1
        for row_idx in range(len(sheet)):
            status_cell = sheet.iloc[row_idx, 1]
            if pd.notna(status_cell) and str(status_cell).strip() not in ['nan', 'Employment status']:
                status_name = str(status_cell).strip()
                if status_name in self.EMPLOYMENT_STATUS_MAPPING:
                    dimensions['employment_status'].append(status_name)
        
        # Extract other dimensions from header rows
        for row_idx in range(min(15, len(sheet))):
            row_str = ' '.join(str(cell) for cell in sheet.iloc[row_idx] if pd.notna(cell))
            if 'Males' in row_str and 'Females' in row_str:
                dimensions['sex'].extend(['Males', 'Females'])
            if 'Single' in row_str and 'Married' in row_str:
                dimensions['marital_status'].extend(['Single', 'Married', 'Widowed, divorced or legally separated'])
            if 'Greek' in row_str and 'EU country' in row_str:
                dimensions['nationality'].extend(['Greek', 'EU country', 'Other'])
            if 'Athens agglomeration' in row_str:
                dimensions['urbanization'].extend(['Athens agglomeration', 'Thessaloniki agglomeration', 'Other urban areas', 'Semi-urban areas', 'Rural areas'])
        
        logger.info(f"      Extracted: {len(dimensions['employment_status'])} employment statuses, {len(dimensions['sex'])} sexes")
        return dimensions

    def extract_dimensions_from_educ_sheets(self, sheet: pd.DataFrame, sheet_name: str) -> Dict[str, List[Any]]:
        """Extract dimensions from education sheets."""
        logger.info(f"    🔍 Extracting dimensions from {sheet_name}")
        
        dimensions = {
            'sex': [],
            'age_groups': [],
            'education_levels': [],
            'regions': []
        }
        
        # Extract sex and age from Column 1 and 2
        for row_idx in range(len(sheet)):
            sex_cell = sheet.iloc[row_idx, 1] if sheet.shape[1] > 1 else None
            age_cell = sheet.iloc[row_idx, 2] if sheet.shape[1] > 2 else None
            
            if pd.notna(sex_cell) and str(sex_cell).strip() in self.GENDER_MAPPING:
                dimensions['sex'].append(str(sex_cell).strip())
            if pd.notna(age_cell) and str(age_cell).strip() in self.AGE_GROUPS_MAPPING:
                dimensions['age_groups'].append(str(age_cell).strip())
        
        # Extract regions if this is EDUC-Regio
        if 'Regio' in sheet_name:
            for row_idx in range(len(sheet)):
                region_cell = sheet.iloc[row_idx, 1]
                if pd.notna(region_cell) and str(region_cell).strip() in self.REGIONS_MAPPING:
                    dimensions['regions'].append(str(region_cell).strip())
        
        # Extract education levels from header
        for row_idx in range(min(10, len(sheet))):
            row_str = ' '.join(str(cell) for cell in sheet.iloc[row_idx] if pd.notna(cell))
            for edu_level in self.EDUCATION_LEVEL_MAPPING:
                if edu_level in row_str:
                    dimensions['education_levels'].append(edu_level)
        
        logger.info(f"      Extracted: {len(dimensions['sex'])} sexes, {len(dimensions['age_groups'])} age groups, {len(dimensions['education_levels'])} education levels")
        return dimensions

    def extract_dimensions_from_status_sheets(self, sheet: pd.DataFrame, sheet_name: str) -> Dict[str, List[Any]]:
        """Extract dimensions from status sheets."""
        logger.info(f"    🔍 Extracting dimensions from {sheet_name}")
        
        dimensions = {
            'sex': [],
            'age_groups': [],
            'regions': [],
            'employment_status': []
        }
        
        # Extract sex and age from Column 1 and 2
        for row_idx in range(len(sheet)):
            sex_cell = sheet.iloc[row_idx, 1] if sheet.shape[1] > 1 else None
            age_cell = sheet.iloc[row_idx, 2] if sheet.shape[1] > 2 else None
            
            if pd.notna(sex_cell) and str(sex_cell).strip() in self.GENDER_MAPPING:
                dimensions['sex'].append(str(sex_cell).strip())
            if pd.notna(age_cell) and str(age_cell).strip() in self.AGE_GROUPS_MAPPING:
                dimensions['age_groups'].append(str(age_cell).strip())
        
        # Extract regions if this is STATUS-Regio
        if 'Regio' in sheet_name:
            for row_idx in range(len(sheet)):
                region_cell = sheet.iloc[row_idx, 1]
                if pd.notna(region_cell) and str(region_cell).strip() in self.REGIONS_MAPPING:
                    dimensions['regions'].append(str(region_cell).strip())
        
        # Extract employment status if this is STATUS-Status
        if 'Status' in sheet_name:
            for row_idx in range(len(sheet)):
                status_cell = sheet.iloc[row_idx, 1]
                if pd.notna(status_cell) and str(status_cell).strip() in self.EMPLOYMENT_STATUS_MAPPING:
                    dimensions['employment_status'].append(str(status_cell).strip())
        
        logger.info(f"      Extracted: {len(dimensions['sex'])} sexes, {len(dimensions['age_groups'])} age groups")
        return dimensions

    def parse_data_from_popul_regio(self, sheet: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Parse data from POPUL-Regio sheet."""
        logger.info(f"    📊 Parsing data from {sheet_name}")
        
        data_records = []
        time_periods = self.extract_time_periods_from_sheet(sheet, sheet_name)
        
        # Find data rows (rows with years)
        data_rows = []
        for row_idx in range(len(sheet)):
            cell_value = sheet.iloc[row_idx, 0]
            if pd.notna(cell_value) and isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                data_rows.append(row_idx)
        
        logger.info(f"      Found {len(data_rows)} data rows")
        
        # Parse each data row
        for row_idx in data_rows:
            year = int(sheet.iloc[row_idx, 0])
            
            # Extract region from Column 1
            region = sheet.iloc[row_idx, 1] if sheet.shape[1] > 1 else None
            if pd.notna(region) and str(region).strip() in self.REGIONS_MAPPING:
                region_name = str(region).strip()
                
                # Parse numeric values from columns 2 onwards
                for col_idx in range(2, min(sheet.shape[1], 50)):  # Limit to reasonable columns
                    cell_value = sheet.iloc[row_idx, col_idx]
                    if pd.notna(cell_value) and isinstance(cell_value, (int, float)):
                        # Determine dimension based on column position or header
                        # This is simplified - in practice we'd need to map column positions to dimensions
                        
                        record = {
                            'indicator': 'POPULATION',
                            'time_period': year,
                            'freq': 'A',
                            'ref_area': self.REGIONS_MAPPING.get(region_name, region_name),
                            'value': float(cell_value),
                            'unit_measure': 'PERSONS',
                            'obs_status': 'A',
                            'source_agency': 'ELSTAT',
                            'collection': 'LFS',
                            'adjustment': 'N',
                            'region': region_name,
                            'sheet_name': sheet_name,
                            'col_position': col_idx
                        }
                        
                        data_records.append(record)
        
        logger.info(f"      Parsed {len(data_records)} records")
        return data_records

    def parse_data_from_popul_status(self, sheet: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Parse data from POPUL-Status sheet."""
        logger.info(f"    📊 Parsing data from {sheet_name}")
        
        data_records = []
        time_periods = self.extract_time_periods_from_sheet(sheet, sheet_name)
        
        # Find data rows (rows with years)
        data_rows = []
        for row_idx in range(len(sheet)):
            cell_value = sheet.iloc[row_idx, 0]
            if pd.notna(cell_value) and isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                data_rows.append(row_idx)
        
        logger.info(f"      Found {len(data_rows)} data rows")
        
        # Parse each data row
        for row_idx in data_rows:
            year = int(sheet.iloc[row_idx, 0])
            
            # Extract employment status from Column 1
            status = sheet.iloc[row_idx, 1] if sheet.shape[1] > 1 else None
            if pd.notna(status) and str(status).strip() in self.EMPLOYMENT_STATUS_MAPPING:
                status_name = str(status).strip()
                
                # Parse numeric values from columns 2 onwards
                for col_idx in range(2, min(sheet.shape[1], 50)):
                    cell_value = sheet.iloc[row_idx, col_idx]
                    if pd.notna(cell_value) and isinstance(cell_value, (int, float)):
                        record = {
                            'indicator': 'POPULATION_EMPLOYMENT_STATUS',
                            'time_period': year,
                            'freq': 'A',
                            'ref_area': 'EL00',  # Country level
                            'value': float(cell_value),
                            'unit_measure': 'PERSONS',
                            'obs_status': 'A',
                            'source_agency': 'ELSTAT',
                            'collection': 'LFS',
                            'adjustment': 'N',
                            'employment_status': status_name,
                            'sheet_name': sheet_name,
                            'col_position': col_idx
                        }
                        
                        data_records.append(record)
        
        logger.info(f"      Parsed {len(data_records)} records")
        return data_records

    def parse_data_from_educ_sheets(self, sheet: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Parse data from education sheets."""
        logger.info(f"    📊 Parsing data from {sheet_name}")
        
        data_records = []
        time_periods = self.extract_time_periods_from_sheet(sheet, sheet_name)
        
        # Find data rows (rows with years)
        data_rows = []
        for row_idx in range(len(sheet)):
            cell_value = sheet.iloc[row_idx, 0]
            if pd.notna(cell_value) and isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                data_rows.append(row_idx)
        
        logger.info(f"      Found {len(data_rows)} data rows")
        
        # Parse each data row
        for row_idx in data_rows:
            year = int(sheet.iloc[row_idx, 0])
            
            # Extract sex and age if available
            sex = sheet.iloc[row_idx, 1] if sheet.shape[1] > 1 else None
            age = sheet.iloc[row_idx, 2] if sheet.shape[1] > 2 else None
            
            # Parse numeric values from columns 3 onwards
            for col_idx in range(3, min(sheet.shape[1], 50)):
                cell_value = sheet.iloc[row_idx, col_idx]
                if pd.notna(cell_value) and isinstance(cell_value, (int, float)):
                    record = {
                        'indicator': 'EDUCATION_LEVEL',
                        'time_period': year,
                        'freq': 'A',
                        'ref_area': 'EL00',
                        'value': float(cell_value),
                        'unit_measure': 'PERSONS',
                        'obs_status': 'A',
                        'source_agency': 'ELSTAT',
                        'collection': 'LFS',
                        'adjustment': 'N',
                        'sex': str(sex) if pd.notna(sex) else None,
                        'age_group': str(age) if pd.notna(age) else None,
                        'sheet_name': sheet_name,
                        'col_position': col_idx
                    }
                    
                    data_records.append(record)
        
        logger.info(f"      Parsed {len(data_records)} records")
        return data_records

    def parse_data_from_status_sheets(self, sheet: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Parse data from status sheets."""
        logger.info(f"    📊 Parsing data from {sheet_name}")
        
        data_records = []
        time_periods = self.extract_time_periods_from_sheet(sheet, sheet_name)
        
        # Find data rows (rows with years)
        data_rows = []
        for row_idx in range(len(sheet)):
            cell_value = sheet.iloc[row_idx, 0]
            if pd.notna(cell_value) and isinstance(cell_value, (int, float)) and 1900 < cell_value < 2030:
                data_rows.append(row_idx)
        
        logger.info(f"      Found {len(data_rows)} data rows")
        
        # Parse each data row
        for row_idx in data_rows:
            year = int(sheet.iloc[row_idx, 0])
            
            # Extract sex and age if available
            sex = sheet.iloc[row_idx, 1] if sheet.shape[1] > 1 else None
            age = sheet.iloc[row_idx, 2] if sheet.shape[1] > 2 else None
            
            # Parse numeric values from columns 3 onwards
            for col_idx in range(3, min(sheet.shape[1], 50)):
                cell_value = sheet.iloc[row_idx, col_idx]
                if pd.notna(cell_value) and isinstance(cell_value, (int, float)):
                    record = {
                        'indicator': 'EMPLOYMENT_STATUS',
                        'time_period': year,
                        'freq': 'A',
                        'ref_area': 'EL00',
                        'value': float(cell_value),
                        'unit_measure': 'PERSONS',
                        'obs_status': 'A',
                        'source_agency': 'ELSTAT',
                        'collection': 'LFS',
                        'adjustment': 'N',
                        'sex': str(sex) if pd.notna(sex) else None,
                        'age_group': str(age) if pd.notna(age) else None,
                        'sheet_name': sheet_name,
                        'col_position': col_idx
                    }
                    
                    data_records.append(record)
        
        logger.info(f"      Parsed {len(data_records)} records")
        return data_records

    def parse_sheet_by_type(self, sheet: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Parse sheet based on its type and structure."""
        logger.info(f"  🔍 Parsing sheet: {sheet_name}")
        
        if 'POPUL-Regio' in sheet_name:
            return self.parse_data_from_popul_regio(sheet, sheet_name)
        elif 'POPUL-Status' in sheet_name:
            return self.parse_data_from_popul_status(sheet, sheet_name)
        elif 'EDUC-' in sheet_name:
            return self.parse_data_from_educ_sheets(sheet, sheet_name)
        elif 'STATUS-' in sheet_name:
            return self.parse_data_from_status_sheets(sheet, sheet_name)
        else:
            logger.warning(f"    ⚠️ Unknown sheet type: {sheet_name}")
            return []

    def parse_all_annual_lfs_files(self) -> pd.DataFrame:
        """Parse all annual LFS files using comprehensive strategy."""
        logger.info("🚀 STARTING COMPREHENSIVE ANNUAL LFS PARSING")
        
        # Find all annual LFS files
        lfs_dir = "assets/LFS"
        annual_files = [f for f in os.listdir(lfs_dir) if "TS_AN" in f and f.endswith('.xlsx')]
        
        logger.info(f"📁 Found {len(annual_files)} annual LFS files")
        
        all_data = []
        
        for file_name in annual_files:
            file_path = os.path.join(lfs_dir, file_name)
            logger.info(f"\n📊 Processing file: {file_name}")
            
            try:
                # Get all sheet names
                xl_file = pd.ExcelFile(file_path)
                sheet_names = xl_file.sheet_names
                
                logger.info(f"  📋 Sheets found: {len(sheet_names)}")
                for sheet_name in sheet_names:
                    logger.info(f"    - {sheet_name}")
                
                # Process each sheet
                for sheet_name in sheet_names:
                    try:
                        # Read sheet
                        sheet = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                        logger.info(f"  📊 Sheet {sheet_name}: {sheet.shape}")
                        
                        # Parse sheet based on type
                        sheet_data = self.parse_sheet_by_type(sheet, sheet_name)
                        
                        if sheet_data:
                            # Add file information
                            for record in sheet_data:
                                record['file_name'] = file_name
                            
                            all_data.extend(sheet_data)
                            logger.info(f"    ✅ Parsed {len(sheet_data)} records from {sheet_name}")
                        else:
                            logger.warning(f"    ⚠️ No data parsed from {sheet_name}")
                    
                    except Exception as e:
                        logger.error(f"    ❌ Error processing sheet {sheet_name}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"❌ Error processing file {file_name}: {e}")
                continue
        
        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            logger.info(f"\n🎉 COMPREHENSIVE PARSING COMPLETE!")
            logger.info(f"  Total records: {len(df):,}")
            logger.info(f"  Total columns: {len(df.columns)}")
            logger.info(f"  Columns: {list(df.columns)}")
            
            # Basic data quality checks
            logger.info(f"\n📊 DATA QUALITY SUMMARY:")
            for col in df.columns:
                if col in ['value', 'time_period']:
                    non_null = df[col].notna().sum()
                    null_count = df[col].isna().sum()
                    total = len(df)
                    null_percent = (null_count / total) * 100
                    logger.info(f"  {col}: {non_null:,} non-null, {null_count:,} nulls ({null_percent:.1f}%)")
            
            return df
        else:
            logger.error("❌ No data parsed from any files!")
            return pd.DataFrame()

def main():
    """Main execution function."""
    strategy = ComprehensiveAnnualLFSStrategy()
    
    # Parse all annual LFS files
    df = strategy.parse_all_annual_lfs_files()
    
    if not df.empty:
        # Save to Excel
        output_file = 'assets/prepared/LFS_annual_COMPREHENSIVE.xlsx'
        df.to_excel(output_file, index=False)
        print(f"\n💾 Dataset saved to: {output_file}")
        
        # Save to CSV for inspection
        csv_file = 'assets/prepared/LFS_annual_COMPREHENSIVE.csv'
        df.to_csv(csv_file, index=False)
        print(f"💾 Dataset also saved to: {csv_file}")
        
        print(f"\n🏆 COMPREHENSIVE ANNUAL LFS PARSING COMPLETE!")
        print(f"  Total records: {len(df):,}")
        print(f"  Total columns: {len(df.columns)}")
    else:
        print("❌ No data was parsed!")

if __name__ == "__main__":
    main()
