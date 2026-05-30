"""Lightweight data validation for pipeline outputs."""
from pathlib import Path

import pandas as pd


class ValidationError(Exception):
    """Raised when data validation fails."""

def validate_required_columns(
    df: pd.DataFrame, required: list[str], name: str = "DataFrame"
) -> None:
    """Validate that all required columns exist."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValidationError(f"{name}: Missing required columns: {missing}")

def validate_numeric_columns(df: pd.DataFrame, cols: list[str], name: str = "DataFrame") -> None:
    """Validate that specified columns are numeric."""
    for col in cols:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            cleaned = df[col].astype(str).str.replace(",", "", regex=False)
            try:
                df[col] = pd.to_numeric(cleaned, errors='raise')
            except (ValueError, TypeError):
                non_numeric = df[col].unique().tolist()[:5]
                raise ValidationError(
                    f"{name}: Column '{col}' has non-numeric values: {non_numeric}"
                )

def validate_no_missing_critical(
    df: pd.DataFrame, cols: list[str], name: str = "DataFrame"
) -> None:
    """Validate no missing values in critical columns."""
    for col in cols:
        if col in df.columns and df[col].isna().any():
            count = df[col].isna().sum()
            raise ValidationError(f"{name}: Column '{col}' has {count} missing values")

def validate_file_not_empty(path: Path, name: str = "File") -> None:
    """Validate a file exists and is not empty."""
    if not path.exists():
        raise ValidationError(f"{name}: File not found: {path}")
    if path.stat().st_size == 0:
        raise ValidationError(f"{name}: File is empty: {path}")

def validate_output_dataset(
    path: Path, required_cols: list[str], name: str = "Dataset"
) -> pd.DataFrame:
    """Full validation of an output dataset file."""
    validate_file_not_empty(path, name)
    df = pd.read_excel(path)
    validate_required_columns(df, required_cols, name)
    numeric_cols = [c for c in df.columns if c not in required_cols]
    validate_numeric_columns(df, numeric_cols, name)
    validate_no_missing_critical(df, required_cols, name)
    return df
