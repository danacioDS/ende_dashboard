import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Dashboard Energía Bolivia",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Dashboard Energético de Bolivia")

st.image(
    "https://media.istockphoto.com/id/1032683612/photo/solar-energy-and-wind-power-stations.jpg?s=612x612&w=0&k=20&c=KXElDTxrRrXG72sVD4QGnctJU1iSMroKPOl6XUfGHNk=",
    caption="Energías renovables impulsando el futuro de Bolivia"
)

st.markdown("""
## 🔍 Exploración de Indicadores del Sector Eléctrico

Este dashboard interactivo te permite analizar los principales indicadores
tarifarios y económicos del sector eléctrico boliviano, con enfoque en:

- 🌞 **Precio de Energía**
- 💡 **Precio de Potencia**
- 📊 **Precio Monómico**

Diseñado para apoyar la toma de decisiones estratégicas en la transición
energética, planificación regulatoria y análisis de desempeño de los agentes
del sistema eléctrico.

---

🧭 **Usa el menú lateral izquierdo** para navegar por las secciones del dashboard.
""")

st.success(
    "📌 Este dashboard es parte del esfuerzo por promover la transparencia "
    "y sostenibilidad del sistema eléctrico nacional."
)

# Sidebar info
st.sidebar.info(
    "**Dashboard Energético de Bolivia**\n\n"
    "Selecciona una página en el menú superior para ver los análisis "
    "de generación y distribución del sistema eléctrico boliviano."
)
