import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN Y CSS (Mantén lo que ya tenías) ---
st.set_page_config(page_title="EPS Operational Intelligence", layout="wide")

st.markdown("""
    <style>
        /* ... (TU CSS AQUI) ... */
        .metric-card { background-color: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; margin-bottom: 20px; }
        .metric-label { color: #64748B; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; }
        .metric-value { color: #1E293B; font-size: 2rem; font-weight: 700; margin-top: 8px; }
        .metric-delta { font-size: 0.875rem; font-weight: 500; margin-top: 4px; }
        .insight-card { background-color: #EFF6FF; border-left: 6px solid #2563EB; padding: 20px; border-radius: 12px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    return pd.DataFrame()

df = load_data()

# --- 3. VALIDACIÓN Y RENDERIZADO DEL DASHBOARD ---
# AQUÍ ESTÁ LA CORRECCIÓN: Todo va dentro de este IF
if not df.empty:
    
    # LÓGICA DE FILTROS ESTILO "CARDS" EN SIDEBAR
    with st.sidebar:
        st.markdown("### 🔍 Filtros Estratégicos")
        empresa_list = ["TODAS"] + list(df['empresa'].unique())
        sel_empresa = st.selectbox("Seleccionar Entidad EPS", empresa_list)
        
        st.markdown("---")
        sel_motivo = st.multiselect("Motivo de Incidencia", df['motivo'].unique(), default=df['motivo'].unique())

    # Filtrar Datos
    df_f = df.copy()
    if sel_empresa != "TODAS":
        df_f = df_f[df_f['empresa'] == sel_empresa]
    df_f = df_f[df_f['motivo'].isin(sel_motivo)]

    # LAYOUT PRINCIPAL
    st.title("🛡️ Sistema de Inteligencia Operacional")
    st.markdown(f"Análisis detallado de continuidad y pérdidas físicas para **{sel_empresa}**")

    # 1. FILA DE KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        val = df_f['duracion_horas'].sum()
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Horas de Corte</div><div class='metric-value'>{val:,.1f}</div><div class='metric-delta' style='color:#EF4444;'>Impacto Crítico</div></div>", unsafe_allow_html=True)
    with k2:
        val = df_f['impacto'].sum()
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Población Afectada</div><div class='metric-value'>{val:,.0f}</div><div class='metric-delta' style='color:#F59E0B;'>Usuarios sin servicio</div></div>", unsafe_allow_html=True)
    with k3:
        # Aseguramos que no haya error si no hay columna costo_reparacion
        val = df_f['costo_reparacion'].sum() if 'costo_reparacion' in df_f.columns else 0
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Costo Operativo</div><div class='metric-value'>S/. {val:,.0f}</div><div class='metric-delta' style='color:#2563EB;'>Inversión en Red</div></div>", unsafe_allow_html=True)
    with k4:
        # Aseguramos que no haya error si no hay columna presion_psi
        val = df_f['presion_psi'].mean() if 'presion_psi' in df_f.columns else 0
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Presión Promedio</div><div class='metric-value'>{val:,.1f} PSI</div><div class='metric-delta' style='color:#10B981;'>Estabilidad de Red</div></div>", unsafe_allow_html=True)

    # ... (Aquí va el resto de tu código de gráficos, Pareto y Boxplot, indentado un nivel a la derecha) ...

else:
    # EL MENSAJE SALVAVIDAS
    st.error("⚠️ El archivo de datos no se ha cargado correctamente.")
    st.info("Verifica que el archivo `dataset_r.csv` esté dentro de la carpeta `data/` en GitHub y que el nombre de las columnas sea correcto.")