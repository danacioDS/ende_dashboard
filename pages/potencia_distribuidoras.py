import streamlit as st
import pandas as pd
from utils.data_loader import load_and_normalize, get_page_config
from utils.filters import filter_by_date, entity_selectbox, child_selectbox
from utils.charts import (
    plot_line_evolution, plot_entity_evolution, plot_system_bars,
    plot_participation_bars, plot_comparison_lines, show_sidebar_info,
)

CONFIG = get_page_config("potencia_distribuidoras")

st.set_page_config(page_title=CONFIG["title"], layout="wide")
st.title(CONFIG["subtitle"])

df = load_and_normalize(CONFIG["file"], CONFIG["entity_cols"], CONFIG["value_pattern"], CONFIG["value_name"])
if df is None:
    st.stop()

df_f = filter_by_date(df)
total = df_f[CONFIG["value_name"]].sum()
parent = entity_selectbox(df_f, CONFIG["parent_col"], CONFIG["parent_label"])
child = child_selectbox(df_f, CONFIG["parent_col"], parent, CONFIG["child_col"], CONFIG["child_label"])

tab1, tab2 = st.tabs(["Visión Detallada", "Visión de Promedios"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"Evolución del {CONFIG['child_label']}: {child}")
        d = df_f[df_f[CONFIG["child_col"]] == child]
        if not d.empty:
            fig = plot_line_evolution(d, "FECHA", CONFIG["value_name"], f"{CONFIG['child_label']}: {child}", ylabel=CONFIG["value_name"])
            st.plotly_chart(fig, use_container_width=True)
            pct = (d[CONFIG["value_name"]].sum() / total) * 100
            m1, m2 = st.columns(2)
            m1.metric("Promedio", f"{d[CONFIG['value_name']].mean():,.2f} {CONFIG['unit']}")
            m2.metric("Participación", f"{pct:.2f}%")
    with c2:
        st.subheader(f"Evolución de {CONFIG['parent_label']}: {parent}")
        d = df_f[df_f[CONFIG["parent_col"]] == parent]
        if not d.empty:
            fig = plot_entity_evolution(d, "FECHA", CONFIG["value_name"], f"{CONFIG['parent_label']}: {parent}", ylabel=CONFIG["value_name"])
            st.plotly_chart(fig, use_container_width=True)
            avg = d.groupby("FECHA")[CONFIG["value_name"]].sum().mean()
            st.metric("Promedio", f"{avg:,.2f} {CONFIG['unit']}")

    if not df_f.empty:
        sys_data = df_f.groupby("FECHA", as_index=False)[CONFIG["value_name"]].sum()
        sys_avg = sys_data[CONFIG["value_name"]].mean()
        st.subheader("Evolución del Sistema")
        fig = plot_system_bars(sys_data, "FECHA", CONFIG["value_name"], "Evolución del Sistema", color_scale="Cividis")
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Promedio del Sistema", f"{sys_avg:,.2f} {CONFIG['unit']}")
        st.subheader(f"Participación por {CONFIG['parent_label']}")
        fig = plot_participation_bars(df_f, CONFIG["parent_col"], CONFIG["value_name"], total, "Reds")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Análisis Comparativo")
    if not df_f.empty:
        comp = df_f.groupby(["FECHA", CONFIG["parent_col"]], as_index=False)[CONFIG["value_name"]].sum()
        fig = plot_comparison_lines(comp, "FECHA", CONFIG["value_name"], CONFIG["parent_col"],
                                     f"Comparación por {CONFIG['parent_label']}", CONFIG["value_name"])
        st.plotly_chart(fig, use_container_width=True)

        total_mes = df_f.groupby("FECHA", as_index=False)[CONFIG["value_name"]].sum().rename(columns={CONFIG["value_name"]: "Total"})
        ent_mes = df_f.groupby(["FECHA", CONFIG["parent_col"]], as_index=False)[CONFIG["value_name"]].sum()
        merged = pd.merge(ent_mes, total_mes, on="FECHA")
        merged["Part"] = (merged[CONFIG["value_name"]] / merged["Total"]) * 100
        stats = merged.groupby(CONFIG["parent_col"], as_index=False).agg(
            Min=(CONFIG["value_name"], "min"), Prom=(CONFIG["value_name"], "mean"),
            Max=(CONFIG["value_name"], "max"), PartProm=("Part", "mean"),
        ).sort_values("PartProm", ascending=False)
        stats.columns = [CONFIG["parent_label"], f"Mín ({CONFIG['unit']})", f"Prom ({CONFIG['unit']})", f"Máx ({CONFIG['unit']})", "Part. Prom (%)"]
        for c in stats.columns[1:4]:
            stats[c] = stats[c].apply(lambda x: f"{x:,.2f}")
        stats["Part. Prom (%)"] = stats["Part. Prom (%)"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(stats)

show_sidebar_info(df_f, CONFIG["child_label"], CONFIG["child_col"], CONFIG["parent_label"], CONFIG["parent_col"],
                  "Potencia Total", total, CONFIG["unit"])
