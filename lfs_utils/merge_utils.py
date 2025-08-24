# merge_utils.py
from typing import List, Set
import pandas as pd

def common_columns(*dfs: pd.DataFrame) -> Set[str]:
    common = set(dfs[0].columns)
    for d in dfs[1:]:
        common &= set(d.columns)
    return common

def outer_merge_on_common(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate DataFrames row-wise on their common columns.
    Keeps only the intersection of columns to ensure consistency.
    """
    if not dfs:
        raise ValueError("No dataframes provided")

    cols = list(common_columns(*dfs))
    aligned = [df[cols] for df in dfs]
    return pd.concat(aligned, ignore_index=True)
