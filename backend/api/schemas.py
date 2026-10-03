# backend/api/schemas.py
from pydantic import BaseModel, Field
from typing import Dict

class TicketRequest(BaseModel):
    titulo: str = Field(..., description="Titulo Corto del Ticket", min_length = 10, max_length = 100)
    texto: str = Field(..., description="Descripción del incidente reportado por el usuario", min_length=5)
    rol_usuario: str = Field(..., description="Rol institucional del usuario que reporta")

class TicketResponse(BaseModel):
    titulo: str 
    nivel_prioridad_texto: str = Field(..., description="Etiqueta legible: CRÍTICO, ALTO, MEDIO, BAJO")
    prioridad: int = Field(..., ge=1, le=5, description="Nivel de urgencia asignado (1 al 5)")
    texto: str
    rol_usuario: str
    explicacion_xai: Dict[str, float] = Field(
        ..., 
        description="Diccionario de telemetría XAI: mapea variables/palabras clave a su peso predictivo"
    )