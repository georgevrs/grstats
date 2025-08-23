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

def main():
    input_file = "assets/MCI/A0515_DKT90_TS_MM_01_1996_06_2025_02_F_EN.xlsx"
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "MCI.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        
        # Parse the sheet
        final_df = parse_mci_sheet(sheet)
        
        if not final_df.empty:
            # Clean up - remove any rows with missing essential data
            final_df = final_df.dropna(subset=['YEAR', 'MONTH', 'FREQ', 'OVERALL_HICP']).reset_index(drop=True)
            
            # Save to Excel
            final_df.to_excel(output_file, index=False)
            logger.success(f"Saved normalized MCI data to {output_file}")
            logger.info(f"Final dataset shape: {final_df.shape}")
            logger.info(f"Year range: {final_df['YEAR'].min()}-{final_df['YEAR'].max()}")
            logger.info(f"Number of months: {len(final_df)}")
            logger.info(f"Average HICP: {final_df['OVERALL_HICP'].mean():.2f}")
            logger.info(f"Min HICP: {final_df['OVERALL_HICP'].min():.2f}")
            logger.info(f"Max HICP: {final_df['OVERALL_HICP'].max():.2f}")
        else:
            logger.error("No data to save")
            
    except Exception as e:
        logger.error(f"Failed to process MCI file: {e}")

if __name__ == "__main__":
    main()
