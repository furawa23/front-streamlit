import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. SETUP DE PÁGINA (LOOK PROFESIONAL)
st.set_page_config(page_title="EPS Operations | Control Center", layout="wide", page_icon="💧")

# 2. HACK DE DISEÑO (CSS INJECTION)
st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 95%;}
        
        /* Estilo de Tarjetas KPI */
        .kpi-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-left: 6px solid #1E88E5;
            margin-bottom: 10px;
        }
        .kpi-title { color: #6c757d; font-size: 0.9rem; font-weight: 600; margin-bottom: 5px; }
        .kpi-value { color: #212529; font-size: 1.8rem; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# 3. LÓGICA DE DATOS (LEER LO QUE PROCESASTE EN COLAB)
@st.cache_data
def load_data():
    # Usamos el dataset de ejemplo que enviaste
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['duracion_horas'] = df['duracion_horas'].fillna(0)
        df['impacto'] = df['impacto'].fillna(0)
        return df
    return pd.DataFrame()

df = load_data()

# 4. HEADER Y FILTROS
st.title("🛡️ Centro de Control Operativo - SUNASS Datathon")
st.markdown("Plataforma de monitoreo de incidencias y optimización de respuesta técnica.")

if not df.empty:
    with st.sidebar:
        st.header("⚙️ Configuración")
        eps = st.multiselect("Seleccionar EPS", df['empresa'].unique(), default=df['empresa'].unique())
        filtro_df = df[df['empresa'].isin(eps)]

    # 5. KPIs PERSONALIZADOS (ESTILO POWER BI)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>HORAS TOTALES CORTE</div><div class='kpi-value'>{filtro_df['duracion_horas'].sum():,.0f} h</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='kpi-card' style='border-left-color: #FFA000;'><div class='kpi-title'>POBLACIÓN AFECTADA</div><div class='kpi-value'>{filtro_df['impacto'].sum():,.0f}</div></div>""", unsafe_allow_html=True)
    with c3:
        roturas = len(df[df['motivo'] == 'Rotura'])
        st.markdown(f"""<div class='kpi-card' style='border-left-color: #D32F2F;'><div class='kpi-title'>ROTURAS DE TUBERÍA</div><div class='kpi-value'>{roturas}</div></div>""", unsafe_allow_html=True)
    with c4:
        estaciones = filtro_df['estacion_id'].nunique()
        st.markdown(f"""<div class='kpi-card' style='border-left-color: #388E3C;'><div class='kpi-title'>ESTACIONES ACTIVAS</div><div class='kpi-value'>{estaciones}</div></div>""", unsafe_allow_html=True)

    st.markdown("###")

    # 6. VISUALIZACIÓN DE DATOS
    col_map, col_chart = st.columns([1.5, 1])
    
    with col_map:
        st.subheader("📍 Ubicación de Incidentes Críticos")
        # Aquí usarías lat/lon si los procesaste en Colab. Si no, un gráfico de áreas.
        fig_bar = px.bar(filtro_df, x="estacion_id", y="duracion_horas", color="motivo", barmode="group", template="plotly_white")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart:
        st.subheader("📊 Impacto por Motivo")
        fig_pie = px.pie(filtro_df, values='impacto', names='motivo', hole=0.5)
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 7. EL SIMULADOR (EL DIFERENCIADOR PARA GANAR)
    st.markdown("---")
    st.subheader("💡 Simulador de Mejora Operacional")
    
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        mejora = st.slider("Mejora en tiempo de atención (%)", 0, 100, 20)
    
    with col_s2:
        horas_ahorradas = filtro_df['duracion_horas'].sum() * (mejora/100)
        st.success(f"Con una mejora del {mejora}%, se recuperarían **{horas_ahorradas:,.1f} horas** de servicio para la población.")

else:
    st.warning("⚠️ Sube el archivo 'dataset_r.csv' a la carpeta 'data/' para activar el dashboard.")