# backend/api/schemas.py
from datetime import datetime
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field

class RolUsuario(str, Enum):
    EMPLEADO = "Empleado General"
    ANALISTA = "Analista / Contable"
    SUPERVISOR = "Supervisor / Coordinador"
    GERENTE = "Gerente / Director"
    ADMIN_TI = "Administrador de TI"
    CEO = "CEO / Alta Dirección"

class TicketRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    titulo: str = Field(..., min_length=5, max_length=100, description="Titulo corto del ticket")
    texto: str = Field(..., min_length=10, max_length=2000, description="Descripción detallada del incidente reportado por el usuario")
    rol_usuario:RolUsuario = Field(..., description="Rol institucional del usuario que reporta el ticket")

class TicketResponse(BaseModel):
    id: str = Field(..., description="Identificador único del ticket generado por el sistema")
    titulo: str 
    creado_en: datetime = Field(..., description="Timestamp de creación del ticket")
    nivel_prioridad_texto: str = Field(..., description="Etiqueta legible: CRÍTICO, ALTO, MEDIO, BAJO")
    prioridad: int = Field(..., ge=1, le=5, description="Nivel de urgencia asignado (1 al 5)")
    texto: str
    rol_usuario: RolUsuario
    explicacion_xai: Dict[str, float] = Field(
        ..., 
        description="Diccionario de telemetría XAI: mapea variables/palabras clave a su peso predictivo"
    )

class QueueResponse(BaseModel):
    total: int = Field(..., description="Número total de tickets en la cola")
    tickets: List[TicketResponse] = Field(..., description="Lista de tickets en la cola")