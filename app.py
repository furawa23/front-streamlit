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
        .card-calc {
            background-color: white; padding: 25px; border-radius: 15px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            border-bottom: 5px solid #10B981; text-align: center;
        }
        .money-value { color: #059669; font-size: 2.2rem; font-weight: 800; }
        .calc-label { color: #64748B; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; }
        .logic-container { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; }
        .formula-tag { background-color: #DBEAFE; color: #1E40AF; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-weight: bold; font-size: 0.9rem; }
        .action-tag { background-color: #FEF3C7; color: #92400E; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9rem; }
        .highlight-calc { background-color: #FFF7ED; font-weight: bold; color: #C2410C; padding: 2px 4px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE DATOS CON LIMPIEZA ---
@st.cache_data
def load_data():
    ruta = 'data/resultados.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        df['fecha'] = pd.to_datetime(df['fecha'])
        # LIMPIEZA CRÍTICA: Rellenar nulos para evitar errores en cálculos
        df['duracion_horas'] = pd.to_numeric(df['duracion_horas'], errors='coerce').fillna(0)
        df['impacto'] = pd.to_numeric(df['impacto'], errors='coerce').fillna(0)
        
        if 'costo_reparacion' not in df.columns:
            df['costo_reparacion'] = (df['duracion_horas'] * 150) + 500
        else:
            df['costo_reparacion'] = pd.to_numeric(df['costo_reparacion'], errors='coerce').fillna(0)
            
        if 'presion_psi' not in df.columns:
            df['presion_psi'] = 25 # Valor base simulado
            
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

    # --- CONTROL DE "DATOS VACÍOS" (EVITA EL CRASH) ---
    if df_f.empty:
        st.warning("⚠️ No hay datos que coincidan con la selección. Por favor, selecciona al menos un Motivo de Incidencia en la barra lateral.")
        st.stop() # Detiene la ejecución aquí para que no intente graficar nada vacío

    # --- 4. DASHBOARD ---
    contexto = f"en {sel_eps}" if sel_eps != "Todas las EPS" else "Regional"
    st.title(f"🚀 Monitor Prescriptivo: {contexto}")

    # KPIs Resaltados
    c1, c2, c3 = st.columns(3)
    total_costo = df_f['costo_reparacion'].sum()
    total_horas = df_f['duracion_horas'].sum()
    
    with c1:
        st.markdown(f"<div class='card-calc'><div class='calc-label'>Costo Operativo</div><div class='money-value'>S/. {total_costo:,.0f}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='card-calc' style='border-bottom-color: #3B82F6;'><div class='calc-label'>Servicio Perdido</div><div class='money-value' style='color:#1D4ED8;'>{total_horas:,.1f} h</div></div>", unsafe_allow_html=True)
    with c3:
        pob_total = df_f['impacto'].sum()
        st.markdown(f"<div class='card-calc' style='border-bottom-color: #F59E0B;'><div class='calc-label'>Impacto Total</div><div class='money-value' style='color:#B45309;'>{pob_total:,.0f} hab</div></div>", unsafe_allow_html=True)

    st.divider()

    # BLOQUE GRÁFICOS
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("📍 Análisis de Criticidad por Instalación")
        df_inst = df_f.groupby('estacion_id').agg({'costo_reparacion': 'sum', 'duracion_horas': 'sum'}).reset_index().sort_values('costo_reparacion', ascending=False)
        
        fig_inst = px.bar(df_inst.head(10), x='estacion_id', y='costo_reparacion', color='duracion_horas', 
                          color_continuous_scale='YlOrRd', labels={'costo_reparacion':'Gasto S/.', 'duracion_horas':'Horas'})
        fig_inst.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_inst, use_container_width=True)

    with col_b:
        st.markdown("### 🔍 Auditoría Económica")
        # Uso de try/except por si el filtrado extremo rompe el acceso a índices
        try:
            top_id = df_inst.iloc[0]['estacion_id']
            costo_top = df_inst.iloc[0]['costo_reparacion']
            pct = (costo_top / total_costo * 100) if total_costo > 0 else 0
            
            st.markdown(f"""
            <div class='logic-container'>
                <span class='formula-tag'>Lógica: (Gasto_Max / Gasto_Total)</span>
                <p class='suggestion-text'>
                    La instalación <b>{top_id}</b> representa el <span class='highlight-calc'>{pct:.1f}%</span> del gasto actual.
                    <br><br><span class='action-tag'>PRESCRIPCIÓN:</span> Iniciar plan de renovación hidráulica en este sector para frenar el drenaje de fondos.
                </p>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.info("Selecciona más datos para ver el análisis detallado.")

    # SIMULADOR FINAL
    st.divider()
    st.header("⚙️ Simulador Prescriptivo de Retorno (ROI)")
    s1, s2, s3 = st.columns(3)
    
    with s1:
        mejora = st.slider("Optimización de Respuesta (%)", 0, 100, 20)
    with s2:
        horas_recup = total_horas * (mejora/100)
        st.metric("Horas Recuperadas", f"+{horas_recup:,.1f} h", delta="Impacto Social")
    with s3:
        ahorro = (total_costo * 0.15) * (mejora/100) # Lógica: 15% del costo es variable por tiempo
        st.markdown(f"<div class='card-calc' style='border-bottom-color: #059669; padding: 15px;'>", unsafe_allow_html=True)
        st.markdown(f"<div class='calc-label'>Ahorro Potencial</div><div class='money-value' style='font-size:1.5rem'>S/. {ahorro:,.0f}</div></div>", unsafe_allow_html=True)

else:
    st.error("Archivo no encontrado o vacío.")