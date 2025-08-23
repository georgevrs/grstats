from loguru import logger
import pandas as pd
import os
import re

def parse_bla_details_sheet(sheet):
    """
    Parse the BLA details sheet to extract regional building activity data.
    Expected structure: Regional breakdown with new dwellings and improvements data.
    """
    logger.info("Parsing BLA details sheet for regional building activity data...")
    data = []
    
    # Find the data table - look for the first data row (Σύνολο Χώρας)
    start_row = None
    for i, row in sheet.iterrows():
        if isinstance(row.iloc[0], str) and "Σύνολο Χώρας" in str(row.iloc[0]):
            start_row = i
            break
    
    if start_row is None:
        logger.error("Could not find data table start")
        return pd.DataFrame()
    
    # Extract year and month from the title
    year = None
    month = None
    
    # Look for the date information in the header rows
    for i in range(min(10, len(sheet))):  # Check first 10 rows
        row = sheet.iloc[i]
        if isinstance(row.iloc[0], str):
            cell_text = str(row.iloc[0]).strip()
            
            # Define month mappings (Greek and English)
            month_mappings = {
                'Ιανουάριος': 1, 'January': 1,
                'Φεβρουάριος': 2, 'February': 2,
                'Μάρτιος': 3, 'March': 3,
                'Απρίλιος': 4, 'April': 4,
                'Μάιος': 5, 'May': 5,
                'Ιούνιος': 6, 'June': 6,
                'Ιούλιος': 7, 'July': 7,
                'Αύγουστος': 8, 'August': 8,
                'Σεπτέμβριος': 9, 'September': 9,
                'Οκτώβριος': 10, 'October': 10,
                'Νοέμβριος': 11, 'November': 11,
                'Δεκέμβριος': 12, 'December': 12
            }
            
            # Look for month and year patterns
            detected_month = None
            for month_name, month_num in month_mappings.items():
                if month_name in cell_text:
                    detected_month = month_num
                    break
            
            if detected_month:
                # Extract year from the same row or next row
                year_match = re.search(r'(\d{4})', cell_text)
                if year_match:
                    year = int(year_match.group(1))
                    month = detected_month
                    break
                else:
                    # Check next row for year
                    if i + 1 < len(sheet):
                        next_row = sheet.iloc[i + 1]
                        if isinstance(next_row.iloc[0], str):
                            year_match = re.search(r'(\d{4})', str(next_row.iloc[0]))
                            if year_match:
                                year = int(year_match.group(1))
                                month = detected_month
                                break
    
    if year is None or month is None:
        logger.error("Could not extract year and month from file header")
        return pd.DataFrame()
    
    logger.debug(f"Processing data for {year}-{month:02d}")
    
    # Process each row starting from the data
    for i in range(start_row, len(sheet)):
        row = sheet.iloc[i]
        
        # Skip empty rows
        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
            continue
            
        # Check if this is a region row (contains region name)
        region_cell = str(row.iloc[0]).strip()
        
        # Skip if it's empty or doesn't contain region data
        if region_cell == '' or not any(keyword in region_cell for keyword in ['ΠΕΡΙΦΕΡΕΙΑ', 'ΕΝΟΤΗΤΑ', 'Σύνολο']):
            continue
            
        # Extract region name - look for English name in the same row
        region = region_cell
        
        # Try to find English region name in the same row (usually in the last column)
        english_region = None
        for col_idx in range(len(row)):
            cell_value = str(row.iloc[col_idx]).strip()
            if cell_value and any(keyword in cell_value.upper() for keyword in ['REGION', 'UNIT', 'GREECE', 'TOTAL']):
                english_region = cell_value
                break
        
        # Use English region name if found, otherwise keep Greek name
        if english_region:
            region = english_region
        
        # Extract numeric data from columns
        try:
            # Column structure based on the data:
            # Region | Number | Rooms | New Dwellings Volume | Surface | Improvements Volume
            number = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
            rooms = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
            new_dwellings_volume = int(row.iloc[3]) if pd.notna(row.iloc[3]) else 0
            surface = int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            improvements_volume = int(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            
            data.append({
                'YEAR': year,
                'MONTH': month,
                'FREQ': 'M',  # Monthly frequency
                'REGION': region,
                'NUMBER': number,
                'ROOMS': rooms,
                'NEW_DWELLINGS_VOLUME': new_dwellings_volume,
                'SURFACE': surface,
                'IMPROVEMENTS_VOLUME': improvements_volume
            })
            
            logger.debug(f"Added data for {region}: {number} dwellings, {rooms} rooms, {new_dwellings_volume} m3 new, {surface} m2, {improvements_volume} m3 improvements")
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse row {i} for region '{region}': {e}")
            continue
    
    df = pd.DataFrame(data)
    if not df.empty:
        df = df[['YEAR', 'MONTH', 'FREQ', 'REGION', 'NUMBER', 'ROOMS', 'NEW_DWELLINGS_VOLUME', 'SURFACE', 'IMPROVEMENTS_VOLUME']]
        logger.success(f"Parsed {len(df)} rows of BLA details data")
    else:
        logger.warning("No data was parsed from the sheet")
    return df

def main():
    input_file = "assets/BLA/A1302_SOP03_TB_MM_03_2025_04_F_BI.xlsx"
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "BLA_04.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        
        # Parse the sheet
        final_df = parse_bla_details_sheet(sheet)
        
        if not final_df.empty:
            # Clean up - remove any rows with missing essential data
            final_df = final_df.dropna(subset=['YEAR', 'MONTH', 'FREQ', 'REGION']).reset_index(drop=True)
            
            # Save to Excel
            final_df.to_excel(output_file, index=False)
            logger.success(f"Saved normalized BLA details data to {output_file}")
            logger.info(f"Final dataset shape: {final_df.shape}")
            logger.info(f"Year: {final_df['YEAR'].iloc[0]}")
            logger.info(f"Month: {final_df['MONTH'].iloc[0]}")
            logger.info(f"Number of regions: {len(final_df)}")
            logger.info(f"Total dwellings: {final_df['NUMBER'].sum():,.0f}")
            logger.info(f"Total rooms: {final_df['ROOMS'].sum():,.0f}")
            logger.info(f"Total new dwellings volume: {final_df['NEW_DWELLINGS_VOLUME'].sum():,.0f} m3")
            logger.info(f"Total surface: {final_df['SURFACE'].sum():,.0f} m2")
            logger.info(f"Total improvements volume: {final_df['IMPROVEMENTS_VOLUME'].sum():,.0f} m3")
        else:
            logger.error("No data to save")
            
    except Exception as e:
        logger.error(f"Failed to process BLA details file: {e}")

if __name__ == "__main__":
    main()
