# frontend/app.py
import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="SOC Triage Dashboard", page_icon="🛡️", layout="wide")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 2. Inicializar el estado de la sesión para guardar la cola de tickets
if "ticket_queue" not in st.session_state:
    st.session_state.ticket_queue = []

st.title("🛡️ SOC Triage Dashboard")
st.markdown("Plataforma de evaluación semántica con Inteligencia Artificial Explicable (XAI).")

# 3. Panel Lateral: Ingesta de Tickets
with st.sidebar:
    st.header("📥 Nuevo Ticket")
    with st.form("ticket_form"):
        user_role = st.selectbox(
            "Rol del Usuario",
            ["Secretaria", "Analista Contable", "Gerente General", "Administrador de TI"]
        )
        ticket_text = st.text_area("Descripción del Incidente", height=150, 
                                   placeholder="Ej: Mi equipo está lento y los archivos tienen extensión .lock")
        
        submitted = st.form_submit_button("Analizar Riesgo")

    if submitted and ticket_text:
        # Intento de conexión al backend
        payload = {"texto": ticket_text, "rol_usuario": user_role}
        try:
            response = requests.post(f"{BACKEND_URL}/api/triage", json=payload, timeout=5)
            result = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Fallback simulado para desarrollo frontend sin backend
            st.warning("Backend no detectado. Mostrando datos simulados de XAI.")
            result = {
                "prioridad": 5 if "lock" in ticket_text.lower() or "gerente" in user_role.lower() else 2,
                "texto": ticket_text,
                "rol_usuario": user_role,
                "explicacion_xai": {
                    "lock": 0.45,
                    "archivos": 0.15,
                    "lento": 0.05,
                    f"rol_{user_role.lower().replace(' ', '_')}": 0.35
                }
            }
        
        # Agregar el resultado al inicio de la cola
        st.session_state.ticket_queue.insert(0, result)

# 4. Vista Principal: Cola de Tickets y Revelación Progresiva
st.header("📋 Cola de Incidentes Activos")

if not st.session_state.ticket_queue:
    st.info("No hay tickets en la cola. Ingresa uno en el panel lateral.")
else:
    for i, ticket in enumerate(st.session_state.ticket_queue):
        # Color dinámico según prioridad
        color = "🔴" if ticket["prioridad"] >= 4 else "🟡" if ticket["prioridad"] == 3 else "🟢"
        
        # Nivel 1 de Revelación: Resumen de Alta Urgencia
        with st.container():
            st.subheader(f"{color} Prioridad {ticket['prioridad']} | Rol: {ticket['rol_usuario']}")
            st.write(f"**Reporte:** {ticket['texto']}")
            
            # Nivel 2 de Revelación: Detalle XAI bajo demanda
            with st.expander("Ver razonamiento de la IA (LIME/SHAP)"):
                st.markdown("**Factores determinantes de la decisión:**")
                
                # Transformar los pesos XAI en un DataFrame para Plotly
                df_xai = pd.DataFrame(
                    list(ticket["explicacion_xai"].items()), 
                    columns=["Variable", "Peso Predictivo"]
                )
                df_xai = df_xai.sort_values(by="Peso Predictivo", ascending=True)
                
                # Gráfico de barras horizontal para explicabilidad
                fig = px.bar(
                    df_xai, 
                    x="Peso Predictivo", 
                    y="Variable", 
                    orientation='h',
                    color="Peso Predictivo",
                    color_continuous_scale="Reds" if ticket["prioridad"] >= 4 else "Blues"
                )
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
            st.divider()