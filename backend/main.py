import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from api.schemas import QueueResponse, RolUsuario, TicketRequest, TicketResponse, NivelPrioridad
from core import queue_store, nlp_engine
from core.triage_rules import ETIQUETAS, ajustar_prediccion_ml, calcular_prioridad
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse


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
    # S2: Usar modelo ML si está disponible, fallback a heurística S1
    if nlp_engine.is_loaded():
        try:
            prioridad, confianza, explicacion = nlp_engine.predecir(
                ticket.titulo, ticket.texto, ticket.rol_usuario
            )
            # Capa híbrida: señales de ataque -> CRÍTICO; si no, el rol acota el rango
            prioridad, explicacion = ajustar_prediccion_ml(
                prioridad, ticket.titulo, ticket.texto, ticket.rol_usuario, explicacion
            )
        except Exception as e:
            print(f"⚠️ Model inference error: {e}. Falling back to heuristic.")
            prioridad, explicacion = calcular_prioridad(ticket.titulo, ticket.texto, ticket.rol_usuario)
    else:
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

@app.get("/api/queue/stream")
async def queue_stream():
    """
    Canal Server-Sent Events (SSE) para notificar cambios en la cola en tiempo real.
    Emite eventos instantáneos cuando se crea o elimina un ticket desde cualquier origen.
    """
    loop = asyncio.get_running_loop()
    event_queue: asyncio.Queue = asyncio.Queue()

    def listener(action: str, payload):
        item_id = payload if isinstance(payload, str) else getattr(payload, "id", str(payload))
        data = {
            "action": action,
            "id": item_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        loop.call_soon_threadsafe(event_queue.put_nowait, json.dumps(data))

    queue_store.register_listener(listener)

    async def event_generator():
        try:
            # Notificación inicial de conexión establecida
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"
            while True:
                try:
                    data_str = await asyncio.wait_for(event_queue.get(), timeout=15.0)
                    yield f"event: queue_update\ndata: {data_str}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive ping periódico para prevenir desconexión de proxies
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            queue_store.unregister_listener(listener)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


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
