from loguru import logger
import pandas as pd
import os
import re

def create_time_period(df):
    """
    Create proper time_period column from YEAR and MONTH columns.
    - If freq is 'A' (annual), time_period = YEAR only (e.g., '2022')
    - If freq is 'M' (monthly), time_period = YEAR-MXX format (e.g., '2022-M02')
    """
    time_periods = []
    
    for _, row in df.iterrows():
        year = str(row['YEAR'])
        month = row['MONTH']
        freq = row['FREQ']
        
        if freq == 'A':
            # Annual data: only year
            time_periods.append(year)
        elif freq == 'M' and pd.notna(month) and month is not None:
            # Monthly data: YEAR-MXX format
            try:
                month_int = int(month)
                month_str = f"M{month_int:02d}"
                time_periods.append(f"{year}-{month_str}")
            except (ValueError, TypeError):
                # Fallback for invalid month data
                time_periods.append(None)
        else:
            # Fallback for invalid data
            time_periods.append(None)
    
    return time_periods

def parse_bla_16_sheet(sheet):
    """
    Parse the BLA Table 16 sheet to extract new establishments data.
    Expected structure: Categories of establishment use with urban/semi-urban/rural breakdown.
    """
    logger.info("Parsing BLA Table 16 sheet for new establishments data...")
    data = []
    
    # Find the data table - look for the first data row (Σ Υ Ν Ο Λ Ο  Ε Λ Λ Α Δ Ο Σ)
    start_row = None
    for i, row in sheet.iterrows():
        if isinstance(row.iloc[0], str) and "Σ Υ Ν Ο Λ Ο  Ε Λ Λ Α Δ Ο Σ" in str(row.iloc[0]):
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
            
        # Check if this is a category row (contains establishment category name)
        category_cell = str(row.iloc[0]).strip()
        
        # Skip if it's empty or doesn't contain category data
        if category_cell == '' or category_cell in ['Σ Υ Ν Ο Λ Ο  Ε Λ Λ Α Δ Ο Σ']:
            continue
            
        # Extract English category name from the last column (column 9)
        english_category = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else ""
        
        # Use English category name if it exists and is not empty, otherwise translate Greek name
        if english_category and english_category != '':
            category = english_category
        else:
            # Translate common Greek category names to English
            greek_to_english = {
                'Αγνώστου Προορισμού': 'Unspecified',
                'Βιομηχανικά': 'Manufacturing',
                'Γεωργικά': 'Agricultural',
                'Γραφεία': 'Offices',
                'Εκπαιδευτικά': 'Educational',
                'Εμπορικά': 'Commercial',
                'Καταλύματα σύντομης διαμονής (Ενοικιαζόμενα καταλύματα)': 'Short stay accommodation (rooms for rent)',
                'Κτηνοτροφικά': 'Livestock',
                'Λοιπά': 'Other',
                'Λοιπές συλλογικές κατοικίες': 'Residences for communities',
                'Ξενοδοχεία': 'Hotels',
                'Περίθαλψης': 'Health care'
            }
            category = greek_to_english.get(category_cell, category_cell)
        
        # Extract numeric data from columns
        try:
            # Column structure based on the data:
            # Category | TOTAL Number | TOTAL Volume | URBAN Number | URBAN Volume | SEMI-URBAN Number | SEMI-URBAN Volume | RURAL Number | RURAL Volume | English Category
            total_number = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
            total_volume = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
            urban_number = int(row.iloc[3]) if pd.notna(row.iloc[3]) else 0
            urban_volume = int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            semi_urban_number = int(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            semi_urban_volume = int(row.iloc[6]) if pd.notna(row.iloc[6]) else 0
            rural_number = int(row.iloc[7]) if pd.notna(row.iloc[7]) else 0
            rural_volume = int(row.iloc[8]) if pd.notna(row.iloc[8]) else 0
            
            data.append({
                'YEAR': year,
                'MONTH': month,
                'FREQ': 'M',  # Monthly frequency
                'CATEGORY': category,
                'TOTAL_NUMBER': total_number,
                'TOTAL_VOLUME': total_volume,
                'URBAN_NUMBER': urban_number,
                'URBAN_VOLUME': urban_volume,
                'SEMI_URBAN_NUMBER': semi_urban_number,
                'SEMI_URBAN_VOLUME': semi_urban_volume,
                'RURAL_NUMBER': rural_number,
                'RURAL_VOLUME': rural_volume
            })
            
            logger.debug(f"Added data for {category}: {total_number} total establishments, {total_volume} m3 total volume")
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse row {i} for category '{category}': {e}")
            continue
    
    df = pd.DataFrame(data)
    if not df.empty:
        df = df[['YEAR', 'MONTH', 'FREQ', 'CATEGORY', 'TOTAL_NUMBER', 'TOTAL_VOLUME', 'URBAN_NUMBER', 'URBAN_VOLUME', 'SEMI_URBAN_NUMBER', 'SEMI_URBAN_VOLUME', 'RURAL_NUMBER', 'RURAL_VOLUME']]
        logger.success(f"Parsed {len(df)} rows of BLA Table 16 data")
    else:
        logger.warning("No data was parsed from the sheet")
    return df

def main():
    import glob
    import os

    bla_files = glob.glob("assets/BLA/*16_F_BI.xlsx")
    if not bla_files:
        logger.error("No BLA file matching '*16_F_BI.xlsx' found in assets/BLA")
        return
    input_file = max(bla_files, key=os.path.getmtime)
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "BLA_16.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        
        # Parse the sheet
        final_df = parse_bla_16_sheet(sheet)
        
        if not final_df.empty:
            # Clean up - remove any rows with missing essential data
            final_df = final_df.dropna(subset=['YEAR', 'MONTH', 'FREQ', 'CATEGORY']).reset_index(drop=True)
            
            # Create proper time_period column
            final_df['time_period'] = create_time_period(final_df)
            
            # Reorder columns to include time_period
            final_df = final_df[['YEAR', 'MONTH', 'FREQ', 'time_period', 'CATEGORY', 'TOTAL_NUMBER', 'TOTAL_VOLUME', 'URBAN_NUMBER', 'URBAN_VOLUME', 'SEMI_URBAN_NUMBER', 'SEMI_URBAN_VOLUME', 'RURAL_NUMBER', 'RURAL_VOLUME']]
            
            # Save to Excel
            final_df.to_excel(output_file, index=False)
            logger.success(f"Saved normalized BLA Table 16 data to {output_file}")
            logger.info(f"Final dataset shape: {final_df.shape}")
            logger.info(f"Year: {final_df['YEAR'].iloc[0]}")
            logger.info(f"Month: {final_df['MONTH'].iloc[0]}")
            logger.info(f"Number of categories: {len(final_df)}")
            logger.info(f"Total establishments: {final_df['TOTAL_NUMBER'].sum():,.0f}")
            logger.info(f"Total volume: {final_df['TOTAL_VOLUME'].sum():,.0f} m3")
            logger.info(f"Urban establishments: {final_df['URBAN_NUMBER'].sum():,.0f}")
            logger.info(f"Urban volume: {final_df['URBAN_VOLUME'].sum():,.0f} m3")
            logger.info(f"Semi-urban establishments: {final_df['SEMI_URBAN_NUMBER'].sum():,.0f}")
            logger.info(f"Semi-urban volume: {final_df['SEMI_URBAN_VOLUME'].sum():,.0f} m3")
            logger.info(f"Rural establishments: {final_df['RURAL_NUMBER'].sum():,.0f}")
            logger.info(f"Rural volume: {final_df['RURAL_VOLUME'].sum():,.0f} m3")
        else:
            logger.error("No data to save")
            
    except Exception as e:
        logger.error(f"Failed to process BLA Table 16 file: {e}")

if __name__ == "__main__":
    main()
