"""Summary statistics and anomaly detection (IQR method)."""
import pandas as pd


def summarize(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include="number")
    stats = {
        col: {
            "mean": round(float(numeric[col].mean()), 3),
            "min": float(numeric[col].min()),
            "max": float(numeric[col].max()),
            "std": round(float(numeric[col].std() or 0), 3),
        }
        for col in numeric.columns
    }
    return {"rows": len(df), "columns": list(df.columns), "numeric_stats": stats}


def find_anomalies(df: pd.DataFrame, k: float = 1.5) -> dict:
    """Flag values outside [Q1 - k*IQR, Q3 + k*IQR] in each numeric column."""
    result = {}
    for col in df.select_dtypes(include="number").columns:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            continue
        mask = (df[col] < q1 - k * iqr) | (df[col] > q3 + k * iqr)
        if mask.any():
            result[col] = {
                "count": int(mask.sum()),
                "rows": [int(i) for i in df.index[mask][:10]],
                "values": [float(v) for v in df.loc[mask, col].head(5)],
            }
    return result
