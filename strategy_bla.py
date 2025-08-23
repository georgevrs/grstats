from loguru import logger
import pandas as pd
import os
import re

def parse_bla_sheet(sheet):
    """
    Parse the BLA sheet to extract monthly building activity data.
    """
    logger.info("Parsing BLA sheet for monthly building activity data...")
    data = []
    start_row = 7  # Data starts after header (row 6, 0-based)
    current_year = None
    for i in range(start_row, len(sheet)):
        row = sheet.iloc[i]
        # Year row: [int, str with 'Σύνολο', int, int, int]
        if isinstance(row[0], int) and isinstance(row[1], str) and "Σύνολο" in row[1]:
            current_year = row[0]
            logger.debug(f"Found year: {current_year} at row {i}")
            
            # Add annual total data
            try:
                annual_permits = row[2]
                annual_area = row[3]
                annual_volume = row[4]
                
                data.append({
                    'FREQ': 'A',
                    'YEAR': current_year,
                    'MONTH': None,
                    'LICENCES': annual_permits,
                    'AREA': annual_area,
                    'VOLUME': annual_volume
                })
                logger.debug(f"Added annual data for {current_year}: permits={annual_permits}, area={annual_area}, volume={annual_volume}")
            except Exception as e:
                logger.warning(f"Could not parse annual data for year {current_year}: {e}")
            
            continue
        # Month row: [nan, int 1-12, int, int, int]
        if pd.isna(row[0]) and isinstance(row[1], int) and 1 <= row[1] <= 12:
            month = row[1]
            permits = row[2]
            area = row[3]
            volume = row[4]
            data.append({
                'FREQ': 'M',
                'YEAR': current_year,
                'MONTH': month,
                'LICENCES': permits,
                'AREA': area,
                'VOLUME': volume
            })
            logger.debug(f"Added monthly data for {current_year}-{month:02d}: {permits} permits, {area} m2, {volume} m3")
    df = pd.DataFrame(data)
    if not df.empty:
        df = df[['FREQ', 'YEAR', 'MONTH', 'LICENCES', 'AREA', 'VOLUME']]
        logger.success(f"Parsed {len(df)} rows of BLA data")
    else:
        logger.warning("No data was parsed from the sheet")
    return df

def main():
    input_file = "assets/BLA/A1302_SOP03_TS_MM_12_2007_03_2025_01_F_Bl.xlsx"
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "BLA.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        
        # Parse the sheet
        final_df = parse_bla_sheet(sheet)
        
        if not final_df.empty:
            # Clean up - remove any rows with missing data, but keep annual rows (MONTH=None)
            # Only drop rows where essential data is missing
            final_df = final_df.dropna(subset=['FREQ', 'YEAR', 'LICENCES', 'AREA', 'VOLUME']).reset_index(drop=True)
            
            # Save to Excel
            final_df.to_excel(output_file, index=False)
            logger.success(f"Saved normalized BLA data to {output_file}")
            logger.info(f"Final dataset shape: {final_df.shape}")
            logger.info(f"Year range: {final_df['YEAR'].min()} - {final_df['YEAR'].max()}")
            logger.info(f"Total permits: {final_df['LICENCES'].sum():,.0f}")
            logger.info(f"Total area: {final_df['AREA'].sum():,.0f} m2")
            logger.info(f"Total volume: {final_df['VOLUME'].sum():,.0f} m3")
        else:
            logger.error("No data to save")
            
    except Exception as e:
        logger.error(f"Failed to process BLA file: {e}")

if __name__ == "__main__":
    main()
