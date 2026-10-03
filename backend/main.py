# backend/main.py
import uuid
from datetime import datetime, timezone
from typing import List
from api.schemas import QueueResponse, RolUsuario, TicketRequest, TicketResponse
from core import queue_store
from core.triage_rules import ETIQUETAS, calcular_prioridad
from fastapi import FastAPI

app = FastAPI(
    title="SOC Cognitive API",
    description="Motor de Triage Semántico y XAI para tickets de seguridad",
    version="1.0.0"
)

@app.get("/api/roles", response_model=List[str])
def get_roles():
    return[rol.value for rol in RolUsuario]

@app.post("/api/triage", response_model=TicketResponse)
def process_ticket(ticket: TicketRequest):
    prioridad, explicacion = calcular_prioridad(ticket.titulo, ticket.texto, ticket.rol_usuario)
    ticket_id = str(uuid.uuid4())
    ticket_response = TicketResponse(
        id=ticket_id,
        titulo=ticket.titulo,
        creado_en=datetime.now(timezone.utc),
        nivel_prioridad_texto=ETIQUETAS[prioridad],
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
