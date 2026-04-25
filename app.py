import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Pro", layout="wide")

# Título Principal
st.title("📊 Dashboard de Análisis Territorial")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Simulamos tus datos. Aquí leerías tu CSV generado en Colab:
    # df = pd.read_csv('data/resultados.csv')
    data = {
        'Año': [2023, 2023, 2024, 2024, 2025, 2025],
        'Provincia': ['San Martín', 'Moyobamba', 'San Martín', 'Moyobamba', 'San Martín', 'Lamas'],
        'Lat': [-6.48, -6.03, -6.48, -6.03, -6.48, -6.42],
        'Lon': [-76.37, -76.97, -76.37, -76.97, -76.37, -76.52],
        'Valor': [100, 150, 120, 180, 200, 90],
        'Variación': [5, 10, 2, 8, 15, -3]
    }
    return pd.DataFrame(data)

df = load_data()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros del Reporte")

# Filtro de Año
años = sorted(df['Año'].unique())
año_sel = st.sidebar.multiselect("Selecciona el Año", años, default=años)

# Filtro de Provincia
provincias = sorted(df['Provincia'].unique())
prov_sel = st.sidebar.multiselect("Selecciona la Provincia", provincias, default=provincias)

# Filtrado del dataframe principal
mask = (df['Año'].isin(año_sel)) & (df['Provincia'].isin(prov_sel))
df_filtrado = df[mask]

# --- DASHBOARD PRINCIPAL ---

# 1. KPIs (Métricas clave)
col1, col2, col3 = st.columns(3)
with col1:
    total_valor = df_filtrado['Valor'].sum()
    st.metric("Total Acumulado", f"{total_valor:,}")
with col2:
    avg_var = df_filtrado['Variación'].mean()
    st.metric("Variación Promedio", f"{avg_var:.2f}%", delta=f"{avg_var:.1f}%")
with col3:
    num_prov = df_filtrado['Provincia'].nunique()
    st.metric("Provincias Analizadas", num_prov)

st.markdown("---")

# 2. Gráficos (Fila 1)
c1, c2 = st.columns(2)

with c1:
    st.subheader("Evolución Temporal")
    fig_line = px.line(df_filtrado, x='Año', y='Valor', color='Provincia', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Distribución por Provincia")
    fig_bar = px.bar(df_filtrado, x='Provincia', y='Valor', color='Año', barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)

# 3. Mapa Interactivo (Fila 2)
st.subheader("📍 Ubicación Geográfica")
if not df_filtrado.empty:
    fig_map = px.scatter_mapbox(
        df_filtrado, 
        lat="Lat", lon="Lon", 
        size="Valor", color="Provincia",
        hover_name="Provincia", size_max=15, zoom=7,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No hay datos para mostrar en el mapa con los filtros seleccionados.")