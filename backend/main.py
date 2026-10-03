# backend/main.py
from fastapi import FastAPI
from api.schemas import TicketRequest, TicketResponse

app = FastAPI(
    title="SOC Cognitive API",
    description="Motor de Triage Semántico y XAI para tickets de seguridad",
    version="1.0.0"
)

tickets_queue: list = []

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
    RANGOS_PESO = {                                                                                                                                                                                 
        "empleado general":        1,                                                                                                                                                               
        "analista / contable":     2,                                                                                                                                                               
        "supervisor / coordinador": 3,                                                                                                                                                              
        "gerente / director":      4,
        "administrador de ti":     4,
        "ceo / alta dirección":    5,
    }
    peso_rango = RANGOS_PESO.get(rol_lower, 1)
    
    # Simular extracción de pesos XAI (LIME/SHAP)
    pesos_xai = {
        f"rol_{ticket.rol_usuario.replace(' ', '_')}": 0.40 if "gerente" in rol_lower else 0.15,
    }

    PALABRAS_CRITICAS = ["ransomware", "lock", "brecha", "ataque", "hackeo", "virus"]
    PALABRAS_ALTAS    = ["acceso", "contraseña", "bloqueado", "urgente"]
  
    bonus = 0
    for palabra in PALABRAS_CRITICAS:
        if palabra in texto_lower:
            bonus = 2
            break
    for palabra in PALABRAS_ALTAS:
        if palabra in texto_lower:
            bonus = max(bonus, 1)
            break
  
    prioridad_asignada = min(5, peso_rango + bonus)
            
    # Rellenar con ruido si no hay palabras clave detectadas para probar los gráficos
    if len(pesos_xai) == 1:
        pesos_xai[texto_lower.split()[0]] = 0.05

    ETIQUETAS = {1: "BAJO", 2: "BAJO", 3: "MEDIO", 4: "ALTO", 5: "CRÍTICO"}

    tickets_queue.append({
        "titulo": ticket.titulo,
        "rol_usuario": ticket.rol_usuario,
        "prioridad": prioridad_asignada,
        "nivel_prioridad_texto": ETIQUETAS[prioridad_asignada],
        "texto": ticket.texto,
    })
  
    return TicketResponse(
        titulo=ticket.titulo,
        nivel_prioridad_texto=ETIQUETAS[prioridad_asignada],
        prioridad=prioridad_asignada,
        texto=ticket.texto,
        rol_usuario=ticket.rol_usuario,
        explicacion_xai=pesos_xai
    )

@app.get("/api/queue")
def get_queue():
    """
    Devuelve la cola de tickets ordenada por prioridad descendente (más crítico primero).
    """
    ordenada = sorted(tickets_queue, key=lambda t: t["prioridad"], reverse=True)
    return {"total": len(ordenada), "tickets": ordenada}
