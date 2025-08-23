from loguru import logger
import pandas as pd
import os
import re

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

def main():
    input_file = "assets/MCI/A0515_DKT90_TS_MM_01_1996_06_2025_03_F_EN.xlsx"
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "HICP.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        
        # Parse the sheet
        final_df = parse_hicp_sheet(sheet)
        
        if not final_df.empty:
            # Clean up - remove any rows with missing essential data
            final_df = final_df.dropna(subset=['YEAR', 'MONTH', 'FREQ', 'HICP']).reset_index(drop=True)
            
            # Save to Excel
            final_df.to_excel(output_file, index=False)
            logger.success(f"Saved normalized HICP data to {output_file}")
            logger.info(f"Final dataset shape: {final_df.shape}")
            logger.info(f"Year range: {final_df['YEAR'].min()}-{final_df['YEAR'].max()}")
            logger.info(f"Number of data points: {len(final_df)}")
            logger.info(f"Average HICP: {final_df['HICP'].mean():.2f}")
            logger.info(f"Min HICP: {final_df['HICP'].min():.2f}")
            logger.info(f"Max HICP: {final_df['HICP'].max():.2f}")
        else:
            logger.error("No data to save")
            
    except Exception as e:
        logger.error(f"Failed to process HICP file: {e}")

if __name__ == "__main__":
    main()
