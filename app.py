import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Centro de Comando EPS", layout="wide", page_icon="💧")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #e9ecef;
        padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS (Simulando el Colab) ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['duracion_horas'] = df['duracion_horas'].fillna(0)
        df['impacto'] = df['impacto'].fillna(0)
        return df
    else:
        return pd.DataFrame()

df = load_data()

# --- 3. INTERFAZ PRINCIPAL ---
if not df.empty:
    # Sidebar: Filtros Operativos
    st.sidebar.image("https://www.sunass.gob.pe/wp-content/uploads/2020/10/logo-sunass.png", width=200)
    st.sidebar.title("Filtros Operativos")
    
    eps_seleccionada = st.sidebar.multiselect("Seleccionar EPS", df['empresa'].unique(), default=df['empresa'].unique())
    motivo_seleccionado = st.sidebar.multiselect("Tipo de Incidente", df['motivo'].unique(), default=df['motivo'].unique())
    
    # Aplicar filtros
    df_filtrado = df[(df['empresa'].isin(eps_seleccionada)) & (df['motivo'].isin(motivo_seleccionado))]
    
    # Título del Dashboard
    st.title("💧 Centro de Monitoreo Operacional de Saneamiento")
    st.markdown("Visualización estratégica de interrupciones del servicio e impacto poblacional.")
    
    # Crear Pestañas
    tab1, tab2 = st.tabs(["🗺️ Monitoreo de Red en Tiempo Real", "⚙️ Simulador de Decisiones (Datathon)"])
    
    # --- PESTAÑA 1: MONITOREO ---
    with tab1:
        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        total_horas = df_filtrado['duracion_horas'].sum()
        total_poblacion = df_filtrado['impacto'].sum()
        incidentes_rotura = len(df_filtrado[df_filtrado['motivo'] == 'Rotura'])
        
        c1.metric("Horas Totales de Corte", f"{total_horas:,.1f} h")
        c2.metric("Población Afectada", f"{total_poblacion:,.0f} hab")
        c3.metric("Fugas / Roturas Críticas", incidentes_rotura, delta="Pérdida Física", delta_color="inverse")
        c4.metric("Estaciones Afectadas", df_filtrado['estacion_id'].nunique())
        
        st.markdown("---")
        
        # Gráficos de Análisis
        col_mapa, col_graficos = st.columns([2, 1.5])
        
        with col_mapa:
            st.subheader("📍 Mapeo de Incidencias Físicas")
            fig_map = px.scatter_mapbox(
                df_filtrado, lat="latitud", lon="longitud", size="impacto", 
                color="motivo", hover_name="estacion_id", hover_data=["duracion_horas"],
                zoom=7, mapbox_style="carto-positron", height=500,
                color_discrete_map={"Rotura": "red", "Emergencia": "orange", "Mantenimiento": "blue", "Programado": "green"}
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
        with col_graficos:
            st.subheader("📊 Horas Perdidas por EPS")
            fig_bar = px.bar(
                df_filtrado.groupby('empresa')['duracion_horas'].sum().reset_index(),
                x='empresa', y='duracion_horas', text_auto='.2s', color='empresa'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.subheader("📈 Evolución de Cortes")
            fig_line = px.line(
                df_filtrado.sort_values('fecha'), x='fecha', y='duracion_horas', 
                color='motivo', markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # --- PESTAÑA 2: SIMULADOR (LA CARTA GANADORA) ---
    with tab2:
        st.header("Simulador de Impacto: Reducción de Agua No Facturada (ANF)")
        st.info("💡 **Caso de Uso:** ¿Qué pasaría si la EPS invierte en mejorar sus tiempos de respuesta para reparar 'Roturas' (fugas)?")
        
        col_slider, col_resultados = st.columns([1, 2])
        
        with col_slider:
            st.markdown("### 🔧 Parámetros de Simulación")
            mejora_porcentaje = st.slider(
                "Reducción en tiempo de respuesta a Roturas (%)", 
                min_value=0, max_value=50, value=20, step=5
            )
            
            # Cálculo de simulación
            df_roturas = df_filtrado[df_filtrado['motivo'] == 'Rotura'].copy()
            horas_originales_rotura = df_roturas['duracion_horas'].sum()
            horas_ahorradas = horas_originales_rotura * (mejora_porcentaje / 100)
            
        with col_resultados:
            st.markdown("### 🎯 Impacto Operacional Proyectado")
            
            res1, res2 = st.columns(2)
            res1.metric(
                "Horas de Servicio Recuperadas", 
                f"+ {horas_ahorradas:,.1f} horas", 
                delta=f"Mejora del {mejora_porcentaje}%", 
                delta_color="normal"
            )
            res2.metric(
                "Nuevo Total de Horas Perdidas", 
                f"{(total_horas - horas_ahorradas):,.1f} horas",
                delta=f"- {horas_ahorradas:,.1f} horas",
                delta_color="inverse"
            )
            
            st.success(f"**Conclusión para el Jurado:** Reducir el tiempo de atención de roturas en un {mejora_porcentaje}% recuperaría **{horas_ahorradas:,.1f} horas** de continuidad del servicio para la población de la región, impactando directamente en la reducción del Índice de Agua No Facturada.")

else:
    st.error("No se encontró el archivo de datos. Asegúrate de tener 'dataset_r.csv' en la carpeta 'data/'.")