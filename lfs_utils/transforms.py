from typing import Iterable, Set, Dict, Tuple, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def standardize_columns(df: pd.DataFrame, rename_map: Dict) -> pd.DataFrame:
    """
    Rename columns by position → name using a map where keys can be ints (pos) or old names.
    """
    # If keys are ints, map current positional index to name
    if all(isinstance(k, int) for k in rename_map.keys()):
        new_cols = list(df.columns)
        for pos, new_name in rename_map.items():
            if pos < len(new_cols):
                new_cols[pos] = new_name
        df.columns = new_cols
        return df
    else:
        return df.rename(columns=rename_map)

def drop_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[:, ~df.columns.duplicated()]

def drop_duplicate_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    before = df.shape[0]
    out = df.drop_duplicates()
    return out, before - out.shape[0]

def fill_na(df: pd.DataFrame, fill_value: str = "_Z") -> pd.DataFrame:
    return df.fillna(fill_value)

def clean_dataframe(
    df: pd.DataFrame,
    col_to_check: str = "Value",
    invalid_value: str = "_Z"
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    1) drop duplicate cols  2) drop duplicate rows  3) drop invalid rows by col_to_check
    Returns df and stats.
    """
    stats = {"dropped_dupe_rows": 0, "dropped_invalid_rows": 0}

    df = drop_duplicate_columns(df)
    df, dropped = drop_duplicate_rows(df)
    stats["dropped_dupe_rows"] = dropped

    before = df.shape[0]
    df = df[df[col_to_check] != invalid_value]
    stats["dropped_invalid_rows"] = before - df.shape[0]

    logger.info("Cleaned: dropped dupes=%d, invalid=%d", dropped, stats["dropped_invalid_rows"])
    return df, stats
