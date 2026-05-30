from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st


def plot_line_evolution(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str = "#1f77b4",
    ylabel: str = "",
) -> px.line:
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    fig.update_traces(line=dict(width=3, color=color), marker=dict(size=8, color=color))
    fig.update_layout(
        yaxis_title=ylabel or y,
        xaxis_title="Fecha",
        showlegend=False,
        template="plotly_white",
    )
    return fig


def plot_entity_evolution(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str = "#d62728",
    ylabel: str = "",
    group_col: str | None = None,
) -> px.line:
    if group_col:
        dfg = df.groupby([x, group_col], as_index=False)[y].sum()
        fig = px.line(dfg, x=x, y=y, color=group_col, markers=True, title=title)
        fig.update_layout(legend_title=group_col)
    else:
        dfg = df.groupby(x, as_index=False)[y].sum()
        fig = px.line(dfg, x=x, y=y, title=title, markers=True)
        fig.update_traces(line=dict(width=3, color=color), marker=dict(size=8, color=color))
    fig.update_layout(
        yaxis_title=ylabel or y,
        xaxis_title="Fecha",
        template="plotly_white",
    )
    return fig


def plot_system_bars(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    ylabel: str = "",
    color_scale: str = "Viridis",
) -> px.bar:
    fig = px.bar(
        df, x=x, y=y, title=title, text_auto=True,
        color=y, color_continuous_scale=color_scale,
    )
    fig.update_traces(textposition="inside", textfont=dict(size=16, color="white"))
    fig.update_layout(
        yaxis_title=ylabel or y,
        xaxis_title="Fecha",
        showlegend=False,
        bargap=0.2,
    )
    return fig


def plot_participation_bars(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    total: float,
    color_scale: str = "Blues",
) -> px.bar:
    participacion = (
        df.groupby(group_col, as_index=False)[value_col]
        .sum()
        .assign(Porcentaje=lambda x: (x[value_col] / total) * 100)
        .sort_values("Porcentaje", ascending=False)
    )
    fig = px.bar(
        participacion,
        x="Porcentaje",
        y=group_col,
        orientation="h",
        color="Porcentaje",
        color_continuous_scale=color_scale,
        text="Porcentaje",
        labels={"Porcentaje": "Participación (%)", group_col: ""},
    )
    fig.update_traces(
        texttemplate="%{x:.2f}%",
        textposition="outside",
        marker_line=dict(color="#000", width=0.5),
    )
    fig.update_layout(
        height=600,
        xaxis_range=[0, participacion["Porcentaje"].max() * 1.15],
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
    )
    return fig


def plot_comparison_lines(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    ylabel: str = "",
) -> px.line:
    fig = px.line(
        df, x=x, y=y, color=color, markers=True,
        line_shape="spline", title=title,
    )
    fig.update_layout(
        yaxis_title=ylabel or y,
        xaxis_title="Fecha",
        legend_title=color,
        height=500,
    )
    return fig


def show_sidebar_info(
    df: pd.DataFrame,
    entity_label: str,
    entity_col: str,
    parent_label: str,
    parent_col: str,
    metric_label: str,
    metric_value: float,
    unit: str,
) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Métricas del Sistema")
    if not df.empty:
        st.sidebar.metric(entity_label, df[entity_col].nunique())
        st.sidebar.metric(parent_label, df[parent_col].nunique())
        st.sidebar.metric(metric_label, f"{metric_value:,.2f} {unit}")
        st.sidebar.caption(
            f"Periodo: {df['FECHA'].min().strftime('%Y-%m')} "
            f"a {df['FECHA'].max().strftime('%Y-%m')}"
        )
    else:
        st.sidebar.warning("Sin datos para mostrar métricas")


def show_price_sidebar_info(
    df: pd.DataFrame,
    entity_label: str,
    entity_col: str,
    parent_label: str,
    parent_col: str,
) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Información del Sistema")
    st.sidebar.write(f"Total de {entity_label}: {df[entity_col].nunique()}")
    st.sidebar.write(f"Total de {parent_label}: {df[parent_col].nunique()}")
    if "FECHA" in df.columns and not df.empty:
        st.sidebar.write(
            f"Rango de fechas: {df['FECHA'].min().strftime('%Y-%m-%d')} "
            f"a {df['FECHA'].max().strftime('%Y-%m-%d')}"
        )
