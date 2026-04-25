import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inteligencia Operacional EPS", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .main { background-color: #F8FAFC; }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .metric-card { background-color: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; margin-bottom: 20px; }
        .metric-label { color: #64748B; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; }
        .metric-value { color: #1E293B; font-size: 2rem; font-weight: 700; margin-top: 8px; }
        .metric-delta { font-size: 0.875rem; font-weight: 500; margin-top: 4px; }
        .insight-card { background-color: #EFF6FF; border-left: 6px solid #2563EB; padding: 20px; border-radius: 12px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- CARGA Y TRANSFORMACIÓN DE DATOS (100% DINÁMICO) ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        # Ya NO hay diccionario. Se usa la data pura y dura.
        return df
    return pd.DataFrame()

df = load_data()

# --- VALIDACIÓN ANTICRASH ---
if not df.empty:
    
    # --- FILTROS SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🔍 Filtros de Gestión")
        empresa_list = ["TODAS"] + list(df['empresa'].unique())
        sel_empresa = st.selectbox("Seleccionar EPS", empresa_list)
        st.markdown("---")
        sel_motivo = st.multiselect("Motivo del Corte de Servicio", df['motivo'].unique(), default=df['motivo'].unique())

    # Aplicar filtros dinámicos
    df_f = df.copy()
    if sel_empresa != "TODAS":
        df_f = df_f[df_f['empresa'] == sel_empresa]
    df_f = df_f[df_f['motivo'].isin(sel_motivo)]

    # --- CABECERA PRINCIPAL ---
    st.title("🛡️ Panel de Control: Eficiencia del Servicio de Agua")
    st.markdown("Monitoreo de interrupciones y análisis de instalaciones críticas.")

    # --- KPIs A PRUEBA DE ERRORES ---
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        val = df_f['duracion_horas'].sum() if 'duracion_horas' in df_f.columns else 0
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Horas Totales sin Agua</div><div class='metric-value'>{val:,.1f} h</div><div class='metric-delta' style='color:#EF4444;'>Impacto Directo al Usuario</div></div>", unsafe_allow_html=True)
    with k2:
        val = df_f['impacto'].sum() if 'impacto' in df_f.columns else 0
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Población Afectada</div><div class='metric-value'>{val:,.0f}</div><div class='metric-delta' style='color:#F59E0B;'>Personas sin servicio</div></div>", unsafe_allow_html=True)
    with k3:
        val = f"S/. {df_f['costo_reparacion'].sum():,.0f}" if 'costo_reparacion' in df_f.columns else "Sin Datos"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Gastos de Reparación</div><div class='metric-value'>{val}</div><div class='metric-delta' style='color:#2563EB;'>Costo Operativo</div></div>", unsafe_allow_html=True)
    with k4:
        val = f"{df_f['presion_psi'].mean():,.1f} PSI" if 'presion_psi' in df_f.columns else "Sin Datos"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Presión Promedio</div><div class='metric-value'>{val}</div><div class='metric-delta' style='color:#10B981;'>Estado de la Red</div></div>", unsafe_allow_html=True)

    # --- SECCIÓN GRÁFICOS ---
    st.markdown("### 🔬 ¿Dónde se están originando los problemas?")
    c_left, c_right = st.columns([2, 1])

    with c_left:
        # GRÁFICO 80/20 usando el ID crudo
        df_p = df_f.groupby('estacion_id')['duracion_horas'].sum().reset_index().sort_values('duracion_horas', ascending=False)
        df_p['acum'] = (df_p['duracion_horas'].cumsum() / df_p['duracion_horas'].sum()) * 100
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Formateamos ligeramente el texto del eje X para que diga "Cód: [ID]"
        nombres_eje_x = ["Cód: " + str(x) for x in df_p['estacion_id']]
        
        fig.add_trace(go.Bar(x=nombres_eje_x, y=df_p['duracion_horas'], name="Horas de Corte", marker_color='#3B82F6'), secondary_y=False)
        fig.add_trace(go.Scatter(x=nombres_eje_x, y=df_p['acum'], name="% Acumulado (Regla 80/20)", line=dict(color='#EF4444', width=3)), secondary_y=True)
        
        fig.update_layout(
            title="Instalaciones Críticas: Concentración de horas sin servicio (Análisis 80/20)", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450,
            xaxis_title="Código de la Instalación",
            yaxis_title="Horas Totales Perdidas"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        # INTERPRETACIÓN MÁS CLARA Y DINÁMICA
        st.markdown("#### 🤖 Conclusión Automática")
        
        if not df_p.empty:
            peor_estacion = df_p.iloc[0]['estacion_id']
            total_horas = df_f['duracion_horas'].sum()
            pct_peor = (df_p.iloc[0]['duracion_horas'] / total_horas) * 100
            
            st.markdown(f"""
                <div class='insight-card'>
                    <p><b>El Foco de Atención:</b> Notamos que la instalación con el código <b>{peor_estacion}</b> es la responsable del <b>{pct_peor:.1f}%</b> de todo el tiempo que la población pasa sin agua.</p>
                    <p><b>Por qué es útil este gráfico:</b> La línea roja nos muestra qué tan rápido se acumulan los problemas. Si reparamos las instalaciones ubicadas más a la izquierda, solucionaremos la gran mayoría de los cortes de servicio usando menos presupuesto.</p>
                </div>
            """, unsafe_allow_html=True)

    # --- SECCIÓN BOXPLOT ---
    st.markdown("### 📊 ¿Qué tan eficientes somos reparando?")
    c1, c2 = st.columns([1.5, 1])

    with c1:
        fig_box = px.box(df_f, x="motivo", y="duracion_horas", color="empresa", points="all")
        fig_box.update_layout(
            title="Dispersión de los tiempos que toman las cuadrillas para resolver problemas",
            xaxis_title="Tipo de Incidencia",
            yaxis_title="Horas que tomó la reparación",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with c2:
        st.markdown("#### ¿Cómo leer este diagrama?")
        st.info("Las **cajas de colores** muestran el tiempo 'normal' que nos toma reparar las incidencias. Los **puntos sueltos que están muy arriba** representan reparaciones que tomaron demasiado tiempo. Nuestro objetivo operativo es que las cajas sean lo más planas posibles.")
        
        st.markdown("---")
        st.subheader("⚙️ Simulador de Impacto")
        mejora = st.slider("Si las cuadrillas fueran un % más rápidas:", 0, 50, 20)
        horas_recup = df_f['duracion_horas'].sum() * (mejora/100)
        st.success(f"Lograríamos devolverle **{horas_recup:,.1f} horas** de agua continua a la comunidad.")

else:
    st.error("⚠️ No se encontraron datos para procesar.")
    st.info("Asegúrate de que el archivo `dataset_r.csv` esté en la carpeta `data/`.")