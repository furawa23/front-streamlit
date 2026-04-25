import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN Y DISEÑO ---
st.set_page_config(page_title="Control Operativo EPS", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        header {visibility: hidden;} footer {visibility: hidden;}
        .metric-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #2563EB; margin-bottom: 15px;}
        .metric-title { color: #64748B; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
        .metric-value { color: #1E293B; font-size: 1.8rem; font-weight: 700; }
        .insight-box { background-color: #EFF6FF; border-left: 5px solid #3B82F6; padding: 15px; border-radius: 8px; margin-top: 10px; font-size: 0.95rem; }
        .alert-box { background-color: #FEF2F2; border-left: 5px solid #EF4444; padding: 15px; border-radius: 8px; margin-top: 10px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE DATOS SEGURA ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        # Aseguramos que existan columnas numéricas para evitar errores
        if 'costo_reparacion' not in df.columns: df['costo_reparacion'] = 0
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- FILTROS LATERALES ---
    with st.sidebar:
        st.markdown("### 🎛️ Filtros de Red")
        sel_empresa = st.selectbox("Seleccionar EPS", ["TODAS"] + list(df['empresa'].unique()))
        sel_motivo = st.multiselect("Tipo de Falla", df['motivo'].unique(), default=df['motivo'].unique())

    # Aplicar filtros
    df_f = df.copy()
    if sel_empresa != "TODAS": df_f = df_f[df_f['empresa'] == sel_empresa]
    df_f = df_f[df_f['motivo'].isin(sel_motivo)]

    # --- CABECERA ---
    st.title("💧 Tablero de Inteligencia Operacional")
    st.markdown("Visión integral del estado de la red de agua potable y saneamiento.")

    # --- 3. KPIs PRINCIPALES ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f"<div class='metric-card'><div class='metric-title'>Horas Perdidas</div><div class='metric-value'>{df_f['duracion_horas'].sum():,.1f} h</div></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='metric-card' style='border-top-color: #F59E0B;'><div class='metric-title'>Población Afectada</div><div class='metric-value'>{df_f['impacto'].sum():,.0f}</div></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='metric-card' style='border-top-color: #EF4444;'><div class='metric-title'>Total de Incidentes</div><div class='metric-value'>{len(df_f)}</div></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div class='metric-card' style='border-top-color: #10B981;'><div class='metric-title'>Costo Reparaciones</div><div class='metric-value'>S/. {df_f['costo_reparacion'].sum():,.0f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 4. PANEL DE GRÁFICOS SIMPLES Y DIRECTOS ---
    
    # FILA 1: Top Instalaciones y Distribución de Causas
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("1. Instalaciones con mayor tiempo de falla (Top 5)")
        df_top = df_f.groupby('estacion_id')['duracion_horas'].sum().nlargest(5).reset_index()
        fig_bar = px.bar(df_top, x='duracion_horas', y='estacion_id', orientation='h', text_auto='.1f', color='duracion_horas', color_continuous_scale='Reds')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.subheader("2. Proporción de Causas")
        fig_pie = px.pie(df_f, names='motivo', values='duracion_horas', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Interpretación Automática de Causa Principal
        causa_principal = df_f.groupby('motivo')['duracion_horas'].sum().idxmax()
        st.markdown(f"<div class='insight-box'><b>💡 Diagnóstico:</b> El principal motivo de cortes en la red es <b>{causa_principal}</b>. Sugerimos redirigir el 40% del presupuesto de mantenimiento a prevenir este factor.</div>", unsafe_allow_html=True)

    # FILA 2: Tendencia en el Tiempo y Matriz de Riesgo
    st.markdown("###")
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("3. Evolución de Cortes en el Tiempo")
        df_time = df_f.groupby('fecha')['duracion_horas'].sum().reset_index()
        fig_line = px.line(df_time, x='fecha', y='duracion_horas', markers=True, line_shape='spline')
        fig_line.update_traces(line_color='#2563EB', line_width=3, marker=dict(size=8))
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with c4:
        st.subheader("4. Matriz de Gravedad (Impacto vs Tiempo)")
        # Un scatter plot simple. Arriba a la derecha es PELIGRO.
        fig_scatter = px.scatter(df_f, x='duracion_horas', y='impacto', color='motivo', size='duracion_horas', hover_name='estacion_id')
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Horas que duró el corte", yaxis_title="Personas afectadas")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Interpretación de Outliers (Puntos Peligrosos)
        incidentes_graves = len(df_f[(df_f['duracion_horas'] > 12) & (df_f['impacto'] > 1000)])
        if incidentes_graves > 0:
            st.markdown(f"<div class='alert-box'><b>🚨 Alerta Crítica:</b> Existen <b>{incidentes_graves} incidentes graves</b> (alta duración y alto impacto poblacional) ubicados en la parte superior derecha del gráfico. Revisar estas estaciones urgentemente.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='insight-box'>✅ No hay incidentes en la zona crítica (alta duración + alto impacto).</div>", unsafe_allow_html=True)

    # --- 5. EL SIMULADOR DE IMPACTO ---
    st.markdown("---")
    st.header("⚙️ Simulador de Recuperación y Ahorro (Proyecciones)")
    st.write("Ajuste los parámetros para simular cómo una inversión en logística impacta a la EPS.")
    
    col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
    
    with col_s1:
        st.markdown("#### Ajuste de Variables")
        mejora_fugas = st.slider("Reducción de Roturas/Fugas (%)", 0, 50, 15)
        mejora_tiempo = st.slider("Mejora en tiempos de atención (%)", 0, 50, 20)
    
    with col_s2:
        st.markdown("#### Horas y Personas Recuperadas")
        # Cálculos de simulación
        horas_originales = df_f['duracion_horas'].sum()
        pob_original = df_f['impacto'].sum()
        
        horas_salvadas = horas_originales * (mejora_tiempo / 100)
        pob_salvada = pob_original * (mejora_fugas / 100)
        
        st.metric("Horas de Servicio Recuperadas", f"+ {horas_salvadas:,.1f} h", delta="Aumento de continuidad")
        st.metric("Población no afectada", f"+ {pob_salvada:,.0f} hab", delta="Mejora en calidad de vida")

    with col_s3:
        st.markdown("#### Impacto Económico")
        # Simulando que el costo de reparación se reduce al haber menos fugas y menos tiempo
        costo_original = df_f['costo_reparacion'].sum()
        ahorro_estimado = costo_original * (mejora_fugas / 100) + (horas_salvadas * 50) # Simulación S/50 por hora
        
        st.metric("Ahorro Estimado Operativo", f"S/. {ahorro_estimado:,.0f}", delta="Presupuesto liberado")
        
        st.markdown(f"<div class='insight-box'><b>Conclusión para el Jurado:</b> Con estas medidas, la EPS ahorraría <b>S/. {ahorro_estimado:,.0f}</b> que pueden ser reinvertidos en ampliar la red de micromedición.</div>", unsafe_allow_html=True)

else:
    st.error("No se han cargado los datos. Revisa la carpeta data/")