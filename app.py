import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. CONFIGURACIÓN PROFESIONAL DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Inteligente | San Martín",
    page_icon="📊",
    layout="wide", # Esto es clave para el look de Power BI
    initial_sidebar_state="expanded"
)

# Estilo personalizado para mejorar la estética
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS CON CACHÉ
@st.cache_data
def load_data():
    # Intentamos cargar el CSV de prueba que creamos
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    else:
        st.error(f"⚠️ No se encontró el archivo en: {ruta}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.image("https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)
    st.sidebar.title("Filtros del Reporte")
    
    selected_year = st.sidebar.selectbox("Seleccione el Año", sorted(df['Año'].unique(), reverse=True))
    selected_prov = st.sidebar.multiselect("Provincias", df['Provincia'].unique(), default=df['Provincia'].unique())

    # Filtrado dinámico
    df_selection = df[(df['Año'] == selected_year) & (df['Provincia'].isin(selected_prov))]

    # --- CUERPO PRINCIPAL ---
    st.title("🚀 Dashboard de Gestión Territorial")
    st.markdown(f"Análisis detallado para el año **{selected_year}**")

    # 3. FILA DE INDICADORES (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_val = df_selection['Valor'].sum()
    pob_total = df_selection['Poblacion'].sum()
    var_avg = df_selection['Variacion'].mean()

    kpi1.metric(label="Valor Total", value=f"{total_val:,}")
    kpi2.metric(label="Población Impactada", value=f"{pob_total:,}")
    kpi3.metric(label="Variación % Promedio", value=f"{var_avg:.1f}%", delta=f"{var_avg:.1f}%")
    kpi4.metric(label="Provincias Activas", value=len(selected_prov))

    st.markdown("---")

    # 4. FILA DE GRÁFICOS (Grid Layout)
    col_left, col_right = st.columns(2)

    with col_left:
        # Gráfico de Burbujas (Bubble Chart del Colab)
        st.subheader("📍 Relación Valor vs Variación")
        fig_bubble = px.scatter(
            df_selection, x="Valor", y="Variacion", size="Poblacion", 
            color="Provincia", hover_name="Distrito", size_max=40,
            template="plotly_white"
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col_right:
        # Gráfico de Barras Agrupadas
        st.subheader("📊 Distribución por Categoría")
        fig_bar = px.bar(
            df_selection, x="Categoria", y="Valor", color="Provincia",
            barmode="group", text_auto='.2s'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # 5. FILA DEL MAPA Y TABLA
    st.subheader("🗺️ Vista Geoespacial e Información Detallada")
    m1, m2 = st.columns([2, 1]) # El mapa será más ancho que la tabla

    with m1:
        fig_map = px.scatter_mapbox(
            df_selection, lat="Latitud", lon="Longitud", size="Poblacion", 
            color="Valor", hover_name="Distrito", zoom=7, height=400,
            mapbox_style="carto-positron"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with m2:
        st.write("Datos filtrados")
        st.dataframe(df_selection[['Distrito', 'Valor', 'Variacion']], height=400)

else:
    st.info("Sube el archivo 'resultados.csv' a la carpeta 'data/' en tu repo para ver la magia.")