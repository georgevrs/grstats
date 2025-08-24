#!/usr/bin/env python3
"""
SPECIALIZED MONTHLY DATA PARSER - FIXES THE BROKEN MONTHLY EXTRACTION
This parser correctly extracts monthly data from Table 1A by properly identifying month headers and data columns.
"""

import pandas as pd
import os
import logging
import re
from collections import defaultdict
from datetime import datetime
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_monthly_data_correctly(file_path):
    """Extract monthly data CORRECTLY from Table 1A."""
    logger.info(f"🔍 FIXING MONTHLY DATA EXTRACTION FROM: {os.path.basename(file_path)}")
    
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(file_path)
        sheet_name = 'TABLE 1Α'  # The specific sheet with monthly data
        
        # Read the sheet with NO header assumption
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        logger.info(f"Sheet dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # First, let's examine the structure to understand how months are organized
        logger.info("🔍 ANALYZING TABLE STRUCTURE FOR MONTHLY DATA")
        
        # Look for month names in the first column
        month_mapping = {
            'Ιανουάριος': 'January', 'Ιανουάριος': 'January', 'Ιανουάριος': 'January',
            'Φεβρουάριος': 'February', 'Φεβρουάριος': 'February', 'Φεβρουάριος': 'February',
            'Μάρτιος': 'March', 'Μάρτιος': 'March', 'Μάρτιος': 'March',
            'Απρίλιος': 'April', 'Απρίλιος': 'April', 'Απρίλιος': 'April',
            'Μάιος': 'May', 'Μάιος': 'May', 'Μάιος': 'May',
            'Ιούνιος': 'June', 'Ιούνιος': 'June', 'Ιούνιος': 'June',
            'Ιούλιος': 'July', 'Ιούλιος': 'July', 'Ιούλιος': 'July',
            'Αύγουστος': 'August', 'Αύγουστος': 'August', 'Αύγουστος': 'August',
            'Σεπτέμβριος': 'September', 'Σεπτέμβριος': 'September', 'Σεπτέμβριος': 'September',
            'Οκτώβριος': 'October', 'Οκτώβριος': 'October', 'Οκτώβριος': 'October',
            'Νοέμβριος': 'November', 'Νοέμβριος': 'November', 'Νοέμβριος': 'November',
            'Δεκέμβριος': 'December', 'Δεκέμβριος': 'December', 'Δεκέμβριος': 'December'
        }
        
        # Also check for English month names
        english_months = ['January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December']
        
        # Look for the year in the header rows
        year_found = None
        for row_idx in range(10):  # Check first 10 rows
            if row_idx < df.shape[0]:
                row = df.iloc[row_idx]
                for col_idx, cell in enumerate(row):
                    if pd.notna(cell) and isinstance(cell, str):
                        year_match = re.search(r'^(\d{4})$', str(cell).strip())
                        if year_match:
                            year_found = int(year_match.group(1))
                            logger.info(f"Found year {year_found} at row {row_idx}, col {col_idx}")
                            break
                if year_found:
                    break
        
        if not year_found:
            # Try to find year in the filename
            filename = os.path.basename(file_path)
            year_match = re.search(r'(\d{4})', filename)
            if year_match:
                year_found = int(year_match.group(1))
                logger.info(f"Using year from filename: {year_found}")
            else:
                year_found = 2004  # Default year for this dataset
                logger.info(f"Using default year: {year_found}")
        
        # Now look for month headers in the first column
        month_data = []
        
        for row_idx in range(df.shape[0]):
            if pd.notna(df.iloc[row_idx, 0]) and isinstance(df.iloc[row_idx, 0], str):
                cell_str = str(df.iloc[row_idx, 0]).strip()
                
                # Check if this is a month name (Greek or English)
                month_found = None
                month_num = None
                
                # Check Greek months
                for greek_month, english_month in month_mapping.items():
                    if greek_month in cell_str:
                        month_found = english_month
                        month_num = english_months.index(english_month) + 1
                        break
                
                # Check English months
                if not month_found:
                    for month in english_months:
                        if month in cell_str:
                            month_found = month
                            month_num = english_months.index(month) + 1
                            break
                
                if month_found:
                    logger.info(f"Found month: {month_found} (row {row_idx})")
                    
                    # Now find the data column for this month
                    # The data should be in the same row but in a different column
                    for col_idx in range(1, df.shape[1]):
                        if pd.notna(df.iloc[row_idx, col_idx]):
                            try:
                                value = float(df.iloc[row_idx, col_idx])
                                
                                # Create the proper time period
                                time_period = f"{year_found}-{month_num:02d}"
                                
                                month_data.append({
                                    'row_idx': row_idx,
                                    'col_idx': col_idx,
                                    'month': month_found,
                                    'month_num': month_num,
                                    'year': year_found,
                                    'time_period': time_period,
                                    'freq': 'M',
                                    'value': value
                                })
                                
                                logger.info(f"  Found data: {time_period} = {value} at col {col_idx}")
                                break
                                
                            except (ValueError, TypeError):
                                continue
        
        logger.info(f"Total monthly data points found: {len(month_data)}")
        
        # Create records with proper dimensional context
        records = []
        for month_info in month_data:
            record = {
                'time_period': month_info['time_period'],
                'freq': 'M',
                'value': month_info['value'],
                'ref_area': 'GR',
                'source_agency': 'EL.STAT',
                'unit_measure': 'THOUSANDS',
                'indicator': 'EMPLOYMENT',
                'file_source': os.path.basename(file_path),
                'sheet_name': sheet_name,
                'month': month_info['month'],
                'month_num': month_info['month_num'],
                'year': month_info['year']
            }
            records.append(record)
        
        logger.info(f"Created {len(records)} monthly records")
        return records
        
    except Exception as e:
        logger.error(f"Error extracting monthly data: {e}")
        return []

def main():
    """Main execution function."""
    logger.info("🔧 FIXING BROKEN MONTHLY DATA EXTRACTION")
    logger.info("This will correctly extract monthly data from Table 1A")
    
    # File path for Table 1A
    file_path = "assets/LFS/A0101_SJO02_TS_MM_01_2004_05_2025_01A_F_EN.xlsx"
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    # Extract monthly data correctly
    monthly_records = extract_monthly_data_correctly(file_path)
    
    if monthly_records:
        logger.info(f"✅ SUCCESS! Extracted {len(monthly_records)} monthly records")
        
        # Show sample records
        logger.info("Sample monthly records:")
        for i, record in enumerate(monthly_records[:5]):
            logger.info(f"  {i+1}. {record['time_period']}: {record['value']} ({record['month']} {record['year']})")
        
        # Create DataFrame and save
        df_monthly = pd.DataFrame(monthly_records)
        output_file = "assets/prepared/LFS_MONTHLY_DATA_FIXED.xlsx"
        df_monthly.to_excel(output_file, index=False)
        
        logger.info(f"💾 Monthly data saved to: {output_file}")
        logger.info(f"📊 Dataset contains {len(df_monthly)} monthly records")
        logger.info(f"⏰ Time range: {df_monthly['time_period'].min()} to {df_monthly['time_period'].max()}")
        
    else:
        logger.error("❌ FAILED to extract monthly data!")

if __name__ == "__main__":
    main()
