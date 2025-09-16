from loguru import logger
import pandas as pd
import os
import re

def get_category_names():
    return [
        "Overall Cost Index",
        "Material Costs Index", 
        "Labour Costs Index"
    ]

def parse_cci_sheet_02_format(sheet):
    logger.info("Parsing CCI sheet for *02_F_EN.xlsx format...")
    data = []
    category_names = get_category_names()
    
    # Look for the data section starting with "Construction Costs Index"
    data_start_row = None
    for i, row in sheet.iterrows():
        if any(isinstance(cell, str) and "Construction Costs Index" in str(cell) for cell in row):
            data_start_row = i
            break
    
    if data_start_row is None:
        logger.error("Could not find 'Construction Costs Index' header")
        return pd.DataFrame(data)
    
    logger.debug(f"Found data section starting at row {data_start_row}")
    
    # Process each year block
    i = data_start_row
    while i < len(sheet):
        row = sheet.iloc[i]
        
        # Check if this row contains a year (4-digit number starting with 2)
        year = None
        for cell in row:
            if isinstance(cell, (int, float)) and not pd.isna(cell):
                year_val = int(cell)
                if 2000 <= year_val <= 2030:  # Reasonable year range
                    year = year_val
                    break
            elif isinstance(cell, str):
                # Try to extract year from string
                year_match = re.search(r'2\d{3}', str(cell))
                if year_match:
                    year = int(year_match.group())
                    break
        
        if year is not None:
            logger.debug(f"Processing year {year} at row {i}")
            
            # Look for the next 3 rows with category data
            for cat_idx in range(3):  # 3 categories: Overall, Material, Labour
                if i + 1 + cat_idx >= len(sheet):
                    break
                    
                cat_row = sheet.iloc[i + 1 + cat_idx]
                cat_name = category_names[cat_idx]
                cat_num = cat_idx + 1
                
                # Extract quarter values (Q1, Q2, Q3, Q4) and annual mean
                # Based on the structure: Year | Q1 | Q2 | Q3 | Q4 | Annual Mean
                quarters = ['A', 'B', 'C', 'D']  # A=Q1, B=Q2, C=Q3, D=Q4
                
                # Process quarters (columns 1-4 after the year)
                for q_idx in range(4):
                    col_idx = q_idx + 1  # Skip year column
                    if col_idx < len(cat_row):
                        val = cat_row.iloc[col_idx]
                        if val is not None and str(val).strip() != '' and not is_float_nan(val):
                            data.append({
                                'Year': year,
                                'Quarter': quarters[q_idx],
                                'Category': cat_num,
                                'CategoryName': cat_name,
                                'Value': try_float(val)
                            })
                
                # Process annual mean (last column)
                annual_col_idx = 5  # Column index for annual mean
                if annual_col_idx < len(cat_row):
                    annual_val = cat_row.iloc[annual_col_idx]
                    if annual_val is not None and str(annual_val).strip() != '' and not is_float_nan(annual_val):
                        data.append({
                            'Year': year,
                            'Quarter': '_Z',
                            'Category': cat_num,
                            'CategoryName': cat_name,
                            'Value': try_float(annual_val)
                        })
            
            # Move to next year block (skip the 3 category rows + 1 empty row)
            i += 4
        else:
            i += 1
    
    return pd.DataFrame(data)

def is_float_nan(val):
    try:
        return pd.isna(float(val))
    except Exception:
        return False

def try_float(val):
    try:
        return float(str(val).replace(",", "."))
    except Exception:
        return None

def add_time_period_and_freq(df):
    # TIME_PERIOD: YEAR-QN (N=1,2,3,4) for quarters, YEAR for annual average (_Z)
    # FREQ: Q for quarters, A for annual average
    def make_time_period(row):
        if row['Quarter'] == '_Z':
            return str(int(float(row['Year'])))
        else:
            # Map A,B,C,D to 1,2,3,4
            q_map = {'A': '1', 'B': '2', 'C': '3', 'D': '4'}
            return f"{int(float(row['Year']))}-Q{q_map.get(row['Quarter'], row['Quarter'])}"
    def make_freq(row):
        return 'A' if row['Quarter'] == '_Z' else 'Q'
    df['TIME_PERIOD'] = df.apply(make_time_period, axis=1)
    df['FREQ'] = df.apply(make_freq, axis=1)
    # Place FREQ next to TIME_PERIOD
    cols = list(df.columns)
    # Move FREQ after TIME_PERIOD
    cols.remove('FREQ')
    cols.insert(cols.index('TIME_PERIOD') + 1, 'FREQ')
    return df[cols]

def impute_overall_index_q1(df):
    # For each year, if OVERALL INDEX Q1 (A) is missing, impute it using annual average and other quarters
    logger.info("Imputing missing OVERALL INDEX Q1 values if needed...")
    df_out = df.copy()
    # Only for Category==0 and Quarter in A,B,C,D,_Z
    for year in df_out['Year'].unique():
        mask_oi = (df_out['Category'] == 0) & (df_out['Year'] == year)
        mask_q1 = mask_oi & (df_out['Quarter'] == 'A')
        if not mask_q1.any():
            # Q1 missing, try to impute
            mask_q2 = mask_oi & (df_out['Quarter'] == 'B')
            mask_q3 = mask_oi & (df_out['Quarter'] == 'C')
            mask_q4 = mask_oi & (df_out['Quarter'] == 'D')
            mask_avg = mask_oi & (df_out['Quarter'] == '_Z')
            try:
                q2 = df_out.loc[mask_q2, 'Value'].values[0] if mask_q2.any() else None
                q3 = df_out.loc[mask_q3, 'Value'].values[0] if mask_q3.any() else None
                q4 = df_out.loc[mask_q4, 'Value'].values[0] if mask_q4.any() else None
                avg = df_out.loc[mask_avg, 'Value'].values[0] if mask_avg.any() else None
                if avg is not None and all(x is not None for x in [q2, q3, q4]):
                    q1 = avg * 4 - (q2 + q3 + q4)
                else:
                    # Fallback: use mean of available quarters or avg
                    vals = [v for v in [q2, q3, q4, avg] if v is not None]
                    q1 = sum(vals) / len(vals) if vals else None
                if q1 is not None:
                    logger.warning(f"Imputed OVERALL INDEX Q1 for year {year}: {q1}")
                    # Insert the row
                    new_row = {
                        'Year': year,
                        'Quarter': 'A',
                        'Category': 0,
                        'CategoryName': 'OVERALL INDEX',
                        'Value': q1
                    }
                    # Add TIME_PERIOD and FREQ
                    q_map = {'A': '1'}
                    new_row['TIME_PERIOD'] = f"{int(float(year))}-Q{q_map['A']}"
                    new_row['FREQ'] = 'Q'
                    # Insert in correct order
                    df_out = pd.concat([df_out, pd.DataFrame([new_row])], ignore_index=True)
            except Exception as e:
                logger.error(f"Failed to impute OVERALL INDEX Q1 for year {year}: {e}")
    # Resort for nice output
    df_out = df_out.sort_values(['Year', 'Category', 'Quarter', 'TIME_PERIOD']).reset_index(drop=True)
    return df_out

def main():
    import glob
    import os

    cci_files = glob.glob("assets/CCI/*02_F_EN.xlsx")
    if not cci_files:
        logger.error("No CCI file matching '*02_F_EN.xlsx' found in assets/CCI")
        return
    # Pick the most recent file by modification time
    input_file = max(cci_files, key=os.path.getmtime)
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "CCI_02.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        # Convert to DataFrame for parsing
        df = sheet
        # Use the new parser for *02_F_EN.xlsx format
        final_df = parse_cci_sheet_02_format(df)
        # Add TIME_PERIOD and FREQ columns
        final_df = add_time_period_and_freq(final_df)
        # Clean up
        final_df = final_df.dropna(subset=["Value"]).reset_index(drop=True)
        # in column "Category" make it "K" + str(int(col))
        final_df['Category'] = "K" + final_df['Category'].astype(str)
        logger.success(f"Parsed {len(final_df)} rows of CCI data.")
        final_df.to_excel(output_file, index=False)
        logger.success(f"Saved normalized CCI data to {output_file}")
    except Exception as e:
        logger.error(f"Failed to process CCI file: {e}")

if __name__ == "__main__":
    main()
