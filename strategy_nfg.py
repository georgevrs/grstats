from loguru import logger
import pandas as pd
import os

def load_excel_sheets(file_path):
    logger.info(f"Loading Excel file: {file_path}")
    try:
        sheet_names = pd.ExcelFile(file_path).sheet_names
        logger.success(f"Found sheets: {sheet_names}")
        dfs = {sheet: pd.read_excel(file_path, sheet_name=sheet) for sheet in sheet_names}
        dfs_renamed = {f"sheet{i+1}": df for i, (sheet, df) in enumerate(dfs.items())}
        return dfs_renamed
    except Exception as e:
        logger.error(f"Failed to load Excel sheets: {e}")
        return None

def clean_df1(df1):
    logger.info("Cleaning first sheet (df1)...")
    try:
        df1 = df1.iloc[1:]
        df1.columns = df1.iloc[1]
        
        account_entry_row = []

        for idx, col in enumerate(df1.columns):
            # use index rather than column name to identify first column
            if idx == 0:
                account_entry_row.append("ACCOUNT_ENTRY")
            else:
                # access by integer location (column index) instead of name
                val = str(df1.iloc[0, idx]).lower()

                if "receivable" in val:
                    account_entry_row.append("C")
                    
                elif "payable" in val:
                    account_entry_row.append("D")
                else:
                    account_entry_row.append("_Z")
        # remove last value from list
        account_entry_row.pop()
        account_entry_row[0] = "ACCOUNT_ENTRY"

        df1 = df1[2:]
        df1.rename(columns={df1.columns[0]: "Date"}, inplace=True)
        df1 = df1.iloc[1:]
        df1["Date"] = df1["Date"].str.replace("*", "", regex=False)
        df1 = df1[df1["Date"].str.match(r"^\d{4}-Q[1-4]$")]
        df1.reset_index(drop=True, inplace=True)
        df1.columns = df1.columns.str.strip()
        # Insert row with all values as "_Z"
        df1.loc[-1] = ["_Z"] * len(df1.columns)
        df1.index = df1.index + 1
        df1 = df1.sort_index()
        df1.iloc[0, 0] = "INSTR_ASSET"
        # Insert row with column names
        columns = df1.columns.tolist()
        df1.loc[-1] = columns
        df1.index = df1.index + 1
        df1 = df1.sort_index()
        df1.iloc[0, 0] = "NA_ITEM"
        logger.success("df1 cleaned successfully.")
        #drop column D995
        df1 = df1.drop(columns=["D995"])
        # Create a one-row DataFrame for insertion
        row_df = pd.DataFrame([account_entry_row], columns=df1.columns)
        # add row at the end
        df1 = pd.concat([df1, row_df], ignore_index=True)

        
        print("DF1 FINAL\n",df1.head())
        return df1
    except Exception as e:
        logger.error(f"Error cleaning df1: {e}")
        return pd.DataFrame()

def clean_df2(df2):
    logger.info("Cleaning second sheet (df2)...")
    try:
        df2 = df2.iloc[1:]
        account_entry_row = []

        for idx, col in enumerate(df2.columns):
            # use index rather than column name to identify first column
            if idx == 0:
                account_entry_row.append("ACCOUNT_ENTRY")
            else:
                val = str(df2.iloc[0, idx]).lower()
                if "receivable" in val:
                    account_entry_row.append("C")
                elif "payable" in val:
                    account_entry_row.append("D")
                else:
                    account_entry_row.append("_Z")
        account_entry_row[0] = "ACCOUNT_ENTRY"
        df2.columns = df2.iloc[0].str.split("\n").str[0]
        df2 = df2[1:]
        df2 = df2.drop(df2.index[1])
        df2.iloc[0, 0] = "INSTR_ASSET"
        df2.loc[-1] = ["_Z"] * len(df2.columns)
        df2.index = df2.index + 1
        df2 = df2.sort_index()
        df2.iloc[0, 0] = "NA_ITEM"
        df2.columns = df2.columns.str.strip()
        df2.rename(columns={"Quarter": "Date"}, inplace=True)
        df2["Date"] = df2["Date"].str.replace("*", "", regex=False)
        pattern = r'^\d{4}-Q[1-4]$'
        # Keep first two rows unchanged, then filter the rest
        df2 = pd.concat([
            df2.iloc[:2],
            df2.iloc[2:][df2.iloc[2:]['Date'].str.match(pattern, na=False)]
        ]).reset_index(drop=True)
        df2.reset_index(drop=True, inplace=True)
        logger.success("df2 cleaned successfully.")
        row_df = pd.DataFrame([account_entry_row], columns=df2.columns)
        # add row at the end
        df2 = pd.concat([df2, row_df], ignore_index=True)

        

        print("DF2 FINAL\n",df2.head())
        return df2
    except Exception as e:
        logger.error(f"Error cleaning df2: {e}")
        return pd.DataFrame()

def merge_and_finalize(df1, df2):
    logger.info("Merging cleaned DataFrames...")
    try:
        merged_df = pd.merge(df1, df2, on="Date", how='outer', suffixes=('_df1', '_df2'))
        
        # Move the last 2 rows to the beginning
        last_two_rows = merged_df.tail(3)
        merged_df = merged_df.iloc[:-3]  # Remove last 2 rows
        merged_df = pd.concat([last_two_rows, merged_df], ignore_index=True)
        
        # Delete the last row
        merged_df = merged_df.iloc[:-1]
        
        merged_df.loc[-1] = ["_Z"] * len(merged_df.columns)
        merged_df.index = merged_df.index + 1
        merged_df = merged_df.sort_index()
        merged_df.iloc[0, 0] = "MATURITY"
        # Set S/L for specific columns if present
        col_map = {
            "AF.31 Short-term debt securities": "S",
            "AF.32 Long-term debt securities": "L",
            "AF.41 Short-term loans": "S",
            "AF.42 Long-term loans": "L"
        }
        for col, val in col_map.items():
            if col in merged_df.columns:
                merged_df.iloc[0, merged_df.columns.get_loc(col)] = val
        merged_df.insert(1, "FREQ", "Q")
        logger.success("Merged DataFrame finalized.")
        return merged_df
    except Exception as e:
        logger.error(f"Error merging DataFrames: {e}")
        return pd.DataFrame()

def main():
    import glob
    nfg_files = glob.glob("assets/NFG/*_BI.xlsx")
    if not nfg_files:
        logger.error("No files found matching pattern assets/NFG/*_BI.xlsx")
        return
    input_file = nfg_files[0]
    logger.info(f"Using input file: {input_file}")
    output_dir = "assets/prepared"
    output_file = os.path.join(output_dir, "NFG.xlsx")
    os.makedirs(output_dir, exist_ok=True)

    dfs_renamed = load_excel_sheets(input_file)
    if dfs_renamed is None or "sheet1" not in dfs_renamed or "sheet2" not in dfs_renamed:
        logger.error("Required sheets not found. Exiting.")
        return
    df1 = clean_df1(dfs_renamed["sheet1"])
    df2 = clean_df2(dfs_renamed["sheet2"])
    if df1.empty or df2.empty:
        logger.error("One of the cleaned DataFrames is empty. Exiting.")
        return
    merged_df = merge_and_finalize(df1, df2)
    if merged_df.empty:
        logger.error("Merged DataFrame is empty. Exiting.")
        return
    try:
        merged_df.to_excel(output_file, index=False)
        logger.success(f"Saved merged DataFrame to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save merged DataFrame: {e}")

if __name__ == "__main__":
    main()
