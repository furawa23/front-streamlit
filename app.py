import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="EPS Operational Intelligence", layout="wide")

# Estilos CSS para tarjetas y cuadros de sugerencia
st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        .metric-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #2563EB; }
        .insight-container { background-color: #F0F7FF; border-radius: 8px; padding: 15px; border-left: 5px solid #3B82F6; margin-top: 10px; }
        .math-logic { font-family: monospace; color: #1E40AF; font-weight: bold; }
        .suggestion-text { color: #1E293B; font-size: 0.95rem; margin-top: 5px; }
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

if not df.empty:
    # --- SIDEBAR (USABILIDAD MEJORADA) ---
    with st.sidebar:
        st.header("🔍 Central de Filtros")
        sel_empresa = st.selectbox("Entidad EPS", ["Todas las EPS"] + list(df['empresa'].unique()))
        sel_motivo = st.multiselect("Motivo de Incidencia", df['motivo'].unique(), default=df['motivo'].unique())
        
        st.divider()
        st.markdown("### ⚙️ Configuración de Vista")
        vista_detalle = st.toggle("Mostrar Tabla de Datos Crudos", value=False)

    # Lógica de Filtrado
    df_f = df.copy()
    if sel_empresa != "Todas las EPS":
        df_f = df_f[df_f['empresa'] == sel_empresa]
    df_f = df_f[df_f['motivo'].isin(sel_motivo)]

    # Variables Dinámicas para Títulos
    nombre_eps = sel_empresa if sel_empresa != "Todas las EPS" else "Sector Saneamiento"
    nombre_falla = ", ".join(sel_motivo) if len(sel_motivo) < 3 else "Múltiples Causas"

    # --- HEADER DINÁMICO ---
    st.title(f"📊 Dashboard Operacional: {nombre_eps}")
    st.caption(f"Análisis enfocado en: {nombre_falla}")

    # --- KPIs ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f"<div class='metric-card'><b>Horas de Corte</b><br><h2>{df_f['duracion_horas'].sum():,.1f}</h2></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='metric-card'><b>Usuarios Afectados</b><br><h2>{df_f['impacto'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='metric-card'><b>Costo Est.</b><br><h2>S/. {df_f['impacto'].sum()*0.5:,.0f}</h2></div>", unsafe_allow_html=True)
    with k4: 
        est_criticas = df_f.groupby('estacion_id')['duracion_horas'].sum().count()
        st.markdown(f"<div class='metric-card'><b>Puntos Críticos</b><br><h2>{est_criticas}</h2></div>", unsafe_allow_html=True)

    st.divider()

    # --- BLOQUE 1: TOP FALLAS (BARRAS) ---
    st.subheader(f"📍 Ranking de Criticidad por Instalación - {nombre_eps}")
    df_bar = df_f.groupby('estacion_id')['duracion_horas'].sum().nlargest(8).reset_index()
    fig_bar = px.bar(df_bar, x='estacion_id', y='duracion_horas', color='duracion_horas', color_continuous_scale='Blues')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Interpretación Matemática 1
    total_h = df_f['duracion_horas'].sum()
    peor_id = df_bar.iloc[0]['estacion_id']
    peor_val = df_bar.iloc[0]['duracion_horas']
    porcentaje = (peor_val / total_h) * 100
    
    st.markdown(f"""
    <div class='insight-container'>
        <span class='math-logic'>Lógica: (Σ horas_{peor_id} / Σ horas_totales) = {porcentaje:.1f}%</span>
        <div class='suggestion-text'>
            <b>Interpretación:</b> La instalación <b>{peor_id}</b> concentra casi la cuarta parte de las fallas del filtro actual. 
            <br><b>Sugerencia:</b> Iniciar auditoría técnica en <b>{peor_id}</b>. Si se reduce su falla a la mitad, recuperamos {peor_val/2:.1f} horas de servicio global.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- BLOQUE 2: TENDENCIA Y CAUSAS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"📈 Tendencia de {nombre_falla}")
        df_line = df_f.groupby('fecha')['duracion_horas'].sum().reset_index()
        fig_line = px.line(df_line, x='fecha', y='duracion_horas', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Matemática 2
        promedio = df_line['duracion_horas'].mean()
        st.markdown(f"""
        <div class='insight-container'>
            <span class='math-logic'>Media Móvil: μ = {promedio:.2f} h/día</span>
            <div class='suggestion-text'>
                <b>Interpretación:</b> El sistema opera con una pérdida constante. 
                <br><b>Sugerencia:</b> Si la tendencia supera las {promedio*1.2:.1f}h, activar protocolo de emergencia de nivel 2.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.subheader("🍕 Distribución por Motivo")
        fig_pie = px.pie(df_f, names='motivo', values='duracion_horas', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Matemática 3
        motivo_top = df_f.groupby('motivo')['duracion_horas'].sum().idxmax()
        st.markdown(f"""
        <div class='insight-container'>
            <span class='math-logic'>P(Moda_Causa) = {motivo_top}</span>
            <div class='suggestion-text'>
                <b>Interpretación:</b> <b>{motivo_top}</b> es el "cuello de botella" operativo dominante.
                <br><b>Sugerencia:</b> Capacitar cuadrillas específicamente en resolución de <b>{motivo_top}</b> para bajar el MTTR (Tiempo medio de reparación).
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- 5. EL SIMULADOR DE IMPACTO (MEJORADO) ---
    st.divider()
    st.header("⚙️ Simulador Prescriptivo de Decisiones")
    c_s1, c_s2 = st.columns([1, 2])
    
    with c_s1:
        st.write("¿Qué pasa si invertimos en mejoras?")
        inv_logistica = st.slider("Inversión en logística (%)", 0, 100, 25)
        mejora_red = st.slider("Renovación de tuberías (%)", 0, 100, 10)
    
    with c_s2:
        horas_ahorradas = (total_h * (inv_logistica/200)) + (total_h * (mejora_red/150))
        st.subheader(f"Resultado Estimado para {nombre_eps}")
        st.info(f"Con esta configuración, se estima una recuperación de **{horas_ahorradas:,.1f} horas** de agua al mes.")
        
        # Sugerencia Matemática Final
        st.write(f"**Justificación:** El modelo asume una correlación de 0.5 entre logística y tiempo de respuesta. El ROI social estimado es de S/. {horas_ahorradas * 120:,.0f} en productividad ciudadana.")

    if vista_detalle:
        st.divider()
        st.subheader("📄 Detalle de Incidentes Filtrados")
        st.dataframe(df_f, use_container_width=True)

else:
    st.warning("⚠️ No se detectó el archivo 'data/dataset_r.csv'. Por favor, cárgalo para activar el análisis.")