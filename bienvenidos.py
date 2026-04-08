import streamlit as st

import importlib.util
import sys
from pathlib import Path
import subprocess
import os

# Configuración general de la página
st.set_page_config(
    page_title="Dashboard Energía Bolivia",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Dashboard Energético de Bolivia")

# Imagen representativa
st.image(
    "https://media.istockphoto.com/id/1032683612/photo/solar-energy-and-wind-power-stations.jpg?s=612x612&w=0&k=20&c=KXElDTxrRrXG72sVD4QGnctJU1iSMroKPOl6XUfGHNk=",
    caption="Energías renovables impulsando el futuro de Bolivia"
)


# Texto introductorio
st.markdown("""
## 🔍 Exploración de Indicadores del Sector Eléctrico

Este dashboard interactivo te permite analizar los principales indicadores tarifarios y económicos del sector eléctrico boliviano, con enfoque especial en:

- 🌞 **Precio de Energía**
- 💡 **Precio de Potencia**
- 📊 **Precio Monómico**

Está diseñado para apoyar la toma de decisiones estratégicas en torno a la transición energética, la planificación regulatoria y el análisis de desempeño de los agentes del sistema eléctrico.

---

🧭 **Usa el menú lateral izquierdo** para navegar por las secciones del dashboard.
""")

st.success("📌 Este dashboard es parte del esfuerzo por promover la transparencia y sostenibilidad del sistema eléctrico nacional.")

# Función para ejecutar un script externo
def ejecutar_script(ruta_script):
    """Ejecuta un script Python externo"""
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_script):
            st.error(f"El archivo {ruta_script} no existe")
            return
        
        # Ejecutar el script
        result = subprocess.run([sys.executable, ruta_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            st.success("Script ejecutado correctamente")
            if result.stdout:
                st.code(result.stdout, language='python')
        else:
            st.error(f"Error al ejecutar el script: {result.stderr}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Función para mostrar el contenido de un script
def mostrar_codigo(ruta_script):
    """Muestra el código de un script"""
    try:
        with open(ruta_script, 'r', encoding='utf-8') as file:
            codigo = file.read()
        st.code(codigo, language='python')
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")

# Menú lateral principal
st.sidebar.title("Navegación Principal")
modulo_principal = st.sidebar.radio(
    "Selecciona el módulo",
    ("Generación", "Distribución", "Documentación"),
    index=0
)

# Módulo de Generación
if modulo_principal == "Generación":
    st.header("🏭 Módulo de Generación")
    
    # Submenú para scripts de generación
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Scripts de Generación")
    
    script_generacion = st.sidebar.selectbox(
        "Selecciona el script a ejecutar",
        [
            "Seleccionar script",
            "energia_por_generador.py",
            "energia_por_tecnologia.py", 
            "capacidad_instalada.py",
            "costos_generacion.py",
            "mix_energetico.py"
        ]
    )
    
    # Contenedor principal para los scripts
    if script_generacion != "Seleccionar script":
        ruta_script = f"./generacion/{script_generacion}"
        
        st.subheader(f"Ejecutando: {script_generacion}")
        
        # Pestañas para diferentes acciones
        tab1, tab2, tab3 = st.tabs(["📊 Ejecutar Script", "👀 Ver Código", "📋 Descripción"])
        
        with tab1:
            st.info(f"Ejecutando {script_generacion}...")
            if st.button("▶️ Ejecutar Script", type="primary"):
                with st.spinner("Ejecutando script..."):
                    ejecutar_script(ruta_script)
        
        with tab2:
            st.info("Visualizando el código fuente:")
            mostrar_codigo(ruta_script)
        
        with tab3:
            # Descripciones de cada script
            descripciones = {
                "energia_por_generador.py": """
                ## 📈 Energía por Generador
                
                **Descripción:** Este script analiza la producción de energía desagregada por cada generador individual del sistema.
                
                **Funcionalidades:**
                - Producción horaria/diaria por generador
                - Factor de planta individual
                - Disponibilidad y horas de operación
                - Análisis de eficiencia por unidad
                
                **Outputs principales:**
                - Reporte de producción por generador
                - Gráficos de tendencia individual
                - Indicadores de performance
                """,
                
                "energia_por_tecnologia.py": """
                ## 🔧 Energía por Tecnología
                
                **Descripción:** Análisis agregado de generación por tipo de tecnología.
                
                **Funcionalidades:**
                - Producción por tecnología (térmica, hidro, solar, eólica, etc.)
                - Participación porcentual en el mix
                - Evolución temporal por tecnología
                - Comparativa entre tecnologías
                
                **Outputs principales:**
                - Mix energético nacional
                - Curvas de duración por tecnología
                - Análisis estacional por tipo de generación
                """,
                
                "capacidad_instalada.py": """
                ## 🏗️ Capacidad Instalada
                
                **Descripción:** Análisis de la capacidad instalada y disponible del sistema.
                
                **Funcionalidades:**
                - Capacidad instalada por tecnología
                - Capacidad disponible neta
                - Reserva del sistema
                - Proyecciones de capacidad
                
                **Outputs principales:**
                - Matriz de capacidad instalada
                - Indicadores de reserva
                - Proyecciones de expansión
                """,
                
                "costos_generacion.py": """
                ## 💰 Costos de Generación
                
                **Descripción:** Análisis de costos marginales y totales de generación.
                
                **Funcionalidades:**
                - Costos variables por tecnología
                - Costos marginales horarios
                - Costos totales del sistema
                - Análisis de eficiencia económica
                
                **Outputs principales:**
                - Curva de costos marginales
                - Costos medios por tecnología
                - Análisis de eficiencia económica
                """,
                
                "mix_energetico.py": """
                ## 🌿 Mix Energético
                
                **Descripción:** Análisis de la composición energética del sistema.
                
                **Funcionalidades:**
                - Participación de renovables vs convencionales
                - Intensidad de carbono del sistema
                - Evolución del mix energético
                - Proyecciones de descarbonización
                
                **Outputs principales:**
                - Indicadores de sostenibilidad
                - Intensidad de CO2 por MWh
                - Trayectoria de descarbonización
                """
            }
            
            if script_generacion in descripciones:
                st.markdown(descripciones[script_generacion])
            else:
                st.info("Descripción no disponible para este script.")
    
    else:
        # Vista por defecto del módulo de generación
        st.info("🌅 Selecciona un script específico del menú lateral para comenzar el análisis.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📋 Scripts Disponibles - Generación
            
            1. **energia_por_generador.py** - Producción individual por unidad
            2. **energia_por_tecnologia.py** - Análisis por tipo de tecnología  
            3. **capacidad_instalada.py** - Capacidad instalada y disponible
            4. **costos_generacion.py** - Análisis de costos marginales
            5. **mix_energetico.py** - Composición del mix energético
            
            ### 🚀 Cómo usar:
            - Selecciona un script del menú lateral
            - Ejecuta el script directamente
            - Visualiza el código fuente
            - Revisa la documentación
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Métricas Clave del Sistema
            
            **Capacidad Total:** 3,450 MW
            **Generación Anual:** 18,200 GWh
            **Factor de Planta:** 58%
            **Participación Renovables:** 35%
            
            ### 🔧 Tecnologías Disponibles:
            - Hidroeléctrica: 1,200 MW
            - Térmica (Gas): 1,800 MW
            - Solar: 250 MW
            - Eólica: 180 MW
            - Biomasa: 20 MW
            
            ### 📈 Última Actualización:
            Datos actualizados al último mes operativo
            """)

# Módulo de Distribución (estructura similar)
elif modulo_principal == "Distribución":
    st.header("📊 Módulo de Distribución")
    
    # Submenú para scripts de distribución
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Scripts de Distribución")
    
    script_distribucion = st.sidebar.selectbox(
        "Selecciona el script a ejecutar",
        [
            "Seleccionar script",
            "demanda_zonas.py",
            "perdidas_tecnicas.py",
            "calidad_servicio.py",
            "tarifas_electricas.py",
            "cobertura_servicio.py"
        ],
        key="distribucion_script"
    )
    
    if script_distribucion != "Seleccionar script":
        ruta_script = f"./distribucion/{script_distribucion}"
        st.subheader(f"Ejecutando: {script_distribucion}")
        
        # Implementar lógica similar a generación
        tab1, tab2, tab3 = st.tabs(["📊 Ejecutar Script", "👀 Ver Código", "📋 Descripción"])
        
        with tab1:
            st.info(f"Ejecutando {script_distribucion}...")
            if st.button("▶️ Ejecutar Script", type="primary", key="ejecutar_dist"):
                with st.spinner("Ejecutando script..."):
                    ejecutar_script(ruta_script)
        
        with tab2:
            st.info("Visualizando el código fuente:")
            mostrar_codigo(ruta_script)
        
        with tab3:
            st.info("Descripción del script de distribución")
            # Agregar descripciones específicas para distribución
    
    else:
        st.info("🌅 Selecciona un script específico del menú lateral para comenzar el análisis.")
        # Vista por defecto similar a generación

# Módulo de Documentación
else:
    st.header("📚 Documentación y Recursos")
    
    st.markdown("""
    ## 🎯 Guía de Uso del Dashboard
    
    ### 📋 Estructura del Sistema:
    
    **Módulo de Generación:**
    - `generacion/energia_por_generador.py` - Análisis por unidad generadora
    - `generacion/energia_por_tecnologia.py` - Análisis por tecnología
    - `generacion/capacidad_instalada.py` - Capacidad del sistema
    - `generacion/costos_generacion.py` - Análisis económico
    - `generacion/mix_energetico.py` - Composición energética
    
    **Módulo de Distribución:**
    - `distribucion/demanda_zonas.py` - Análisis de demanda
    - `distribucion/perdidas_tecnicas.py` - Pérdidas del sistema
    - `distribucion/calidad_servicio.py` - Indicadores de calidad
    - `distribucion/tarifas_electricas.py` - Análisis tarifario
    - `distribucion/cobertura_servicio.py` - Cobertura geográfica
    
    ### 🚀 Cómo ejecutar scripts:
    1. Selecciona el módulo en el menú principal
    2. Elige el script específico del submenú lateral
    3. Usa las pestañas para:
       - 📊 Ejecutar el script directamente
       - 👀 Ver el código fuente
       - 📋 Leer la documentación
    
    ### ⚙️ Requisitos del Sistema:
    - Python 3.8+
    - Librerías listadas en requirements.txt
    - Acceso a la base de datos energética
    - Permisos de ejecución adecuados
    """)

# Pie de página
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Dashboard Energético de Bolivia** 
    \nSistema de análisis del sector eléctrico
    \n📧 Contacto: equipo.energia@bolivia.bo
    \n🔄 Versión: 2.0.0
    """
)

# Información general
st.markdown("---")
st.success("""
📌 **Sistema de Análisis Energético** - Este dashboard proporciona acceso centralizado 
a todos los scripts de análisis del sector eléctrico boliviano. Selecciona un módulo 
y script específico para comenzar tu análisis.
""")
