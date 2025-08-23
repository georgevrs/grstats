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
        df1 = df1.iloc[2:]
        df1.columns = df1.iloc[0]
        df1 = df1[1:]
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
        return df1
    except Exception as e:
        logger.error(f"Error cleaning df1: {e}")
        return pd.DataFrame()

def clean_df2(df2):
    logger.info("Cleaning second sheet (df2)...")
    try:
        df2 = df2.iloc[1:]
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
        return df2
    except Exception as e:
        logger.error(f"Error cleaning df2: {e}")
        return pd.DataFrame()

def merge_and_finalize(df1, df2):
    logger.info("Merging cleaned DataFrames...")
    try:
        merged_df = pd.merge(df1, df2, on="Date", how='outer', suffixes=('_df1', '_df2'))
        
        # Move the last 2 rows to the beginning
        last_two_rows = merged_df.tail(2)
        merged_df = merged_df.iloc[:-2]  # Remove last 2 rows
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
    input_file = "assets/NFG/A0701_SEL05_TS_QQ_01_1999_01_2025_01E_F_BI.xlsx"
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
