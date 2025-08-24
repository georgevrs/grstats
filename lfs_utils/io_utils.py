from pathlib import Path
import pandas as pd

def read_excel(path: Path) -> pd.DataFrame:
    return pd.read_excel(path)
