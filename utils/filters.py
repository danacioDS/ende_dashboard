from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st
from datetime import datetime


def date_range_slider(
    df: pd.DataFrame,
    date_col: str = "FECHA",
    key: str = "date_range",
) -> tuple[pd.Timestamp, pd.Timestamp]:
    min_date = df[date_col].min()
    max_date = df[date_col].max()

    if pd.isna(min_date) or pd.isna(max_date):
        st.sidebar.warning("No hay fechas válidas. Usando rango por defecto.")
        min_date = pd.Timestamp(datetime(2023, 1, 1))
        max_date = pd.Timestamp.now()

    selected = st.sidebar.slider(
        "Rango de fechas",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
        format="YYYY-MM",
        key=key,
    )
    return pd.Timestamp(selected[0]), pd.Timestamp(selected[1])


def filter_by_date(
    df: pd.DataFrame,
    date_col: str = "FECHA",
    key: str = "date_range",
) -> pd.DataFrame:
    if df.empty:
        st.warning("No hay datos disponibles para filtrar")
        return df

    start, end = date_range_slider(df, date_col, key)
    mask = (df[date_col] >= start) & (df[date_col] <= end)
    return df[mask].copy()


def entity_selectbox(
    df: pd.DataFrame,
    col: str,
    label: str,
    key: str | None = None,
) -> str:
    options = sorted(df[col].unique().tolist(), key=str)
    return st.sidebar.selectbox(label, options, key=key)


def child_selectbox(
    df: pd.DataFrame,
    parent_col: str,
    parent_value: str,
    child_col: str,
    label: str,
    key: str | None = None,
) -> str:
    options = sorted(
        df[df[parent_col] == parent_value][child_col].unique().tolist()
    )
    return st.sidebar.selectbox(label, options, key=key)
