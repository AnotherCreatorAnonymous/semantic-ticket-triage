# frontend/api_client.py
"""Cliente HTTP del backend. Toda comunicación con la API pasa por aquí; app.py solo dibuja."""
import os
from typing import Any, Dict, List

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT_SEGUNDOS = 5

# Nombres legibles para los campos que devuelve Pydantic en los errores 422
NOMBRES_CAMPOS = {
    "titulo": "Título",
    "texto": "Descripción",
    "rol_usuario": "Rango / Rol",
}


class BackendNoDisponible(Exception):
    """El backend no responde (caído, apagado o fuera de tiempo)."""


class ErrorValidacion(Exception):
    """El backend rechazó el ticket (422). `errores` trae mensajes listos para mostrar."""

    def __init__(self, errores: List[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


class ErrorBackend(Exception):
    """El backend respondió con un error inesperado (500, 404, ...)."""


def _request(metodo: str, ruta: str, **kwargs) -> requests.Response:
    try:
        return requests.request(metodo, f"{BACKEND_URL}{ruta}", timeout=TIMEOUT_SEGUNDOS, **kwargs)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
        raise BackendNoDisponible(f"No se pudo conectar con {BACKEND_URL}") from exc


def _traducir_errores_422(detalle: List[Dict[str, Any]]) -> List[str]:
    """Convierte el `detail` de Pydantic en frases como 'Título: String should have at least 5 characters'."""
    mensajes = []
    for error in detalle:
        campo = error.get("loc", ["", "?"])[-1]
        mensajes.append(f"{NOMBRES_CAMPOS.get(campo, campo)}: {error.get('msg', 'valor inválido')}")
    return mensajes


def obtener_roles() -> List[str]:
    respuesta = _request("GET", "/api/roles")
    if respuesta.status_code != 200:
        raise ErrorBackend(f"GET /api/roles respondió {respuesta.status_code}")
    return respuesta.json()


def enviar_ticket(titulo: str, texto: str, rol_usuario: str) -> Dict[str, Any]:
    payload = {"titulo": titulo, "texto": texto, "rol_usuario": rol_usuario}
    respuesta = _request("POST", "/api/triage", json=payload)
    if respuesta.status_code == 200:
        return respuesta.json()
    if respuesta.status_code == 422:
        raise ErrorValidacion(_traducir_errores_422(respuesta.json().get("detail", [])))
    raise ErrorBackend(f"POST /api/triage respondió {respuesta.status_code}")


def obtener_cola() -> Dict[str, Any]:
    respuesta = _request("GET", "/api/queue")
    if respuesta.status_code != 200:
        raise ErrorBackend(f"GET /api/queue respondió {respuesta.status_code}")
    return respuesta.json()
