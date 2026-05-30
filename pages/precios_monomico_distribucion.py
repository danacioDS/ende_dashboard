import streamlit as st
from utils.data_loader import load_and_normalize, get_page_config
from utils.filters import filter_by_date, entity_selectbox, child_selectbox
from utils.charts import plot_line_evolution, plot_system_bars, plot_comparison_lines, show_price_sidebar_info

CONFIG = get_page_config("precios_monomico_distribucion")

st.set_page_config(page_title=CONFIG["title"], layout="wide")
st.title(CONFIG["subtitle"])

df = load_and_normalize(CONFIG["file"], CONFIG["entity_cols"], CONFIG["value_pattern"], CONFIG["value_name"])
if df is None:
    st.stop()

df_f = filter_by_date(df)
parent = entity_selectbox(df_f, CONFIG["parent_col"], CONFIG["parent_label"])
child = child_selectbox(df_f, CONFIG["parent_col"], parent, CONFIG["child_col"], CONFIG["child_label"])

tab1, tab2 = st.tabs(["Visión Detallada", "Visión de Promedios"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"Evolución {CONFIG['value_name']} para {CONFIG['child_label']}: {child}")
        d = df_f[df_f[CONFIG["child_col"]] == child]
        if not d.empty:
            fig = plot_line_evolution(d, "FECHA", CONFIG["value_name"], f"{CONFIG['child_label']}: {child}", ylabel=CONFIG["value_name"])
            st.plotly_chart(fig, use_container_width=True)
            st.metric(f"Promedio {child}", f"{d[CONFIG['value_name']].mean():.2f} {CONFIG['unit']}")
    with c2:
        st.subheader(f"Precio Promedio para {CONFIG['parent_label']}: {parent}")
        d = df_f[df_f[CONFIG["parent_col"]] == parent]
        if not d.empty:
            dp = d.groupby(["FECHA", CONFIG["parent_col"]], as_index=False)[CONFIG["value_name"]].mean()
            fig = plot_line_evolution(dp, "FECHA", CONFIG["value_name"], f"{CONFIG['parent_label']}: {parent}", color="#d62728", ylabel=CONFIG["value_name"])
            st.plotly_chart(fig, use_container_width=True)
            st.metric(f"Promedio {parent}", f"{d[CONFIG['value_name']].mean():.2f} {CONFIG['unit']}")

    st.subheader("Evolución del Precio Promedio del Sistema")
    sys_data = df_f.groupby("FECHA", as_index=False)[CONFIG["value_name"]].mean()
    sys_avg = sys_data[CONFIG["value_name"]].mean()
    fig = plot_system_bars(sys_data, "FECHA", CONFIG["value_name"], "Evolución del Sistema", color_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Precio Promedio del Sistema", f"{sys_avg:.2f} {CONFIG['unit']}")

with tab2:
    st.header("Análisis Comparativo")
    st.subheader(f"Comparación de {CONFIG['parent_label']}s")
    comp = df_f.groupby(["FECHA", CONFIG["parent_col"]], as_index=False)[CONFIG["value_name"]].mean()
    fig = plot_comparison_lines(comp, "FECHA", CONFIG["value_name"], CONFIG["parent_col"],
                                 f"Comparación por {CONFIG['parent_label']}", CONFIG["value_name"])
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Mínimo Sistema", f"{df_f[CONFIG['value_name']].min():.2f} {CONFIG['unit']}")
    c2.metric("Promedio Sistema", f"{df_f[CONFIG['value_name']].mean():.2f} {CONFIG['unit']}")
    c3.metric("Máximo Sistema", f"{df_f[CONFIG['value_name']].max():.2f} {CONFIG['unit']}")

show_price_sidebar_info(df_f, CONFIG["child_label"]+"s", CONFIG["child_col"], CONFIG["parent_label"]+"s", CONFIG["parent_col"])
