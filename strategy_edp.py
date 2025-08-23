from loguru import logger
import pandas as pd
import os

def main():
    file = "assets/EDP/A0701_SEL03_TB_AN_00_2025_06_P_EN.xlsx"

    logger.info(f"Loading Excel file: {file}")
    try:
        sheets = pd.ExcelFile(file).sheet_names
        logger.success(f"Found sheets: {sheets}")
    except Exception as e:
        logger.error(f"Failed to read Excel file or list sheets: {e}")
        return

    def load_and_clean_table(file, sheet_name, col_indices, col_names, code_prefix="A.N"):
        logger.info(f"Loading and cleaning table: {sheet_name}")
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            logger.debug(f"Loaded {len(df)} rows from {sheet_name}")
            df = df.iloc[:, col_indices]
            df.columns = col_names
            logger.debug(f"Selected columns: {col_names}")

            df = df[df["Code"].fillna("").str.startswith(code_prefix)]
            logger.debug(f"Filtered rows with Code starting with '{code_prefix}': {len(df)} rows remain")

            for year in col_names[1:]:
                before = len(df)
                df = df[pd.to_numeric(df[year], errors='coerce').notnull()]
                after = len(df)
                logger.debug(f"Filtered non-numeric values in column '{year}': {before} -> {after}")

            logger.success(f"Cleaned table '{sheet_name}': {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error processing table '{sheet_name}': {e}")
            return pd.DataFrame(columns=col_names)

    def custom_reorder(code):
        parts = code.split(".")
        # Step 1: Remove index 11
        if len(parts) > 11:
            del parts[11]
        # Step 2: Move index -3 to -2
        if len(parts) >= 3:
            token = parts.pop(-3)
            parts.insert(-2, token)
        # Step 3: Move new index 11 to index -3
        if len(parts) > 11:
            token = parts.pop(11)
            parts.insert(-3, token)
        # Step 4: Move new index 11 to index -4
        if len(parts) > 11:
            token = parts.pop(11)
            parts.insert(-4, token)
        token = parts.pop(-2)
        parts.insert(-4, token)
        # swap index -4 with index -5
        if len(parts) > 5:
            parts[-4], parts[-5] = parts[-5], parts[-4]
        return ".".join(parts)

    # Define column indices and names
    columns_indices_table1 = [1, 4, 5, 6, 7]
    columns_indices_table2 = [1, 3, 4, 5, 6]
    columns_indices_table3 = [1, 3, 4, 5, 6]
    columns_indices_table4 = [1, 5, 6, 7, 8]
    column_names = ["Code", "2021", "2022", "2023", "2024"]

    logger.info("Loading and cleaning all required tables...")
    table1 = load_and_clean_table(file, "Table 1", columns_indices_table1, column_names)
    table2a = load_and_clean_table(file, "Table 2A", columns_indices_table2, column_names)
    table2c = load_and_clean_table(file, "Table 2C", columns_indices_table2, column_names)
    table2d = load_and_clean_table(file, "Table 2D", columns_indices_table2, column_names)
    table3a = load_and_clean_table(file, "Table 3A", columns_indices_table3, column_names)
    table3b = load_and_clean_table(file, "Table 3B", columns_indices_table3, column_names)
    table3d = load_and_clean_table(file, "Table 3D", columns_indices_table3, column_names)
    table3e = load_and_clean_table(file, "Table 3E", columns_indices_table3, column_names)
    table4 = load_and_clean_table(file, "Table 4", columns_indices_table4, column_names)

    logger.info("Table lengths:")
    logger.info(f"Table 1: {len(table1)}")
    logger.info(f"Table 2A: {len(table2a)}")
    logger.info(f"Table 2C: {len(table2c)}")
    logger.info(f"Table 2D: {len(table2d)}")
    logger.info(f"Table 3A: {len(table3a)}")
    logger.info(f"Table 3B: {len(table3b)}")
    logger.info(f"Table 3D: {len(table3d)}")
    logger.info(f"Table 3E: {len(table3e)}")
    logger.info(f"Table 4: {len(table4)}")
    total_length = (
        len(table1) + len(table2a) + len(table2c) + len(table2d) +
        len(table3a) + len(table3b) + len(table3d) + len(table3e) + len(table4)
    )
    logger.success(f"Total rows in all tables: {total_length}")

    logger.info("Merging all tables into a single DataFrame...")
    merged_table = pd.concat(
        [table1, table2a, table2c, table2d, table3a, table3b, table3d, table3e, table4],
        ignore_index=True
    )
    logger.success(f"Merged table shape: {merged_table.shape}")

    logger.info("Processing 'Edp' sheet for merging...")
    try:
        df = pd.read_excel(file, sheet_name="Edp")
        logger.debug(f"Loaded 'Edp' sheet with {df.shape[0]} rows and {df.shape[1]} columns")
        df = df.iloc[31:]
        logger.debug(f"Trimmed to rows from 32 onwards: {df.shape}")
        df = df.iloc[:, :-5]
        logger.debug(f"Dropped last 5 columns: {df.shape}")
        df = df[[df.columns[-1]] + list(df.columns[:-1])]
        logger.debug(f"Moved last column to front: {df.columns.tolist()}")
        df = df.iloc[:, :-5]
        logger.debug(f"Dropped last 4 columns: {df.shape}")
        df.columns = df.iloc[0]
        df = df[1:]
        df.reset_index(drop=True, inplace=True)
        # join all columns with dot excpet first column
        df['SDMX series'] = df.iloc[:, 1:].apply(lambda x: '.'.join(x.dropna().astype(str)), axis=1)
        # drop all columns excpet first and last
        logger.success(f"Processed 'Edp' DataFrame: {df.shape}")
    except Exception as e:
        logger.error(f"Failed to process 'Edp' sheet: {e}")
        return

    logger.info(f"First cell of processed 'Edp' DataFrame: {df.iloc[0, 0]}")

    logger.info("Applying custom code reordering to merged table...")
    merged_table["Code_adjusted"] = merged_table.iloc[:, 0].apply(custom_reorder)
    logger.success("Custom code reordering applied.")

    logger.info("Checking which codes in merged_table are not present in 'Edp' DataFrame...")
    not_in_df = merged_table[~merged_table["Code_adjusted"].isin(df.iloc[:, 0])]
    logger.info(f"Codes in merged_table not in df: {len(not_in_df)}")
    if len(not_in_df) > 0:
        logger.warning("Codes not in df:")
        logger.warning(not_in_df["Code_adjusted"].unique())
    else:
        logger.success("All codes in merged_table are present in 'Edp' DataFrame.")

    logger.info("Merging merged_table with 'Edp' DataFrame on adjusted code...")
    merged_df = pd.merge(
        merged_table,
        df,
        left_on="Code_adjusted",
        right_on=df.columns[0],
        how="left",
        suffixes=('', '_edp')
    )
    logger.success(f"Merged DataFrame shape: {merged_df.shape}")

    logger.info("Dropping unnecessary columns from merged DataFrame...")
    try:
        merged_df = merged_df.drop(columns=[merged_df.columns[0], merged_df.columns[5], merged_df.columns[6]])
        logger.success(f"Columns dropped. New shape: {merged_df.shape}")
    except Exception as e:
        logger.error(f"Error dropping columns: {e}")

    logger.info("Setting 'REF_AREA' column to 'EL' for all rows...")
    merged_df["REF_AREA"] = "EL"

    output_dir = "assets/prepared"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "EDP.xlsx")
    logger.info(f"Saving merged DataFrame to {output_file}...")
    try:
        merged_df.to_excel(output_file, index=False)
        logger.success(f"File saved: {output_file}")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")

if __name__ == "__main__":
    main()