import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="EPS Command Center | SUNASS", layout="wide")

st.markdown("""
    <style>
        .reportview-container { background: #f0f2f6; }
        .metric-card {
            background-color: white; padding: 20px; border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #007bff;
        }
        .recommendation-box {
            background-color: #e3f2fd; border-left: 5px solid #2196f3;
            padding: 15px; border-radius: 5px; margin-top: 10px;
        }
        .alert-critical { background-color: #ffebee; border-left: 5px solid #f44336; padding: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (Lo que procesas en Colab) ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['hora'] = df['fecha'].dt.hour
        df['dia_semana'] = df['fecha'].dt.day_name()
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SIDEBAR: FILTROS ---
    st.sidebar.title("🎮 Panel de Control")
    sel_eps = st.sidebar.selectbox("Entidad EPS", ["TODAS"] + list(df['empresa'].unique()))
    
    df_f = df.copy()
    if sel_eps != "TODAS":
        df_f = df_f[df_f['empresa'] == sel_eps]

    # --- HEADER ---
    st.title("🛡️ Inteligencia de Operaciones de Saneamiento")
    st.info("Este panel analiza fallos en red y prescribe acciones correctivas inmediatas.")

    # --- 3. KPIs DINÁMICOS ---
    c1, c2, c3, c4 = st.columns(4)
    total_horas = df_f['duracion_horas'].sum()
    avg_impacto = df_f['impacto'].mean()
    
    with c1:
        st.markdown(f"<div class='metric-card'><b>Horas Perdidas</b><br><h2>{total_horas:,.1f}h</h2></div>", unsafe_allow_html=True)
    with c2:
        # KPI con lógica: Si es mucha gente, se pone rojo
        color = "red" if avg_impacto > 1000 else "black"
        st.markdown(f"<div class='metric-card'><b>Impacto Promedio</b><br><h2 style='color:{color}'>{avg_impacto:,.0f} hab</h2></div>", unsafe_allow_html=True)
    with c3:
        costo = df_f['costo_reparacion'].sum() if 'costo_reparacion' in df_f.columns else 0
        st.markdown(f"<div class='metric-card'><b>Costo Operativo</b><br><h2>S/. {costo:,.0f}</h2></div>", unsafe_allow_html=True)
    with c4:
        eficiencia = 100 - (df_f[df_f['motivo']=='Rotura']['duracion_horas'].mean() * 2) # Simulación
        st.markdown(f"<div class='metric-card'><b>Índice Eficiencia</b><br><h2>{max(eficiencia, 0):,.1f}%</h2></div>", unsafe_allow_html=True)

    st.markdown("###")

    # --- 4. ANÁLISIS DE PATRONES TEMPORALES (NUEVO) ---
    col_heat, col_rec = st.columns([2, 1])

    with col_heat:
        st.subheader("🗓️ ¿Cuándo fallan las tuberías? (Análisis de Turnos)")
        # Crear un heatmap de Día vs Hora
        heat_data = df_f.groupby(['dia_semana', 'hora'])['id'].count().reset_index()
        fig_heat = px.density_heatmap(
            heat_data, x="hora", y="dia_semana", z="id",
            labels={'id': 'Frecuencia', 'hora': 'Hora del Día', 'dia_semana': 'Día'},
            color_continuous_scale="Viridis", text_auto=True
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_rec:
        st.subheader("🤖 Plan de Acción Sugerido")
        # MOTOR DE RECOMENDACIONES LÓGICAS
        roturas_criticas = len(df_f[df_f['motivo'] == 'Rotura'])
        horas_promedio = df_f['duracion_horas'].mean()

        if roturas_criticas > 5:
            st.markdown("""<div class='alert-critical'><b>PROBLEMA:</b> Alta incidencia de roturas detectada.<br>
            <b>CAUSA:</b> Posible fatiga de red o picos de presión nocturna.<br>
            <b>ACCIÓN:</b> Implementar válvulas reguladoras en los sectores con Cód ID más altos.</div>""", unsafe_allow_html=True)
        
        if horas_promedio > 12:
            st.markdown("""<div class='recommendation-box'><b>PROBLEMA:</b> Tiempo de respuesta lento (>12h).<br>
            <b>ACCIÓN:</b> Evaluar stock de repuestos en almacenes periféricos. Reducir burocracia en órdenes de trabajo.</div>""", unsafe_allow_html=True)
        else:
            st.success("✅ Los tiempos de respuesta están dentro del rango óptimo de la SUNASS.")

    # --- 5. PARETO DE IMPACTO (¿Dónde duele más?) ---
    st.markdown("### 📊 Priorización de Inversión (Ley 80/20)")
    df_p = df_f.groupby('estacion_id')['impacto'].sum().reset_index().sort_values('impacto', ascending=False)
    df_p['acum'] = (df_p['impacto'].cumsum() / df_p['impacto'].sum()) * 100
    
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=df_p['estacion_id'], y=df_p['impacto'], name="Usuarios Afectados", marker_color='#1E88E5'))
    fig_p.add_trace(go.Scatter(x=df_p['estacion_id'], y=df_p['acum'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
    
    fig_p.update_layout(
        yaxis2=dict(title="Porcentaje Acumulado", overlaying="y", side="right", range=[0, 105]),
        title="Estaciones con mayor impacto ciudadano (Enfoque en estas estaciones primero)",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_p, use_container_width=True)

else:
    st.error("Sube el dataset procesado en Colab para activar las recomendaciones.")