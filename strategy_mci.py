import re
import hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd
import os

# ---------- Config ----------
# Use current working directory instead of hardcoded /mnt/data
INPUT_DIR = Path("assets/MCI")
OUTPUT_PARQUET = Path("unified_dataset.parquet")
OUTPUT_EXCEL = Path("assets/prepared/MCI.xlsx")

TIME_CANDIDATE_COLS = {"time", "period", "date", "month", "year"}  # case-insensitive

# ---------- Helpers ----------
def extract_dataset_id_and_vintage(fname: str):
    """
    Example: A0511_DKT60_TS_MM_01_2000_06_2025_02_F_EN.xlsx
    Return dataset_id='A0511_DKT60_TS_MM_01', vintage='2025-02'
    """
    stem = Path(fname).stem
    parts = stem.split("_")
    # Heuristic: dataset_id often the first 4–5 tokens before the historical start/end and vintage
    # We'll look for last yyyy mm block before the 'F' or language code.
    # Format observed: <dataset_id>_<start_year>_<start_month>_<end_year>_<end_month>_F_<lang>
    # vintage should be the "end_year" + "end_month".
    try:
        # Find last 6 consecutive tokens that look like year, month pairs
        years = [i for i,p in enumerate(parts) if re.fullmatch(r"\d{4}", p)]
        # Use the last year index as vintage year; assume next token is month
        if years:
            y_idx = years[-1]
            v_year = parts[y_idx]
            v_month = parts[y_idx+1] if y_idx+1 < len(parts) else "01"
            vintage = f"{v_year}-{v_month.zfill(2)}"
            dataset_id = "_".join(parts[:y_idx-1])  # conservative slice
            if not dataset_id:  # fallback
                dataset_id = parts[0]
        else:
            dataset_id = parts[0]
            vintage = None
    except Exception:
        dataset_id = parts[0]
        vintage = None

    return dataset_id, vintage

def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns into 'lvl0 | lvl1 | ...' and forward-fill empties."""
    if isinstance(df.columns, pd.MultiIndex):
        # Fill empty pieces, then join
        filled = []
        for col_tuple in df.columns:
            parts = [str(x).strip() if (x is not None and str(x).strip() != "") else "" for x in col_tuple]
            # forward-fill within tuple
            for i in range(1, len(parts)):
                if parts[i] == "":
                    parts[i] = parts[i-1]
            label = " | ".join([p for p in parts if p != ""])
            filled.append(label)
        df.columns = dedupe_column_labels(filled)
    else:
        df.columns = dedupe_column_labels([str(c).strip() for c in df.columns])
    return df

def dedupe_column_labels(cols):
    """Ensure unique column names."""
    seen, result = {}, []
    for c in cols:
        base = c or "Unnamed"
        if base not in seen:
            seen[base] = 0
            result.append(base)
        else:
            seen[base] += 1
            result.append(f"{base}__{seen[base]}")
    return result

def find_time_column(df: pd.DataFrame):
    """Find a likely time/period column name."""
    # For MCI files, look for month columns specifically
    month_cols = [col for col in df.columns if str(col).upper() in ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUNE', 'JULY', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']]
    if month_cols:
        return month_cols[0]  # Return first month column
    
    # Fallback to original logic
    lower_map = {c: str(c).strip().lower() for c in df.columns}
    for c, lc in lower_map.items():
        if lc in TIME_CANDIDATE_COLS:
            return c
    # Heuristic: first column often is time
    return df.columns[0]

def normalize_period_and_freq(s: pd.Series):
    """
    Convert various time strings to (time_period, freq).
    Supports: 'YYYY-MM', 'YYYYMmm', 'Mon-YYYY', 'YYYY', 'YYYY-Q#', and month names
    """
    def norm_one(x):
        if pd.isna(x):
            return (None, None)
        t = str(x).strip().upper()

        # Month names (JAN, FEB, MAR, etc.)
        month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
        }
        
        if t in month_map:
            # For MCI data, we'll use a placeholder year since we don't have it in the column
            # The actual year should come from the filename or be inferred
            return (f"2000-{month_map[t]}", "M")

        # YYYY-MM or YYYY-M
        m = re.fullmatch(r"(\d{4})[-/\.](\d{1,2})", t)
        if m:
            y, mo = m.group(1), m.group(2).zfill(2)
            return (f"{y}-{mo}", "M")

        # YYYYMM
        m = re.fullmatch(r"(\d{4})(\d{2})", t)
        if m:
            y, mo = m.group(1), m.group(2)
            return (f"{y}-{mo}", "M")

        # YYYY Mmm or Mon-YYYY
        try:
            dt = pd.to_datetime(t, errors="raise", format="%b-%Y")
            return (f"{dt.year}-{str(dt.month).zfill(2)}", "M")
        except Exception:
            pass
        try:
            dt = pd.to_datetime(t, errors="raise")
            # If it parsed to a date, emit monthly YYYY-MM
            return (f"{dt.year}-{str(dt.month).zfill(2)}", "M")
        except Exception:
            pass

        # YYYY-Q#
        m = re.fullmatch(r"(\d{4})[-/ ]?Q([1-4])", t, flags=re.IGNORECASE)
        if m:
            y, q = m.group(1), m.group(2)
            return (f"{y}-Q{q}", "Q")

        # YYYY only
        m = re.fullmatch(r"(\d{4})", t)
        if m:
            return (m.group(1), "A")

        # 2000M06 style
        m = re.fullmatch(r"(\d{4})M(\d{2})", t, flags=re.IGNORECASE)
        if m:
            y, mo = m.group(1), m.group(2)
            return (f"{y}-{mo}", "M")

        # Fallback: return raw
        return (t, None)

    res = s.map(norm_one)
    tp = [r[0] for r in res]
    fq = [r[1] for r in res]
    return pd.Series(tp), pd.Series(fq)

def series_id_from_label(label: str) -> str:
    """Deterministic short id from label."""
    return hashlib.sha1(label.encode("utf-8")).hexdigest()[:12]

def try_parse_with_multiheaders(xls: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    """Try multiple header depths, return the 'best' structured frame."""
    for hdr in ([0,1,2], [0,1], [0]):
        try:
            df = xls.parse(sheet_name=sheet, header=hdr)
            if df is not None and df.shape[1] >= 2:
                return df
        except Exception:
            continue
    # last fallback: no header
    df = xls.parse(sheet_name=sheet, header=None)
    return df

def find_data_start_row(df: pd.DataFrame) -> int:
    """Find the row where actual data starts by looking for month names."""
    month_patterns = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUNE', 'JULY', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    for idx, row in df.iterrows():
        row_str = ' '.join(str(cell).upper() for cell in row if pd.notna(cell))
        if any(month in row_str for month in month_patterns):
            return idx
    return 0

def clean_mci_dataframe_v2(df: pd.DataFrame, material_names: list) -> pd.DataFrame:
    """Clean and restructure MCI dataframes with time periods in first column."""
    # For this MCI file structure:
    # Row 11: Material group names
    # Row 12+: Time periods like 'JAN-00', 'FEB-00', etc. in first column
    
    # Use the material names from row 11 as column names
    # Find the first row with time period data
    data_start = None
    for idx, row in df.iterrows():
        if pd.notna(row.iloc[0]) and '-' in str(row.iloc[0]):
            data_start = idx
            break
    
    if data_start is None:
        return df  # fallback
    
    # Create new dataframe starting from the data row
    data_df = df.iloc[data_start:].copy()
    
    # Set column names
    data_df.columns = ['time_period'] + material_names[1:]  # Skip first column (Year and month)
    
    # Drop rows where time_period is NaN or empty
    data_df = data_df.dropna(subset=['time_period'])
    
    # Clean up the dataframe
    data_df = data_df.dropna(how='all')  # Remove completely empty rows
    
    return data_df

def clean_mci_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and restructure MCI dataframes specifically.
    
    MCI structure v1 has:
    - Multiple sections with different data types
    - "MONTHLY MATERIAL COST INDICES YEAR XXXX" sections (actual index values)
    - "MONTHLY CHANGES YEAR XXXX" sections (percentage changes)
    - Each section has 16 material groups (OVERALL INDEX + 15 numbered ones)
    - Sections are separated by blank rows
    """
    
    # Find the header row (contains month names)
    header_row = None
    for idx, row in df.iterrows():
        row_str = ' '.join(str(cell).upper() for cell in row if pd.notna(cell))
        if 'JAN' in row_str and 'FEB' in row_str and 'MAR' in row_str:
            header_row = idx
            break
    
    if header_row is None:
        return df  # fallback
    
    # Extract headers from the header row
    headers = df.iloc[header_row].tolist()
    
    # Extract only the month columns (skip ANNUAL AVERAGE)
    month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUNE', 'JULY', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    month_indices = []
    for i, header in enumerate(headers):
        if str(header).upper() in month_names:
            month_indices.append(i)
    
    # Process data starting from the next row
    data_start = header_row + 1
    all_data = []
    
    row_idx = data_start
    
    while row_idx < len(df):
        # Look for section headers
        section_header = str(df.iloc[row_idx, 0]) if pd.notna(df.iloc[row_idx, 0]) else ""
        
        # Check if this is a section header
        if "MONTHLY MATERIAL COST INDICES" in section_header:
            data_type = "COST_INDICES"
            # Extract year from header
            year_match = re.search(r'YEAR (\d{4})', section_header)
            current_year = int(year_match.group(1)) if year_match else None
        elif "MONTHLY CHANGES" in section_header:
            data_type = "CHANGES"
            # Extract year from header
            year_match = re.search(r'YEAR (\d{4})', section_header)
            current_year = int(year_match.group(1)) if year_match else None
        else:
            # Not a section header, skip to next row
            row_idx += 1
            continue
        
        if current_year is None:
            row_idx += 1
            continue
        
        # Skip the next 2 rows (Base year info and blank row)
        row_idx += 3
        
        # Process up to 16 rows (OVERALL INDEX + 15 material groups) or until blank row
        material_groups = []
        year_data = []
        
        for group_idx in range(16):
            if row_idx >= len(df):
                break
                
            material_group = df.iloc[row_idx, 1]  # Column 1 has material groups
            
            # If material group is NaN or empty, we've hit a separator - end this section
            if pd.isna(material_group) or str(material_group).strip() == '':
                break
                
            # Extract month values for this material group
            month_values = []
            for month_idx in month_indices:
                if month_idx < len(df.columns):
                    month_values.append(df.iloc[row_idx, month_idx])
                else:
                    month_values.append(None)
            
            year_data.append(month_values)
            material_groups.append(str(material_group).strip())
            row_idx += 1
        
        # Convert year data to proper format
        if year_data and material_groups:
            for group_idx, (material_group, values) in enumerate(zip(material_groups, year_data)):
                for month_idx, (month_name, value) in enumerate(zip(month_names, values)):
                    if pd.notna(value):
                        all_data.append({
                            'Material_Group': material_group,
                            'Month': month_name,
                            'Year': current_year,
                            'Value': value,
                            'Data_Type': data_type
                        })
        
        # Skip any blank rows until next section
        while row_idx < len(df) and (pd.isna(df.iloc[row_idx, 1]) or str(df.iloc[row_idx, 1]).strip() == ''):
            row_idx += 1
    
    # Convert to DataFrame
    if all_data:
        result_df = pd.DataFrame(all_data)
        return result_df
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data found

def clean_time_periods(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and fix time periods in the dataframe."""
    # Sort by time_period to ensure proper ordering for year inference
    df = df.sort_values('time_period').reset_index(drop=True)
    
    cleaned_periods = []
    cleaned_freqs = []
    
    for idx, row in df.iterrows():
        time_period = row['time_period']
        freq = row['freq']
        
        if pd.isna(time_period):
            cleaned_periods.append(None)
            cleaned_freqs.append(None)
            continue
            
        time_str = str(time_period).strip()
        
        # Handle ANNUAL AVERAGE entries
        if 'ANNUAL AVERAGE' in time_str.upper():
            # Extract year from ANNUAL AVERAGE-YYYY format
            year_match = re.search(r'(\d{4})', time_str)
            if year_match:
                cleaned_periods.append(year_match.group(1))
                cleaned_freqs.append('A')  # Annual frequency
            else:
                cleaned_periods.append(time_str)
                cleaned_freqs.append(freq)
            continue
        
        # Handle wrong time periods like "20-08" or "20-09"
        if re.match(r'^\d{2}-\d{2}$', time_str):
            # This is a wrong format like "20-08"
            # Look for the previous valid time period to infer the year
            prev_year = None
            for i in range(idx-1, -1, -1):
                prev_period = df.iloc[i]['time_period']
                if pd.notna(prev_period) and re.match(r'^\d{4}-\d{2}$', str(prev_period)):
                    prev_year = str(prev_period).split('-')[0]
                    break
            
            if prev_year:
                month = time_str.split('-')[1]
                cleaned_periods.append(f"{prev_year}-{month}")
                cleaned_freqs.append('M')  # Monthly frequency
            else:
                # Fallback: assume 2020s decade for "20-XX" format
                month = time_str.split('-')[1]
                year_part = time_str.split('-')[0]
                if year_part == '20':
                    cleaned_periods.append(f"2020-{month}")
                elif year_part == '21':
                    cleaned_periods.append(f"2021-{month}")
                elif year_part == '22':
                    cleaned_periods.append(f"2022-{month}")
                elif year_part == '23':
                    cleaned_periods.append(f"2023-{month}")
                elif year_part == '24':
                    cleaned_periods.append(f"2024-{month}")
                elif year_part == '25':
                    cleaned_periods.append(f"2025-{month}")
                else:
                    # Generic fallback
                    cleaned_periods.append(f"202{year_part}-{month}")
                cleaned_freqs.append('M')
        elif re.match(r'^\d{4}$', time_str):
            # This is just a year like "2000", "2001", etc.
            cleaned_periods.append(time_str)
            cleaned_freqs.append('A')  # Annual frequency
        else:
            # Normal time period, keep as is
            cleaned_periods.append(time_str)
            cleaned_freqs.append(freq)
    
    df['time_period'] = cleaned_periods
    df['freq'] = cleaned_freqs
    
    return df

def standardize_series_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize series labels by removing "(Change)" suffix and other variations
    to ensure consistent material names across different data types.
    """
    print("Standardizing series labels...")
    
    # Create a copy to avoid modifying the original
    df_standardized = df.copy()
    
    # Show original labels before standardization
    print("Original unique labels:", sorted(df_standardized['series_label'].unique()))
    
    # Remove "(Change)" suffix from series labels
    df_standardized['series_label'] = df_standardized['series_label'].str.replace(r'\s*\(Change\)\s*', '', regex=True)
    
    # Also remove any trailing whitespace
    df_standardized['series_label'] = df_standardized['series_label'].str.strip()
    
    # Normalize quotes (convert curly quotes to straight quotes)
    # Replace curly apostrophes with straight ones
    df_standardized['series_label'] = df_standardized['series_label'].str.replace('\u2019', "'")  # Right single quotation mark
    df_standardized['series_label'] = df_standardized['series_label'].str.replace('\u2018', "'")  # Left single quotation mark
    df_standardized['series_label'] = df_standardized['series_label'].str.replace('\u201D', '"')  # Right double quotation mark
    df_standardized['series_label'] = df_standardized['series_label'].str.replace('\u201C', '"')  # Left double quotation mark
    
    # Filter out invalid labels like "MATERIAL GROUPS"
    df_standardized = df_standardized[df_standardized['series_label'] != 'MATERIAL GROUPS']
    
    # Get unique labels after standardization
    unique_labels = df_standardized['series_label'].unique()
    
    # Standardize common variations - this ensures exact matches
    # Note: We don't need to change the labels here since they're already correct
    # This is just for verification that all labels are in our expected set
    expected_labels = {
        'Timber and builders\' carpentry',
        'Marble products, granites',
        'Basic metals',
        'Plumbing, heating and drainage equipment and supplies',
        'Natural stone',
        'Door and window fittings',
        'Electrical equipment',
        'Glass products',
        'Cement, mortars and ready mixed concrete',
        'Paints and varnishes',
        'Floor and wall tiles and sanitary ware',
        'Artificial stone',
        'Elevators',
        'Insulating materials',
        'OVERALL INDEX',
        'Fuel for machinery (diesel), electricity, water'
    }
    
    # Verify all labels are in our expected set
    unmapped = [label for label in unique_labels if label not in expected_labels]
    if unmapped:
        print(f"Warning: Found unexpected labels after standardization: {unmapped}")
        print("These will need to be added to the series_mapping in add_series_codes function")
    
    # Log the standardization results
    print(f"Standardized series labels: {len(unique_labels)} unique labels")
    print(f"Labels: {sorted(unique_labels)}")
    
    return df_standardized

def convert_index_mode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert index_mode values based on frequency:
    - CHANGES -> MOR if freq is "M", ANR if freq is "A"
    - COST_INDICES -> CTX if freq is "M", AVX if freq is "A"
    """
    print("Converting index_mode values based on frequency...")
    
    # Create a copy to avoid modifying the original
    df_converted = df.copy()
    
    # Convert CHANGES based on frequency
    mask_changes = df_converted['index_mode'] == 'CHANGES'
    df_converted.loc[mask_changes & (df_converted['freq'] == 'M'), 'index_mode'] = 'MOR'
    df_converted.loc[mask_changes & (df_converted['freq'] == 'A'), 'index_mode'] = 'ANR'
    
    # Convert COST_INDICES based on frequency
    mask_cost_indices = df_converted['index_mode'] == 'COST_INDICES'
    df_converted.loc[mask_cost_indices & (df_converted['freq'] == 'M'), 'index_mode'] = 'CTX'
    df_converted.loc[mask_cost_indices & (df_converted['freq'] == 'A'), 'index_mode'] = 'AVX'
    
    # Log the conversion results
    conversion_counts = df_converted['index_mode'].value_counts()
    print(f"Index mode conversion completed:")
    print(f"  - MOR (Monthly Changes): {conversion_counts.get('MOR', 0)}")
    print(f"  - ANR (Annual Changes): {conversion_counts.get('ANR', 0)}")
    print(f"  - CTX (Monthly Cost Indices): {conversion_counts.get('CTX', 0)}")
    print(f"  - AVX (Annual Cost Indices): {conversion_counts.get('AVX', 0)}")
    
    return df_converted

def add_series_codes(df: pd.DataFrame) -> pd.DataFrame:
    """Add proper MCI series codes based on the standardized codelist."""
    # Create a mapping from series labels to proper MCI codes
    # This eliminates duplicates and uses consistent codes
    series_mapping = {
        'OVERALL INDEX': 'MCI01',
        'Timber and builders\' carpentry': 'MCI02',
        'Marble products, granites': 'MCI03',
        'Basic metals': 'MCI04',
        'Plumbing, heating and drainage equipment and supplies': 'MCI05',
        'Natural stone': 'MCI06',
        'Door and window fittings': 'MCI07',
        'Electrical equipment': 'MCI08',
        'Glass products': 'MCI09',
        'Cement, mortars and ready mixed concrete': 'MCI10',
        'Paints and varnishes': 'MCI11',
        'Floor and wall tiles and sanitary ware': 'MCI12',
        'Artificial stone': 'MCI13',
        'Elevators': 'MCI14',
        'Insulating materials': 'MCI15',
        'Fuel for machinery (diesel), electricity, water': 'MCI16'
    }
    
    # Add the series_code column
    df['series_code'] = df['series_label'].map(series_mapping)
    
    # Verify all series have codes
    unmapped_mask = df['series_code'].isna()
    if unmapped_mask.any():
        unmapped_series = df[unmapped_mask]['series_label'].unique()
        print(f"Warning: Found unmapped series labels: {unmapped_series}")
        print("This should not happen after standardization. Adding fallback codes...")
        
        # Force mapping to prevent errors
        for series in unmapped_series:
            if series not in series_mapping:
                print(f"Adding missing mapping for: {series}")
                # Find next available code
                next_code = f"MCI{len(series_mapping) + 1:02d}"
                series_mapping[series] = next_code
                print(f"Mapped {series} -> {next_code}")
        
        # Re-apply mapping
        df['series_code'] = df['series_label'].map(series_mapping)
    
    # Final verification - ensure all codes are assigned
    if df['series_code'].isna().any():
        print("CRITICAL ERROR: Some series still have no codes after mapping!")
        print("Unmapped series:", df[df['series_code'].isna()]['series_label'].unique())
    
    return df

# ---------- Main transformer ----------
def excel_to_tidy(path: Path) -> pd.DataFrame:
    dataset_id, vintage = extract_dataset_id_and_vintage(path.name)
    last_updated = datetime.fromtimestamp(path.stat().st_mtime)

    xls = pd.ExcelFile(path)
    all_rows = []

    for sheet in xls.sheet_names:
        try:
            # Skip non-data sheets
            if sheet.upper() in ['INFO', 'METADATA', 'NOTES', 'README']:
                continue
                
            raw = try_parse_with_multiheaders(xls, sheet)

            # Special handling for MCI files - do this BEFORE flattening columns
            if 'MATERIAL COST' in sheet or 'MCI' in path.name.upper():
                # For structure v2, get material names directly from Excel before processing
                material_names = None
                if 'MATERIAL COSTS' in sheet:  # This is structure v2
                    # Read the sheet again to get material names from row 11
                    raw_excel = pd.read_excel(path, sheet_name=sheet, header=None)
                    material_names = raw_excel.iloc[11].tolist()
                
                # Check which MCI structure this file has
                if any('JAN-' in str(cell) or 'FEB-' in str(cell) for cell in raw.iloc[:20, 0] if pd.notna(cell)):
                    raw = clean_mci_dataframe_v2(raw, material_names)
                else:
                    raw = clean_mci_dataframe(raw)
                
                if raw.empty:
                    continue
                
                # For MCI files, process each month column separately
                month_cols = [col for col in raw.columns if str(col).upper() in ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUNE', 'JULY', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']]
                
                # Check if this is structure v1 (has Month, Year, Value columns from clean_mci_dataframe)
                if 'Material_Group' in raw.columns and 'Month' in raw.columns and 'Year' in raw.columns:
                    # Structure v1: properly parsed with Material_Group, Month, Year, Value, Data_Type columns
                    month_map = {
                        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                        'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUG': '08',
                        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
                    }
                    
                    # Create time periods from Year and Month
                    time_periods = []
                    for _, row in raw.iterrows():
                        year = str(int(row['Year']))
                        month = str(row['Month']).upper()
                        if month in month_map:
                            time_periods.append(f"{year}-{month_map[month]}")
                        else:
                            time_periods.append(f"{year}-01")  # fallback
                    
                    # Create long format
                    long_df = pd.DataFrame({
                        'time_period': time_periods,
                        'freq': 'M',
                        'series_label': raw['Material_Group'],
                        'series_label_raw': raw['Material_Group'],
                        'value': pd.to_numeric(raw['Value'], errors='coerce'),
                        'unit': 'Index (2021=100)' if 'Data_Type' in raw.columns and raw['Data_Type'].iloc[0] == 'COST_INDICES' else 'Percentage Change',
                        'adjustment': None,
                        'index_mode': raw['Data_Type'] if 'Data_Type' in raw.columns else 'UNKNOWN'
                    })
                    
                    # Add series_id with data type differentiation
                    if 'Data_Type' in raw.columns:
                        # Differentiate series by data type to avoid conflicts
                        series_labels_with_type = []
                        for _, row in raw.iterrows():
                            data_type = row.get('Data_Type', 'UNKNOWN')
                            material_group = row['Material_Group']
                            if data_type == 'CHANGES':
                                series_labels_with_type.append(f"{material_group} (Change)")
                            else:
                                series_labels_with_type.append(material_group)
                        
                        long_df['series_label'] = series_labels_with_type
                        long_df['series_label_raw'] = series_labels_with_type
                    
                    # Add series_id
                    long_df['series_id'] = long_df['series_label'].map(series_id_from_label)
                    
                    # Lineage
                    long_df['dataset_id'] = dataset_id
                    long_df['vintage'] = vintage
                    long_df['sheet'] = sheet
                    long_df['source_file'] = path.name
                    long_df['last_updated'] = last_updated
                    
                    all_rows.append(long_df)
                    continue  # Skip the regular processing for structure v1
                else:
                    # Structure v2: time periods in first column
                    # Process each material group column
                    for col in raw.columns[1:]:  # Skip time_period column
                        # Handle MultiIndex columns by flattening the name
                        col_name = str(col) if not isinstance(col, tuple) else ' | '.join(str(c) for c in col if pd.notna(c))
                        
                        material_df = raw[['time_period', col]].copy()
                        material_df = material_df.dropna(subset=[col])
                        
                        # Convert time period format (e.g., 'JAN-00' to '2000-01', 'ANNUAL AVERAGE-2000' to '2000')
                        time_periods = []
                        freqs = []
                        for tp in material_df['time_period']:
                            if pd.notna(tp):
                                tp_str = str(tp).strip()
                                
                                # Handle ANNUAL AVERAGE entries
                                if 'ANNUAL AVERAGE' in tp_str.upper():
                                    year_match = re.search(r'(\d{4})', tp_str)
                                    if year_match:
                                        time_periods.append(year_match.group(1))
                                        freqs.append('A')  # Annual frequency
                                    else:
                                        time_periods.append(tp_str)
                                        freqs.append('M')
                                    continue
                                
                                # Handle monthly formats like 'JAN-00', 'FEB-00', etc.
                                month_map = {
                                    'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                                    'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUG': '08',
                                    'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
                                }
                                
                                if '-' in tp_str:
                                    # Handle double dashes by cleaning them first
                                    tp_str = tp_str.replace('--', '-')
                                    
                                    month_name = tp_str.split('-')[0].upper()
                                    year_part = tp_str.split('-')[1]
                                    
                                    if month_name in month_map:
                                        # This is a monthly entry like 'JAN-00'
                                        if len(year_part) == 2:
                                            year = "20" + year_part
                                        else:
                                            year = year_part
                                        result = f"{year}-{month_map[month_name]}"
                                        time_periods.append(result)
                                        freqs.append('M')  # Monthly frequency
                                    else:
                                        # Unknown format, keep as is
                                        time_periods.append(tp_str)
                                        freqs.append('M')
                                else:
                                    # Unknown format, keep as is
                                    time_periods.append(tp_str)
                                    freqs.append('M')
                            else:
                                time_periods.append(None)
                                freqs.append(None)
                        
                        # Create long format
                        long_df = pd.DataFrame({
                            'time_period': time_periods,
                            'freq': freqs,
                            'series_label': col_name,
                            'series_label_raw': col_name,
                            'value': pd.to_numeric(material_df[col], errors='coerce'),
                            'unit': 'Index (2021=100)',
                            'adjustment': None,
                            'index_mode': 'COST_INDICES'  # Structure v2 is always cost indices
                        })
                        
                        # Add series_id
                        long_df['series_id'] = long_df['series_label'].map(series_id_from_label)
                        
                        # Lineage
                        long_df['dataset_id'] = dataset_id
                        long_df['vintage'] = vintage
                        long_df['sheet'] = sheet
                        long_df['source_file'] = path.name
                        long_df['last_updated'] = last_updated
                        
                        all_rows.append(long_df)
                
                continue  # Skip the regular processing for MCI files

            # Regular processing for non-MCI files
            raw = flatten_columns(raw)
            
            # Drop fully empty columns
            raw = raw.dropna(axis=1, how="all")
            if raw.empty or raw.shape[1] < 2:
                continue

            time_col = find_time_column(raw)
            if time_col not in raw.columns:
                # Not a data sheet
                continue

            df = raw.copy()
            # Clean time
            df = df[~df[time_col].isna()]
            time_period, freq = normalize_period_and_freq(df[time_col])
            df.insert(0, "time_period", time_period)
            df.insert(1, "freq", freq)

            # Keep only time + numeric/value columns
            value_cols = [c for c in df.columns if c not in {time_col, "time_period", "freq"}]

            # Melt
            long_df = df.melt(
                id_vars=["time_period", "freq"],
                value_vars=value_cols,
                var_name="series_label",
                value_name="value",
            )

            # Drop rows without time or without any value
            long_df = long_df.dropna(subset=["time_period"])
            # Convert to numeric when possible
            long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")

            # Parse series metadata from label if present
            # Expect patterns like "Indicator | Unit | Adj"
            parts = long_df["series_label"].str.split(r"\s*\|\s*", expand=True)
            # Assign safely
            col_map = {}
            if parts.shape[1] >= 1:
                col_map["series_label"] = parts[0]
            if parts.shape[1] >= 2:
                col_map["unit"] = parts[1]
            if parts.shape[1] >= 3:
                col_map["adjustment"] = parts[2]
            # Create new cols while keeping original series_label_raw
            long_df = long_df.rename(columns={"series_label": "series_label_raw"})
            for newc, ser in col_map.items():
                long_df[newc] = ser

            # Add index_mode for non-MCI files
            long_df["index_mode"] = "UNKNOWN"

            # Add series_id
            long_df["series_id"] = long_df["series_label"].fillna(long_df["series_label_raw"]).map(series_id_from_label)

            # Lineage
            long_df["dataset_id"] = dataset_id
            long_df["vintage"] = vintage
            long_df["sheet"] = sheet
            long_df["source_file"] = path.name
            long_df["last_updated"] = last_updated

            all_rows.append(long_df)
        except Exception as e:
            print(f"[WARN] Failed to process sheet '{sheet}' in {path.name}: {e}")
            continue

    if not all_rows:
        return pd.DataFrame()

    out = pd.concat(all_rows, ignore_index=True)

    # Clean and fix time periods
    out = clean_time_periods(out)
    
    # Standardize series labels to eliminate duplicates
    out = standardize_series_labels(out)
    
    # Add series codes (MCI01, MCI02, MCI03, etc.)
    out = add_series_codes(out)
    
    # Convert index_mode values based on frequency
    out = convert_index_mode(out)
    
    # Remove duplicates based on time_period, series_label, and index_mode
    # This handles cases where the same data appears in multiple source files
    # but preserves different data types (COST_INDICES vs CHANGES)
    out = out.drop_duplicates(subset=['time_period', 'series_label', 'index_mode'], keep='first')
    
    print(f"After removing duplicates: {len(out)} rows")
    
    # Final duplicate removal: if we have duplicates in all 4 columns (time_period, series_label, index_mode, source_file)
    # then drop them and keep the first occurrence
    initial_rows = len(out)
    out = out.drop_duplicates(subset=['time_period', 'series_label', 'index_mode', 'source_file'], keep='first')
    final_rows = len(out)
    
    if initial_rows != final_rows:
        print(f"Final duplicate removal: {initial_rows} -> {final_rows} rows (removed {initial_rows - final_rows} duplicates)")
    else:
        print(f"No final duplicates found: {final_rows} rows")

    # Column order
    cols = [
        "dataset_id", "vintage", "sheet",
        "time_period", "freq",
        "series_id", "series_code", "series_label", "series_label_raw",
        "unit", "adjustment", "index_mode",
        "value",
        "source_file", "last_updated",
    ]
    for c in cols:
        if c not in out.columns:
            out[c] = pd.NA
    out = out[cols]
    
    # Optional: drop rows with all-null values
    out = out.dropna(subset=["value"], how="all")
    return out

def main():
    # Check if input directory exists
    # Search for Excel files in the MCI folder, as in other strategies
    if not INPUT_DIR.exists():
        print(f"Error: Input directory '{INPUT_DIR}' does not exist!")
        print(f"Current working directory: {os.getcwd()}")
        return
    # Look for Excel files in MCI folder - updated pattern to match your files
    files = sorted(list(INPUT_DIR.glob("*.xlsx")))
    
    if not files:
        print(f"No Excel files found in {INPUT_DIR}")
        print(f"Available files: {list(INPUT_DIR.glob('*'))}")
        return
    
    print(f"Found {len(files)} Excel files:")
    for f in files:
        print(f"  - {f.name}")
    
    frames = []
    for f in files:
        try:
            print(f"Processing {f.name}...")
            tidy = excel_to_tidy(f)
            if not tidy.empty:
                frames.append(tidy)
                print(f"  ✓ Extracted {len(tidy)} rows")
            else:
                print(f"  ⚠ No data extracted")
        except Exception as e:
            print(f"[ERROR] Failed on {f.name}: {e}")

    if not frames:
        print("No data extracted from any files.")
        return

    unified = pd.concat(frames, ignore_index=True)

    # Drop the specified columns as requested
    columns_to_drop = [
        "dataset_id", "vintage", "sheet", "series_id", 
        "series_label", "series_label_raw", "unit", "adjustment",
        "source_file", "last_updated"
    ]
    
    # Only drop columns that exist
    existing_columns_to_drop = [col for col in columns_to_drop if col in unified.columns]
    if existing_columns_to_drop:
        print(f"Dropping columns from final output: {existing_columns_to_drop}")
        unified = unified.drop(columns=existing_columns_to_drop)
    
    print(f"Final columns: {unified.columns.tolist()}")
    print(f"Final shape: {unified.shape}")

    # Persist (Excel only, do not save parquet)
    try:
        # Excel for hand-off
        with pd.ExcelWriter(OUTPUT_EXCEL, engine="xlsxwriter") as writer:
            unified.to_excel(writer, index=False, sheet_name="unified")
        print(f"✓ Saved: {OUTPUT_EXCEL}")
    except Exception as e:
        print(f"⚠ Failed to save Excel: {e}")

    print(f"\nSummary:")
    print(f"Total rows: {len(unified):,}")
    print(f"Unique series codes: {unified['series_code'].nunique()}")
    print(f"Date range: {unified['time_period'].min()} to {unified['time_period'].max()}")
    print(f"Index mode distribution:")
    print(unified['index_mode'].value_counts())

if __name__ == "__main__":
    main()
