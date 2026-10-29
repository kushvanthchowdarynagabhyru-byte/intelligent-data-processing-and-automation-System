"""Load a file and detect what kind of dataset it is."""
from pathlib import Path

import pandas as pd

# keyword sets used to guess the dataset category
CATEGORIES = {
    "sales": {"price", "quantity", "order", "revenue", "total", "product", "customer"},
    "sensor": {"temperature", "humidity", "pressure", "sensor", "voltage", "device", "reading"},
    "finance": {"amount", "balance", "account", "transaction", "debit", "credit", "invoice"},
    "hr": {"employee", "salary", "department", "hire", "designation"},
}


def load_file(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".json":
        return pd.read_json(path)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {ext}")


def detect_category(df: pd.DataFrame) -> str:
    """Score each category by how many keywords appear in column names."""
    words = set()
    for col in df.columns:
        words.update(str(col).lower().replace("-", "_").replace(" ", "_").split("_"))
    scores = {name: len(words & kws) for name, kws in CATEGORIES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"
