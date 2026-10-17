# backend/main.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from api.schemas import QueueResponse, RolUsuario, TicketRequest, TicketResponse, NivelPrioridad
from core import queue_store, nlp_engine
from core.triage_rules import ETIQUETAS, calcular_prioridad
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="SOC Cognitive API",
    description="Motor de Triage Semántico y XAI para tickets de seguridad",
    version="2.0.0"
)

# Load ML model at startup
@app.on_event("startup")
def startup_event():
    try:
        nlp_engine.load_model()
        print("✅ Model loaded successfully")
    except FileNotFoundError:
        print("⚠️ Model not found. Using heuristic fallback for S2. Train with: python training/train_baseline.py")
    except Exception as e:
        print(f"⚠️ Model load error: {e}. Using heuristic fallback.")

@app.get("/api/roles", response_model=List[str])
def get_roles():
    return[rol.value for rol in RolUsuario]

@app.post("/api/triage", response_model=TicketResponse)
def process_ticket(ticket: TicketRequest):
    prioridad, explicacion = calcular_prioridad(ticket.titulo, ticket.texto, ticket.rol_usuario)
    ticket_id = str(uuid.uuid4())
    nivel_texto = ETIQUETAS[prioridad]
    ticket_response = TicketResponse(
        id=ticket_id,
        titulo=ticket.titulo,
        creado_en=datetime.now(timezone.utc),
        nivel_prioridad_texto=NivelPrioridad(nivel_texto),
        prioridad=prioridad,
        texto=ticket.texto,
        rol_usuario=ticket.rol_usuario,
        explicacion_xai=explicacion
    )
    queue_store.agregar(ticket_response)
    return ticket_response

@app.get("/api/queue", response_model=QueueResponse)
def get_queue():
    tickets = queue_store.listar_ordenada()
    return QueueResponse(total=len(tickets), tickets=tickets)

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "model": "loaded" if nlp_engine.is_loaded() else "heuristic_fallback"
    }

@app.delete("/api/queue/{ticket_id}")
def delete_ticket(ticket_id: str):
    deleted = queue_store.eliminar(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return {"status": "deleted", "id": ticket_id}
