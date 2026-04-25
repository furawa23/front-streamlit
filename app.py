import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de ancho completo
st.set_page_config(layout="wide", page_title="Dashboard Pro")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    else:
        # Esto crea un DF vacío para que la app no explote si no hay archivo
        st.error(f"No se encontró el archivo en {ruta}")
        return pd.DataFrame()
df = load_data()

# --- FILTROS ESTILO POWER BI (Sidebar) ---
st.sidebar.header("Panel de Control")
# Filtro por Año
año = st.sidebar.selectbox("Seleccionar Año", sorted(df['Año'].unique(), reverse=True))
# Filtro por Provincia
provincias = st.sidebar.multiselect("Provincias", df['Provincia'].unique(), default=df['Provincia'].unique())

# Filtrar el DataFrame
df_filtered = df[(df['Año'] == año) & (df['Provincia'].isin(provincias))]

# --- DASHBOARD ---
st.title(f"📊 Análisis de Datos - {año}")

# 1. Gráfico de Burbujas (Como el de tu Colab)
st.subheader("Relación de Variables (Bubble Chart)")
fig_bubble = px.scatter(
    df_filtered, 
    x="Variable_X", # Cambia por tus columnas reales
    y="Variable_Y", 
    size="Poblacion", 
    color="Provincia",
    hover_name="Distrito", 
    log_x=True, 
    size_max=60,
    template="plotly_dark" # O "ggplot2" para un look más limpio
)
st.plotly_chart(fig_bubble, use_container_width=True)

# 2. Dos columnas para gráficos comparativos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución por Categoría")
    fig_bar = px.bar(df_filtered, x="Categoria", y="Valor", color="Provincia", barmode="group")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Variación Mensual")
    fig_line = px.line(df_filtered, x="Mes", y="Valor", color="Provincia", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# 3. El Mapa (Si tienes Lat/Lon)
st.subheader("📍 Mapa de Distribución Regional")
fig_map = px.scatter_mapbox(
    df_filtered, lat="Latitud", lon="Longitud", color="Valor", size="Valor",
    color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=6,
    mapbox_style="carto-positron"
)
st.plotly_chart(fig_map, use_container_width=True)