"""Automatic cleaning: no configuration needed."""
import re
import warnings

import pandas as pd


def _snake(name: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "_", str(name).strip()).strip("_").lower()


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    log: list[str] = []

    df.columns = [_snake(c) for c in df.columns]

    n = len(df)
    df = df.drop_duplicates()
    if len(df) < n:
        log.append(f"removed {n - len(df)} duplicate rows")

    empty = [c for c in df.columns if df[c].isna().mean() > 0.6]
    if empty:
        df = df.drop(columns=empty)
        log.append(f"dropped mostly-empty columns: {empty}")

    for col in df.columns:
        s = df[col]
        if s.dtype == object or str(s.dtype) == "string":
            s = s.astype("string").str.strip()
            numeric = pd.to_numeric(s.str.replace(r"[$,₹€\s%]", "", regex=True), errors="coerce")
            if s.notna().any() and numeric.notna().sum() / s.notna().sum() >= 0.8:
                df[col] = numeric
                log.append(f"converted '{col}' to numeric")
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dates = pd.to_datetime(s, errors="coerce")
            if s.notna().any() and dates.notna().sum() / s.notna().sum() >= 0.8 \
                    and s.str.contains(r"[-/]", na=False).mean() > 0.8:
                df[col] = dates
                log.append(f"converted '{col}' to datetime")
                continue
            df[col] = s

    # fill remaining missing values
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if not missing:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
            log.append(f"filled {missing} missing in '{col}' with median")
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
        else:
            df[col] = df[col].fillna("unknown")
            log.append(f"filled {missing} missing in '{col}' with 'unknown'")

    return df.reset_index(drop=True), log
