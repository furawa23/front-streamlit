import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="EPS Operational & Financial Intelligence", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .main { background-color: #F1F5F9; }
        header {visibility: hidden;} footer {visibility: hidden;}
        .card-calc { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-bottom: 5px solid #10B981; text-align: center; }
        .money-value { color: #059669; font-size: 2.2rem; font-weight: 800; }
        .calc-label { color: #64748B; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; }
        .logic-container { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; }
        .formula-tag { background-color: #DBEAFE; color: #1E40AF; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-weight: bold; font-size: 0.9rem; }
        .action-tag { background-color: #FEF3C7; color: #92400E; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9rem; }
        .highlight-calc { background-color: #FFF7ED; font-weight: bold; color: #C2410C; padding: 2px 4px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE DATOS Y LIMPIEZA CRÍTICA ---
@st.cache_data
def load_data():
    ruta = 'data/DataLimpia.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['duracion_horas'] = pd.to_numeric(df['duracion_horas'], errors='coerce').fillna(0)
        df['impacto'] = pd.to_numeric(df['impacto'], errors='coerce').fillna(0)
        
        # Generar costos si no existen
        if 'costo_reparacion' not in df.columns:
            df['costo_reparacion'] = (df['duracion_horas'] * 150) + 500
        else:
            df['costo_reparacion'] = pd.to_numeric(df['costo_reparacion'], errors='coerce').fillna(0)
            
        return df
    return pd.DataFrame()

df = load_data()

# --- 3. LÓGICA DE FILTROS ---
if not df.empty:
    with st.sidebar:
        st.header("⚙️ Parámetros")
        eps_list = ["Todas las EPS"] + sorted(list(df['empresa'].unique()))
        sel_eps = st.selectbox("Entidad seleccionada", eps_list)
        
        motivos_disponibles = sorted(list(df['motivo'].unique()))
        sel_motivos = st.multiselect("Tipos de Incidencia", motivos_disponibles, default=motivos_disponibles)

    # Filtrado
    df_f = df.copy()
    if sel_eps != "Todas las EPS":
        df_f = df_f[df_f['empresa'] == sel_eps]
    df_f = df_f[df_f['motivo'].isin(sel_motivos)]

    # --- CONTROL ANTICRASH ---
    if df_f.empty:
        st.warning("⚠️ No hay datos con los filtros actuales. Por favor, selecciona al menos un Motivo.")
        st.stop()

    # --- 4. HEADER Y KPIs ---
    contexto = f"en {sel_eps}" if sel_eps != "Todas las EPS" else "Regional"
    st.title(f"🚀 Monitor de Inteligencia Operativa: {contexto}")

    c1, c2, c3 = st.columns(3)
    total_costo = df_f['costo_reparacion'].sum()
    total_horas = df_f['duracion_horas'].sum()
    total_pob = df_f['impacto'].sum()
    
    with c1: st.markdown(f"<div class='card-calc'><div class='calc-label'>Costo Operativo</div><div class='money-value'>S/. {total_costo:,.0f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card-calc' style='border-bottom-color: #3B82F6;'><div class='calc-label'>Servicio Perdido</div><div class='money-value' style='color:#1D4ED8;'>{total_horas:,.1f} h</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='card-calc' style='border-bottom-color: #F59E0B;'><div class='calc-label'>Impacto Total</div><div class='money-value' style='color:#B45309;'>{total_pob:,.0f} hab</div></div>", unsafe_allow_html=True)

    st.divider()

    # --- 5. GRÁFICOS ANALÍTICOS ---
    
    # BLOQUE 1: PARETO 80/20 (Instalaciones Críticas)
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.subheader("📍 Análisis 80/20: Instalaciones con Mayor Desgaste")
        df_p = df_f.groupby('estacion_id')['duracion_horas'].sum().reset_index().sort_values('duracion_horas', ascending=False)
        df_p['acum'] = (df_p['duracion_horas'].cumsum() / df_p['duracion_horas'].sum()) * 100
        
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pareto.add_trace(go.Bar(x=df_p['estacion_id'], y=df_p['duracion_horas'], name="Horas Perdidas", marker_color='#3B82F6'), secondary_y=False)
        fig_pareto.add_trace(go.Scatter(x=df_p['estacion_id'], y=df_p['acum'], name="% Acumulado", line=dict(color='#EF4444', width=3)), secondary_y=True)
        fig_pareto.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_pareto, use_container_width=True)

    with col_p2:
        st.markdown("### 🔍 Regla de Pareto")
        try:
            top_id = df_p.iloc[0]['estacion_id']
            pct_horas = (df_p.iloc[0]['duracion_horas'] / total_horas * 100)
            
            st.markdown(f"""
            <div class='logic-container'>
                <span class='formula-tag'>Lógica: (Max_Horas / Total_Horas)</span>
                <p class='suggestion-text'>
                    La instalación <b>{top_id}</b> es el "cuello de botella", acaparando el <span class='highlight-calc'>{pct_horas:.1f}%</span> de todo el tiempo de falla.
                    <br><br><span class='action-tag'>PRESCRIPCIÓN:</span> Auditar válvulas y presiones en esta estación específica. Atacar la barra más alta resuelve casi la mitad del problema.
                </p>
            </div>
            """, unsafe_allow_html=True)
        except: st.info("Datos insuficientes para Pareto.")

    st.divider()

    # BLOQUE 2: TENDENCIA Y DISTRIBUCIÓN
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("📈 Tendencia Temporal de Fallas")
        df_time = df_f.groupby('fecha')['duracion_horas'].sum().reset_index()
        fig_line = px.line(df_time, x='fecha', y='duracion_horas', markers=True, line_shape='spline')
        fig_line.update_traces(line_color='#10B981', line_width=3)
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with col_t2:
        st.subheader("🍕 Distribución de Costos por Motivo")
        fig_pie = px.pie(df_f, names='motivo', values='costo_reparacion', hole=0.4)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

    # BLOQUE 3: BOXPLOT DE EFICIENCIA OPERATIVA
    st.divider()
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        st.subheader("📊 Eficiencia de Cuadrillas: Dispersión de Tiempos")
        fig_box = px.box(df_f, x="motivo", y="duracion_horas", color="empresa", points="all")
        fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Horas de Reparación")
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_b2:
        st.markdown("### ⏱️ Análisis de Tiempos")
        try:
            media_h = df_f['duracion_horas'].mean()
            casos_outliers = len(df_f[df_f['duracion_horas'] > (media_h * 1.5)])
            st.markdown(f"""
            <div class='logic-container'>
                <span class='formula-tag'>Umbral Outlier: > {media_h*1.5:.1f}h (1.5x Media)</span>
                <p class='suggestion-text'>
                    El tiempo promedio es de {media_h:.1f}h. Sin embargo, los puntos altos del gráfico revelan <span class='highlight-calc'>{casos_outliers} incidentes anómalos</span>.
                    <br><br><span class='action-tag'>PRESCRIPCIÓN LOGÍSTICA:</span> La gran variabilidad (cajas altas) indica falta de estandarización en repuestos. Se requiere descentralizar el almacén.
                </p>
            </div>
            """, unsafe_allow_html=True)
        except: pass

    # --- 6. SIMULADOR DE IMPACTO (EL CIERRE) ---
    st.divider()
    st.header("⚙️ Simulador Prescriptivo de Retorno (ROI)")
    s1, s2, s3 = st.columns(3)
    
    with s1:
        st.write("### 🛠️ Parámetros")
        mejora = st.slider("Mejora en Tiempo de Respuesta (%)", 0, 100, 20)
    with s2:
        st.write("### 🎯 Impacto Social")
        horas_recup = total_horas * (mejora/100)
        st.metric("Horas Recuperadas", f"+{horas_recup:,.1f} h", delta="Aumento de Continuidad")
    with s3:
        st.write("### 💰 Impacto Económico")
        ahorro = (total_costo * 0.15) * (mejora/100) # Lógica simulada
        st.markdown(f"<div class='card-calc' style='border-bottom-color: #059669; padding: 15px;'>", unsafe_allow_html=True)
        st.markdown(f"<div class='calc-label'>Ahorro Potencial Mensual</div><div class='money-value' style='font-size:1.8rem'>S/. {ahorro:,.0f}</div></div>", unsafe_allow_html=True)

else:
    st.error("Archivo no encontrado. Verifica la ruta 'data/dataset_r.csv'.")