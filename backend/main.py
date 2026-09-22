# backend/main.py
from fastapi import FastAPI
from api.schemas import TicketRequest, TicketResponse

app = FastAPI(
    title="SOC Cognitive API",
    description="Motor de Triage Semántico y XAI para tickets de seguridad",
    version="1.0.0"
)

@app.post("/api/triage", response_model=TicketResponse)
async def process_ticket(ticket: TicketRequest):
    """
    Endpoint principal de inferencia.
    Recibe el ticket, evalúa la semántica y retorna la prioridad con telemetría XAI.
    """
    # -------------------------------------------------------------------
    # TODO: Inyectar backend.core.nlp_engine y backend.core.xai_engine
    # -------------------------------------------------------------------
    
    # Lógica simulada (Mock) para pruebas de integración con el Frontend
    texto_lower = ticket.texto.lower()
    rol_lower = ticket.rol_usuario.lower()
    
    # Evaluar riesgo base
    is_critical = "lock" in texto_lower or "ransomware" in texto_lower or "gerente" in rol_lower
    prioridad_asignada = 5 if is_critical else 2
    
    # Simular extracción de pesos XAI (LIME/SHAP)
    pesos_xai = {
        f"rol_{ticket.rol_usuario.replace(' ', '_')}": 0.40 if "gerente" in rol_lower else 0.15,
    }
    
    palabras_clave = ["lock", "ransomware", "brecha", "lento", "acceso"]
    for palabra in palabras_clave:
        if palabra in texto_lower:
            pesos_xai[palabra] = 0.55 if palabra in ["lock", "ransomware", "brecha"] else 0.10
            
    # Rellenar con ruido si no hay palabras clave detectadas para probar los gráficos
    if len(pesos_xai) == 1:
        pesos_xai[texto_lower.split()[0]] = 0.05
        
    return TicketResponse(
        prioridad=prioridad_asignada,
        texto=ticket.texto,
        rol_usuario=ticket.rol_usuario,
        explicacion_xai=pesos_xai
    )