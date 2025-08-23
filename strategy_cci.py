from loguru import logger
import pandas as pd
import os
import re

def get_category_names():
    return [
        "Earth-moving",
        "Concrete reinforced or not",
        "Wall-building",
        "Plastering",
        "Electrical installations",
        "Hydraulic installations",
        "Central heating installations",
        "Coverings-Coatings",
        "Carpentry",
        "Iron and steel structures",
        "Aluminium structures",
        "Painting",
        "Insulation",
        "Glazing",
        "Elevators",
        "Plaster structures",
        "Special installations without appliances and accessories"
    ]

def parse_cci_sheet_dynamic(sheet):
    logger.info("Parsing CCI sheet dynamically for available quarters and annual averages...")
    data = []
    year = None
    year_pattern = re.compile(r'YEAR\s*(\d{4})')
    overall_pattern = re.compile(r'^OVERALL INDEX$', re.IGNORECASE)
    category_names = get_category_names()
    n_categories = len(category_names)
    i = 0
    while i < len(sheet):
        row = sheet.iloc[i]
        # Detect year
        found_year = False
        for cell in row:
            if isinstance(cell, str):
                m = year_pattern.search(cell)
                if m:
                    year = int(m.group(1))
                    found_year = True
                    logger.debug(f"Detected year: {year} at row {i}")
        if found_year:
            # Look for OVERALL INDEX row
            for j in range(i+1, min(i+10, len(sheet))):
                row_ov = sheet.iloc[j]
                if any(isinstance(cell, str) and overall_pattern.match(cell.strip()) for cell in row_ov):
                    # OVERALL INDEX row found
                    # Dynamically detect available quarters (non-empty columns after the name, before annual average)
                    quarter_labels = []
                    quarter_indices = []
                    for col_idx in range(1, len(row_ov)):
                        val = row_ov.iloc[col_idx]
                        if val is not None and str(val).strip() != '' and not is_float_nan(val):
                            quarter_labels.append(chr(64+col_idx))  # A=1, B=2, C=3, D=4, etc.
                            quarter_indices.append(col_idx)
                        else:
                            break
                    # If more than 4, last is annual average
                    if len(quarter_labels) > 4:
                        quarter_labels = quarter_labels[:4]
                        quarter_indices = quarter_indices[:4]
                    # If last value is annual average, use it
                    avg_idx = quarter_indices[-1] + 1 if quarter_indices else 2
                    # Add OVERALL INDEX quarters
                    for q_idx, col_idx in enumerate(quarter_indices):
                        q = quarter_labels[q_idx]
                        val = row_ov.iloc[col_idx]
                        data.append({
                            'Year': year,
                            'Quarter': q,
                            'Category': 0,
                            'CategoryName': 'OVERALL INDEX',
                            'Value': try_float(val)
                        })
                    # Annual Average
                    avg_val = row_ov.iloc[avg_idx] if avg_idx < len(row_ov) else None
                    if avg_val is not None and str(avg_val).strip() != '' and not is_float_nan(avg_val):
                        data.append({
                            'Year': year,
                            'Quarter': '_Z',
                            'Category': 0,
                            'CategoryName': 'OVERALL INDEX',
                            'Value': try_float(avg_val)
                        })
                    # Now, next 17 rows are categories
                    for cat_idx in range(n_categories):
                        row_cat = sheet.iloc[j + 1 + cat_idx]
                        cat_num = cat_idx + 1
                        cat_name = category_names[cat_idx]
                        # Dynamically detect available quarters for this category
                        cat_quarter_indices = []
                        for col_idx in range(2, len(row_cat)):
                            val = row_cat.iloc[col_idx]
                            if val is not None and str(val).strip() != '' and not is_float_nan(val):
                                cat_quarter_indices.append(col_idx)
                            else:
                                break
                        # If more than 4, last is annual average
                        if len(cat_quarter_indices) > 4:
                            cat_quarter_indices = cat_quarter_indices[:4]
                        # Add category quarters
                        for q_idx, col_idx in enumerate(cat_quarter_indices):
                            q = chr(65 + q_idx)  # A, B, C, D
                            val = row_cat.iloc[col_idx]
                            data.append({
                                'Year': year,
                                'Quarter': q,
                                'Category': cat_num,
                                'CategoryName': cat_name,
                                'Value': try_float(val)
                            })
                        # Annual Average
                        avg_idx = cat_quarter_indices[-1] + 1 if cat_quarter_indices else 3
                        avg_val = row_cat.iloc[avg_idx] if avg_idx < len(row_cat) else None
                        if avg_val is not None and str(avg_val).strip() != '' and not is_float_nan(avg_val):
                            data.append({
                                'Year': year,
                                'Quarter': '_Z',
                                'Category': cat_num,
                                'CategoryName': cat_name,
                                'Value': try_float(avg_val)
                            })
                    i = j + 1 + n_categories
                    break
            else:
                i += 1
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

    cci_files = glob.glob("assets/CCI/*04_F_EN.xlsx")
    if not cci_files:
        logger.error("No CCI file matching '*04_F_EN.xlsx' found in assets/CCI")
        return
    # Pick the most recent file by modification time
    input_file = max(cci_files, key=os.path.getmtime)
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "CCI.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Loading Excel file: {input_file}")
    try:
        xl = pd.ExcelFile(input_file)
        sheet = xl.parse(xl.sheet_names[0], header=None)
        # Forward fill for merged cells in first two columns
        sheet.iloc[:,0] = sheet.iloc[:,0].ffill()
        sheet.iloc[:,1] = sheet.iloc[:,1].ffill()
        # Convert to DataFrame with string columns for easier parsing
        df = sheet.astype(str)
        # Use iterrows for robust parsing
        final_df = parse_cci_sheet_dynamic(df)
        # Add TIME_PERIOD and FREQ columns
        final_df = add_time_period_and_freq(final_df)
        # Impute missing OVERALL INDEX Q1 if needed
        final_df = impute_overall_index_q1(final_df)
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
