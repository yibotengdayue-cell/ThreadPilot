import pandas as pd
from pathlib import Path

def summarize_csv(csv_path: str) -> dict:
    p = Path(csv_path)
    df = pd.read_csv(p)
    desc = df.describe(include="all").to_dict()
    return {
        "file": p.name,
        "rows": len(df),
        "cols": len(df.columns),
        "describe": desc
    }
