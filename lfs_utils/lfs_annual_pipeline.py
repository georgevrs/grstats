from typing import Dict, Tuple
import logging
import pandas as pd

from .config import Paths, RENAME_MAPS
from .io_utils import read_excel
from .transforms import standardize_columns, fill_na, clean_dataframe
from .merge_utils import outer_merge_on_common, common_columns

logger = logging.getLogger(__name__)

INVALID = "_Z"

def load_raw(paths: Paths) -> Dict[str, pd.DataFrame]:
    keys = list(paths.inputs.keys())
    return {k: read_excel(paths.file(k)) for k in keys}

def rename_if_needed(df: pd.DataFrame, key: str) -> pd.DataFrame:
    m = RENAME_MAPS.get(key)
    return standardize_columns(df, m) if m else df

def build_educ(d: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict]:
    dfs = [d["lfs_educ_regio"], d["lfs_educ_sexage"], d["lfs_educ_status"]]
    merged = outer_merge_on_common(dfs)
    merged = fill_na(merged, INVALID)
    cleaned, stats = clean_dataframe(merged, col_to_check="Value", invalid_value=INVALID)
    return cleaned, stats

def build_emp(d: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict]:
    merged = outer_merge_on_common([d["lfs_emp_regio"], d["lfs_emp_sexage"]])
    merged = fill_na(merged, INVALID)
    cleaned, stats = clean_dataframe(merged, col_to_check="Value", invalid_value=INVALID)

    # Final, explicit column order for EMP (matches your list)
    emp_names = [
        'Year','Region','TOT_EMP','UNDERMP_PT_WORK','UNDERMP_PT_WORK_SUB','WORK_FOR_MORE_HOURS',
        'LOOKING_FOR_ANOTHER_JOB','HAVE_MORE_THAN_ONE_JOB_OR_BUSINESS','WORK_WITHOUT_SSN',
        'Education_Level_Main','Education_Level_Sub','Unit_of_Measure','Value','Sex','Age_Group'
    ]
    # Only rename if counts match to avoid silent misalignments
    if len(cleaned.columns) == len(emp_names):
        cleaned.columns = emp_names
    else:
        logger.warning("EMP column count mismatch: got %d expected %d", len(cleaned.columns), len(emp_names))
    return cleaned, stats

def build_job(d: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict]:
    # Standardize columns first (pos→name)
    job_regio = rename_if_needed(d["lfs_job_regio"], "lfs_job_regio")
    job_sexage = rename_if_needed(d["lfs_job_sexage"], "lfs_job_sexage")
    job_occup = rename_if_needed(d["lfs_job_occup"], "lfs_job_occup")

    merged12 = outer_merge_on_common([job_regio, job_sexage])
    merged_all = outer_merge_on_common([merged12, job_occup])
    merged_all = fill_na(merged_all, INVALID)

    cleaned, stats = clean_dataframe(merged_all, col_to_check="Value", invalid_value=INVALID)
    return cleaned, stats

def build_demo(d: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict]:
    occup = rename_if_needed(d["lfs_occup_demo"], "lfs_occup_demo")
    sector = rename_if_needed(d["lfs_sector_demo"], "lfs_sector_demo")
    merged = outer_merge_on_common([occup, sector])
    merged = fill_na(merged, INVALID)
    cleaned, stats = clean_dataframe(merged, col_to_check="Value", invalid_value=INVALID)
    return cleaned, stats

def build_popul(d: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict]:
    merged = outer_merge_on_common([d["lfs_popul_regio"], d["lfs_popul_status"]])
    merged = fill_na(merged, INVALID)
    cleaned, stats = clean_dataframe(merged, col_to_check="Value", invalid_value=INVALID)
    return cleaned, stats

def build_status(d: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict]:
    merged = outer_merge_on_common([d["lfs_status_regio"], d["lfs_status_sexage"]])
    merged = fill_na(merged, INVALID)
    cleaned, stats = clean_dataframe(merged, col_to_check="Value", invalid_value=INVALID)
    return cleaned, stats

def run() -> Dict[str, Tuple[pd.DataFrame, Dict]]:
    """
    Executes all flows and returns dict of {'educ': (df, stats), ...}
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    paths = Paths()
    raw = load_raw(paths)

    # Pre-rename where needed (for flows that rely on names later)
    for k in ["lfs_job_regio", "lfs_job_sexage", "lfs_job_occup", "lfs_occup_demo", "lfs_sector_demo"]:
        raw[k] = rename_if_needed(raw[k], k)

    out = {
        "educ":   build_educ(raw),
        "emp":    build_emp(raw),
        "job":    build_job(raw),
        "demo":   build_demo(raw),
        "popul":  build_popul(raw),
        "status": build_status(raw),
    }

    for name, (_, stats) in out.items():
        logging.info("Flow %-7s → dropped dupes=%d, invalid=%d",
                     name, stats["dropped_dupe_rows"], stats["dropped_invalid_rows"])
    return out
