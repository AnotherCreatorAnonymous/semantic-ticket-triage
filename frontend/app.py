# frontend/app.py
"""Dashboard SOC (Semana 1): formulario de tickets + cola de TI ordenada por prioridad."""
import re

import pandas as pd
import plotly.express as px
import streamlit as st

import api_client

# Deben coincidir con TicketRequest en backend/api/schemas.py.
# Validar aquí evita un viaje al backend; el backend sigue siendo la validación definitiva.
TITULO_MIN, TITULO_MAX = 5, 100
TEXTO_MIN, TEXTO_MAX = 10, 2000

ZONA_HORARIA = "America/Bogota"

ESTILO_NIVEL = {
    "CRÍTICO": ("🔴", "red"),
    "ALTO": ("🟠", "orange"),
    "MEDIO": ("🟡", "yellow"),
    "BAJO": ("🟢", "green"),
}

st.set_page_config(page_title="SOC Triage Dashboard", page_icon="🛡️", layout="wide")


# ---------------------------------------------------------------------------
# Utilidades de presentación
# ---------------------------------------------------------------------------
def escapar_markdown(texto: str) -> str:
    """Evita que el texto del usuario se interprete como Markdown (enlaces, negritas, etc.).

    En un SOC esto importa: un ticket con '[clic aquí](http://sitio-malicioso)' no debe
    convertirse en un enlace clicable dentro del dashboard.
    """
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|<>~:$])", r"\\\1", texto)


def formatear_fecha(iso_utc: str) -> str:
    return pd.to_datetime(iso_utc, utc=True).tz_convert(ZONA_HORARIA).strftime("%d/%m/%Y %H:%M")


def validar_formulario(titulo: str, texto: str) -> list:
    errores = []
    if not TITULO_MIN <= len(titulo) <= TITULO_MAX:
        errores.append(f"El título debe tener entre {TITULO_MIN} y {TITULO_MAX} caracteres.")
    if not TEXTO_MIN <= len(texto) <= TEXTO_MAX:
        errores.append(f"La descripción debe tener entre {TEXTO_MIN} y {TEXTO_MAX} caracteres.")
    return errores


@st.cache_data(ttl=60)
def cargar_roles() -> list:
    # Los roles cambian muy poco: se piden al backend como máximo una vez por minuto
    return api_client.obtener_roles()


def render_grafico_factores(explicacion: dict, color: str):
    df = pd.DataFrame(list(explicacion.items()), columns=["Factor", "Aporte"])
    df["Tipo"] = df["Factor"].apply(lambda f: "Rol" if f.startswith("rol: ") else "Palabra clave")
    df = df.sort_values("Aporte")

    fig = px.bar(
        df,
        x="Aporte",
        y="Factor",
        color="Tipo",
        orientation="h",
        color_discrete_map={"Rol": "#8c8c8c", "Palabra clave": color},
    )
    fig.update_layout(
        height=80 + 40 * len(df),
        margin=dict(l=0, r=0, t=10, b=0),
        legend_title_text="",
        xaxis_title="Puntos que aporta a la prioridad",
        yaxis_title="",
    )
    st.plotly_chart(fig, width="stretch")


def render_ticket(ticket: dict):
    nivel = ticket["nivel_prioridad_texto"]
    emoji, color = ESTILO_NIVEL.get(nivel, ("⚪", "gray"))
    colores_grafico = {"red": "#d62728", "orange": "#ff7f0e", "yellow": "#e3b505", "green": "#2ca02c"}

    with st.container(border=True):
        cabecera, meta = st.columns([3, 1])
        with cabecera:
            st.markdown(
                f"{emoji} :{color}[**{nivel}**] · Prioridad **{ticket['prioridad']}**  \n"
                f"### {escapar_markdown(ticket['titulo'])}"
            )
        with meta:
            st.caption(f"👤 {ticket['rol_usuario']}")
            st.caption(f"🕒 {formatear_fecha(ticket['creado_en'])}")

        st.text(ticket["texto"])

        with st.expander("¿Por qué esta prioridad?"):
            st.caption(
                "Semana 1: factores de la heurística (peso del rol + palabras clave). "
                "En la Semana 3 se reemplazan por explicaciones LIME del modelo."
            )
            render_grafico_factores(ticket["explicacion_xai"], colores_grafico.get(color, "#1f77b4"))


# ---------------------------------------------------------------------------
# Estado de la sesión
# ---------------------------------------------------------------------------
# Streamlit no permite cambiar el valor de un widget después de dibujarlo, así que
# para limpiar el formulario tras un envío exitoso se marca una bandera y se limpia
# en la siguiente ejecución, ANTES de dibujar los campos.
if st.session_state.pop("limpiar_formulario", False):
    st.session_state["campo_titulo"] = ""
    st.session_state["campo_texto"] = ""

if "ultimo_envio" in st.session_state:
    enviado = st.session_state.pop("ultimo_envio")
    st.toast(f"Ticket encolado como {enviado['nivel_prioridad_texto']} (prioridad {enviado['prioridad']})", icon="✅")


# ---------------------------------------------------------------------------
# Panel lateral: formulario de nuevo ticket
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📥 Nuevo Ticket de Soporte")

    try:
        roles = cargar_roles()
    except (api_client.BackendNoDisponible, api_client.ErrorBackend) as exc:
        roles = []
        st.error(f"🔴 Backend no disponible: {exc}")

    with st.form("formulario_ticket"):
        rol = st.selectbox("Rango / Rol *", roles, disabled=not roles)
        titulo = st.text_input(
            "Título del Ticket *",
            key="campo_titulo",
            max_chars=TITULO_MAX,
            placeholder="Ej: Archivos con extensión .lock",
        )
        texto = st.text_area(
            "Descripción del Incidente *",
            key="campo_texto",
            height=150,
            max_chars=TEXTO_MAX,
            placeholder="Ej: Desde esta mañana ningún archivo abre y todos terminan en .lock",
        )
        enviado = st.form_submit_button("🔍 Analizar con IA", disabled=not roles, width="stretch")

    if enviado:
        titulo, texto = titulo.strip(), texto.strip()
        errores = validar_formulario(titulo, texto)
        if errores:
            for error in errores:
                st.error(error)
        else:
            try:
                with st.spinner("Analizando ticket..."):
                    resultado = api_client.enviar_ticket(titulo, texto, rol)
            except api_client.ErrorValidacion as exc:
                st.error("El backend rechazó el ticket:")
                for error in exc.errores:
                    st.write(f"- {error}")
            except (api_client.BackendNoDisponible, api_client.ErrorBackend) as exc:
                st.error(f"No se pudo enviar el ticket: {exc}")
            else:
                st.session_state["ultimo_envio"] = resultado
                st.session_state["limpiar_formulario"] = True
                st.rerun()


# ---------------------------------------------------------------------------
# Vista principal: cola de TI
# ---------------------------------------------------------------------------
st.title("🛡️ SOC Triage Dashboard")
st.markdown("Plataforma de evaluación semántica con Inteligencia Artificial Explicable (XAI).")

titulo_cola, boton_actualizar = st.columns([4, 1])
with titulo_cola:
    st.header("📋 Cola de Incidentes")
with boton_actualizar:
    # Cada clic vuelve a ejecutar el script, lo que recarga la cola desde el backend
    st.button("🔄 Actualizar", width="stretch")

try:
    cola = api_client.obtener_cola()
except (api_client.BackendNoDisponible, api_client.ErrorBackend) as exc:
    st.error(f"No se pudo cargar la cola: {exc}")
    st.stop()

if cola["total"] == 0:
    st.info("No hay tickets en la cola. Ingresa uno en el panel lateral.")
else:
    st.caption(f"{cola['total']} ticket(s) · ordenados por prioridad (los empates, por orden de llegada)")
    for ticket in cola["tickets"]:
        render_ticket(ticket)
