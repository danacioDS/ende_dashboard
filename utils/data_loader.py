from __future__ import annotations

import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st
import yaml


def _load_config() -> dict[str, Any]:
    config_path = Path(__file__).resolve().parent.parent / "ende_config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG_CACHE: dict[str, Any] | None = None


def get_config() -> dict[str, Any]:
    global CONFIG_CACHE
    if CONFIG_CACHE is None:
        CONFIG_CACHE = _load_config()
    return CONFIG_CACHE


def get_page_config(page_name: str) -> dict[str, Any]:
    cfg = get_config()
    pages = cfg.get("dashboard", {}).get("pages", {})
    if page_name not in pages:
        st.error(f"Configuración no encontrada para: {page_name}")
        st.stop()
    return dict(pages[page_name])


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = (
        df.columns.str.normalize("NFKC")
        .str.replace("\u200b", "", regex=False)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )
    df.columns = cols
    return df


def build_date_mapping(start_year: int = 2023, end_year: int = 2025) -> dict[str, str]:
    mapping: dict[str, str] = {}
    d = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 1)
    while d <= end:
        mapping[d.strftime("%m%Y")] = d.strftime("%Y-%m-01")
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1)
        else:
            d = d.replace(month=d.month + 1)
    return mapping


def parse_period_code(period_code: str) -> Optional[datetime]:
    try:
        if len(period_code) == 5:
            month = int(period_code[0])
            year = int(period_code[1:5])
        elif len(period_code) == 6:
            month = int(period_code[0:2])
            year = int(period_code[2:6])
        else:
            return None
        return datetime(year, month, 1)
    except (ValueError, IndexError):
        return None


def resolve_data_path(relative_path: str) -> Path:
    current_dir = Path(__file__).resolve().parent.parent
    return current_dir / relative_path


def load_and_normalize(
    file_relpath: str,
    entity_cols: list[str],
    value_pattern: str | None = None,
    value_name: str | None = None,
) -> Optional[pd.DataFrame]:
    """Load wide-format Excel, normalize to long format.

    Returns a DataFrame with columns:
      - All entity_cols present in the file
      - FECHA (parsed from month-coded column names)
      - VALOR (numeric value)
    """
    file_path = resolve_data_path(file_relpath)
    if not file_path.exists():
        st.error(f"Archivo no encontrado: {file_path}")
        return None

    try:
        raw_cols = pd.read_excel(file_path, nrows=0).columns.tolist()
        norm_cols = [
            unicodedata.normalize("NFKC", c).strip().replace("\u200b", "").replace("\xa0", " ")
            for c in raw_cols
        ]
        rename_map = dict(zip(raw_cols, norm_cols))
        df = pd.read_excel(file_path, engine="openpyxl").rename(columns=rename_map)
    except Exception as e:
        st.error(f"Error al leer archivo: {e}")
        return None

    if df.empty:
        st.error("El archivo está vacío")
        return None

    # Detect entity columns that actually exist in the data
    valid_entity = [c for c in entity_cols if c in df.columns]
    missing_entity = set(entity_cols) - set(df.columns)
    if missing_entity:
        st.warning(f"Entity columns not found: {missing_entity}")

    if not valid_entity:
        st.error("No se encontraron columnas de entidad en el archivo")
        return None

    # Detect value columns: either matching pattern or anything not entity
    if value_pattern:
        value_cols = [c for c in df.columns if value_pattern in c and c not in valid_entity]
    else:
        value_cols = [c for c in df.columns if c not in valid_entity]

    if not value_cols:
        st.error(
            f"No se encontraron columnas con el patrón '{value_pattern}'. "
            f"Columnas disponibles: {df.columns.tolist()[:20]}"
        )
        return None

    # Melt to long format
    melted = df.melt(
        id_vars=valid_entity,
        value_vars=value_cols,
        var_name="VARIABLE",
        value_name="VALOR",
    )

    # Extract period code from column name (last whitespace-delimited token)
    melted["FECHA"] = melted["VARIABLE"].str.split().str[-1]

    date_mapping = build_date_mapping()
    melted["FECHA"] = melted["FECHA"].apply(lambda x: date_mapping.get(x, pd.NaT))
    melted = melted.dropna(subset=["FECHA"])
    melted["FECHA"] = pd.to_datetime(melted["FECHA"], errors="coerce")
    melted = melted.dropna(subset=["FECHA"])

    melted["VALOR"] = pd.to_numeric(
        melted["VALOR"].astype(str).str.replace(",", ""), errors="coerce"
    )
    melted = melted.dropna(subset=["VALOR"])

    columns = valid_entity + ["FECHA", "VALOR"]
    result = melted[columns].reset_index(drop=True)
    if value_name:
        result = result.rename(columns={"VALOR": value_name})
    return result


# --- Backward-compatibility wrappers ---


def load_and_melt(
    file_relpath: str,
    id_vars: list[str],
    value_col_pattern: str,
    value_name: str,
    date_mapping: dict[str, str] | None = None,
) -> Optional[pd.DataFrame]:
    """Legacy wrapper — delegates to load_and_normalize."""
    return load_and_normalize(file_relpath, id_vars, value_col_pattern, value_name)


def load_and_pivot_columns(
    file_relpath: str,
    id_vars: list[str],
    col_pattern: str,
    value_name: str,
) -> Optional[pd.DataFrame]:
    """Legacy wrapper — delegates to load_and_normalize."""
    return load_and_normalize(file_relpath, id_vars, col_pattern, value_name)
