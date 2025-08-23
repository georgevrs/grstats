from loguru import logger
import pandas as pd
import os
import re

def parse_mci_sheet(sheet):
    """
    Parse the MCI sheet to extract Harmonized Index of Consumer Prices data.
    Expected structure: Year and month data with HICP values and rates of change.
    """
    logger.info("Parsing MCI sheet for Harmonized Index of Consumer Prices data...")
    data = []
    
    # Find the data table - look for the first data row (1996 : 1)
    start_row = None
    for i, row in sheet.iterrows():
        if isinstance(row.iloc[1], str) and "1996 :  1" in str(row.iloc[1]):
            start_row = i
            break
    
    if start_row is None:
        logger.error("Could not find data table start")
        return pd.DataFrame()
    
    logger.debug(f"Processing data starting from row {start_row}")
    
    # Process each row starting from the data
    current_year = None
    
    for i in range(start_row, len(sheet)):
        row = sheet.iloc[i]
        
        # Skip empty rows
        if pd.isna(row.iloc[1]) or str(row.iloc[1]).strip() == '':
            continue
            
        # Check if this is a year header row (contains year and month)
        year_month_cell = str(row.iloc[1]).strip()
        
        # Skip if it's empty
        if year_month_cell == '':
            continue
            
        # Extract year and month from the cell
        # Format: "  1996 :  1" or "             2 " or "Annual average"
        year_match = re.search(r'(\d{4})\s*:\s*(\d+)', year_month_cell)
        if year_match:
            # This is a year header row
            current_year = int(year_match.group(1))
            month = int(year_match.group(2))
        elif year_month_cell == 'Annual average':
            # This is an annual average row
            month = 13  # Use 13 to represent annual average
        else:
            # Try to extract just the month number (for subsequent months)
            month_match = re.search(r'(\d+)', year_month_cell.strip())
            if month_match and len(month_match.group(1)) <= 2 and current_year is not None:
                month = int(month_match.group(1))
            else:
                continue
        
        # Extract numeric data from columns
        try:
            # Column structure based on the data:
            # Year/Month | Overall HICP | Rate of change (%) from month to month | Annual rate of change (%) | Annual average index | Annual average rate of change (%)
            overall_hicp = float(row.iloc[2]) if pd.notna(row.iloc[2]) else None
            monthly_rate = float(row.iloc[3]) if pd.notna(row.iloc[3]) else None
            annual_rate = float(row.iloc[4]) if pd.notna(row.iloc[4]) else None
            annual_avg_index = float(row.iloc[5]) if pd.notna(row.iloc[5]) else None
            annual_avg_rate = float(row.iloc[6]) if pd.notna(row.iloc[6]) else None
            
            data.append({
                'YEAR': current_year,
                'MONTH': month,
                'FREQ': 'A' if month == 13 else 'M',  # Annual frequency for annual averages, Monthly for others
                'OVERALL_HICP': overall_hicp,
                'MONTHLY_RATE_CHANGE': monthly_rate,
                'ANNUAL_RATE_CHANGE': annual_rate,
                'ANNUAL_AVERAGE_INDEX': annual_avg_index,
                'ANNUAL_AVERAGE_RATE_CHANGE': annual_avg_rate
            })
            
            month_display = "Annual" if month == 13 else f"{month:02d}"
            logger.debug(f"Added data for {current_year}-{month_display}: HICP={overall_hicp}, Monthly rate={monthly_rate}, Annual rate={annual_rate}")
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse row {i} for year/month '{year_month_cell}': {e}")
            continue
    
    df = pd.DataFrame(data)
    if not df.empty:
        df = df[['YEAR', 'MONTH', 'FREQ', 'OVERALL_HICP', 'MONTHLY_RATE_CHANGE', 'ANNUAL_RATE_CHANGE', 'ANNUAL_AVERAGE_INDEX', 'ANNUAL_AVERAGE_RATE_CHANGE']]
        logger.success(f"Parsed {len(df)} rows of MCI data")
    else:
        logger.warning("No data was parsed from the sheet")
    return df

def parse_hicp_sheet(sheet):
    """
    Parse the HICP sheet to extract Harmonized Index of Consumer Prices data.
    Expected structure: Months as rows, years as columns with HICP values.
    """
    logger.info("Parsing HICP sheet for Harmonized Index of Consumer Prices data...")
    data = []
    
    # Find the data table - look for the header row with years
    start_row = None
    for i, row in sheet.iterrows():
        if isinstance(row.iloc[1], str) and "Month" in str(row.iloc[1]):
            start_row = i
            break
    
    if start_row is None:
        logger.error("Could not find data table start")
        return pd.DataFrame()
    
    logger.debug(f"Processing data starting from row {start_row}")
    
    # Extract years from the header row
    header_row = sheet.iloc[start_row]
    years = []
    for col_idx in range(2, len(header_row)):  # Skip the "Month" column and start from column 2
        cell_value = str(header_row.iloc[col_idx]).strip()
        if cell_value and cell_value.replace('.0', '').isdigit():
            years.append(int(float(cell_value)))
    
    logger.debug(f"Found years: {years}")
    
    # Process each data row (months)
    for i in range(start_row + 1, len(sheet)):
        row = sheet.iloc[i]
        
        # Skip empty rows
        if pd.isna(row.iloc[1]) or str(row.iloc[1]).strip() == '':
            continue
            
        # Extract month name
        month_cell = str(row.iloc[1]).strip()
        logger.debug(f"Processing row {i}, month cell: '{month_cell}'")
        
        # Skip if it's empty or doesn't contain month data
        if month_cell == '':
            logger.debug(f"Skipping empty row {i}")
            continue
            
        # Map month names to numbers
        month_mapping = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        if month_cell not in month_mapping:
            logger.debug(f"Skipping row with month: '{month_cell}'")
            continue
            
        month = month_mapping[month_cell]
        logger.debug(f"Processing month: {month_cell} -> {month}")
        
        # Extract HICP values for each year
        for col_idx, year in enumerate(years, start=2):
            try:
                hicp_value = row.iloc[col_idx]
                logger.debug(f"Raw HICP value for {year}-{month:02d}: {hicp_value} (type: {type(hicp_value)})")
                if pd.notna(hicp_value):
                    hicp_value = float(hicp_value)
                    
                    data.append({
                        'YEAR': year,
                        'MONTH': month,
                        'FREQ': 'M',  # Monthly frequency
                        'HICP': hicp_value
                    })
                    
                    logger.debug(f"Added data for {year}-{month:02d}: HICP={hicp_value}")
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse HICP value for {year}-{month:02d}: {e}")
                continue
    
    df = pd.DataFrame(data)
    if not df.empty:
        df = df[['YEAR', 'MONTH', 'FREQ', 'HICP']]
        logger.success(f"Parsed {len(df)} rows of HICP data")
    else:
        logger.warning("No data was parsed from the sheet")
    return df

def merge_mci_hicp_data(mci_df, hicp_df):
    """
    Merge MCI and HICP data by YEAR and MONTH.
    Creates a comprehensive dataset with all available metrics.
    """
    logger.info("Merging MCI and HICP data...")
    
    if mci_df.empty and hicp_df.empty:
        logger.error("Both MCI and HICP dataframes are empty")
        return pd.DataFrame()
    
    if mci_df.empty:
        logger.warning("MCI dataframe is empty, returning HICP data only")
        return hicp_df
    
    if hicp_df.empty:
        logger.warning("HICP dataframe is empty, returning MCI data only")
        return mci_df
    
    # Merge on YEAR and MONTH, keeping all data
    merged_df = pd.merge(mci_df, hicp_df, on=['YEAR', 'MONTH', 'FREQ'], how='outer')
    
    # Handle frequency column - ensure consistency
    merged_df['FREQ'] = merged_df['FREQ'].fillna('M')
    
    # Create TIME_PERIOD column at index position 3
    # Format: YYYY-MM for months 1-12, YYYY for month 13 (annual)
    merged_df['TIME_PERIOD'] = merged_df.apply(
        lambda row: f"{row['YEAR']}-M{row['MONTH']:02d}" if row['MONTH'] != 13 else str(row['YEAR']), 
        axis=1
    )
    
    # Reorder columns to put TIME_PERIOD at index position 3 (after YEAR, MONTH, FREQ)
    column_order = ['YEAR', 'MONTH', 'FREQ', 'TIME_PERIOD']
    # Add remaining columns after TIME_PERIOD
    for col in merged_df.columns:
        if col not in column_order:
            column_order.append(col)
    
    merged_df = merged_df[column_order]
    
    # Sort by year and month for better readability
    merged_df = merged_df.sort_values(['YEAR', 'MONTH']).reset_index(drop=True)
    
    logger.success(f"Merged dataset created with {len(merged_df)} rows")
    logger.info(f"Columns in merged dataset: {list(merged_df.columns)}")
    logger.info(f"TIME_PERIOD format examples: {merged_df['TIME_PERIOD'].head().tolist()}")
    
    return merged_df

def main():
    # Input files
    import glob
    import os

    hicp_files = glob.glob("assets/HICP/*03_F_EN.xlsx")
    if not hicp_files:
        logger.error("No HICP file matching '*03_F_EN.xlsx' found in assets/HICP")
        return
    # Pick the most recent file by modification time
    hicp_input_file = max(hicp_files, key=os.path.getmtime)

    # do the same for mci
    mci_files = glob.glob("assets/HICP/*02_F_EN.xlsx")
    if not mci_files:
        logger.error("No MCI file matching '*02_F_EN.xlsx' found in assets/HICP")
        return
    mci_input_file = max(mci_files, key=os.path.getmtime)
    
    # Output configuration
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "HICP.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Parse MCI data
        logger.info(f"Loading MCI Excel file: {mci_input_file}")
        mci_xl = pd.ExcelFile(mci_input_file)
        mci_sheet = mci_xl.parse(mci_xl.sheet_names[0], header=None)
        mci_df = parse_mci_sheet(mci_sheet)
        
        # Parse HICP data
        logger.info(f"Loading HICP Excel file: {hicp_input_file}")
        hicp_xl = pd.ExcelFile(hicp_input_file)
        hicp_sheet = hicp_xl.parse(hicp_xl.sheet_names[0], header=None)
        hicp_df = parse_hicp_sheet(hicp_sheet)
        
        # Merge the datasets
        final_df = merge_mci_hicp_data(mci_df, hicp_df)
        
        if not final_df.empty:
            # Clean up - remove any rows with missing essential data
            # Keep rows that have at least YEAR, MONTH, and one of the HICP values
            essential_columns = ['YEAR', 'MONTH', 'FREQ']
            hicp_columns = ['OVERALL_HICP', 'HICP']
            
            # Check if at least one HICP column has data
            final_df = final_df.dropna(subset=essential_columns).reset_index(drop=True)
            
            # Save to Excel
            final_df.to_excel(output_file, index=False)
            logger.success(f"Saved merged MCI and HICP data to {output_file}")
            
            # Log comprehensive statistics
            logger.info(f"Final merged dataset shape: {final_df.shape}")
            logger.info(f"Year range: {final_df['YEAR'].min()}-{final_df['YEAR'].max()}")
            logger.info(f"Number of data points: {len(final_df)}")
            
            # MCI statistics
            if 'OVERALL_HICP' in final_df.columns:
                mci_data = final_df.dropna(subset=['OVERALL_HICP'])
                if not mci_data.empty:
                    logger.info(f"MCI data points: {len(mci_data)}")
                    logger.info(f"Average MCI HICP: {mci_data['OVERALL_HICP'].mean():.2f}")
                    logger.info(f"MCI HICP range: {mci_data['OVERALL_HICP'].min():.2f} - {mci_data['OVERALL_HICP'].max():.2f}")
            
            # HICP statistics
            if 'HICP' in final_df.columns:
                hicp_data = final_df.dropna(subset=['HICP'])
                if not hicp_data.empty:
                    logger.info(f"HICP data points: {len(hicp_data)}")
                    logger.info(f"Average HICP: {hicp_data['HICP'].mean():.2f}")
                    logger.info(f"HICP range: {hicp_data['HICP'].min():.2f} - {hicp_data['HICP'].max():.2f}")
            
            # Data completeness analysis
            total_possible = len(final_df)
            mci_complete = len(final_df.dropna(subset=['OVERALL_HICP']))
            hicp_complete = len(final_df.dropna(subset=['HICP']))
            both_complete = len(final_df.dropna(subset=['OVERALL_HICP', 'HICP']))
            
            logger.info(f"Data completeness:")
            logger.info(f"  - Total rows: {total_possible}")
            logger.info(f"  - MCI data available: {mci_complete} ({mci_complete/total_possible*100:.1f}%)")
            logger.info(f"  - HICP data available: {hicp_complete} ({hicp_complete/total_possible*100:.1f}%)")
            logger.info(f"  - Both datasets available: {both_complete} ({both_complete/total_possible*100:.1f}%)")
            
        else:
            logger.error("No data to save")
            
    except Exception as e:
        logger.error(f"Failed to process MCI and HICP files: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
