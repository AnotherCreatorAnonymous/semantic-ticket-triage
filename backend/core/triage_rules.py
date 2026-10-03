import re
import unicodedata
from typing import Dict, Tuple

from api.schemas import RolUsuario

PESO_ROL = {
    RolUsuario.EMPLEADO: 1,
    RolUsuario.ANALISTA: 2,
    RolUsuario.SUPERVISOR: 3,
    RolUsuario.GERENTE: 4,
    RolUsuario.ADMIN_TI: 4,
    RolUsuario.CEO: 5
}

PALABRAS_CRITICAS = {"ransomware", "brecha", "ataque", "hackeo", "virus", "malware", "phishing"}
PALABRAS_ALTAS = {"acceso", "contraseña", "bloqueado", "urgente"}
EXTENSIONES_SOSPECHOSAS = {"lock", "locked", "encrypted", "crypt"}

BONUS_CRITICO = 2
BONUS_ALTO = 1

ETIQUETAS = {1: "BAJO", 2: "BAJO", 3: "MEDIO", 4: "ALTO", 5: "CRÍTICO"}

def normalizar_texto(texto:str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")

# Se calculan una sola vez al importar el módulo, no en cada petición
CRITICAS_NORMALIZADAS = {normalizar_texto(palabra) for palabra in PALABRAS_CRITICAS}
ALTAS_NORMALIZADAS = {normalizar_texto(palabra) for palabra in PALABRAS_ALTAS}

# Nombre de archivo seguido de una extensión sospechosa, ej. "informe.lock"
_EXTENSIONES_REGEX = "|".join(EXTENSIONES_SOSPECHOSAS)
PATRON_SOSPECHOSO = re.compile(rf"\b\w+\.({_EXTENSIONES_REGEX})\b")

def calcular_prioridad(titulo: str, texto: str, rol: RolUsuario) -> Tuple[int, Dict[str, float]]:
    contenido = normalizar_texto(titulo + " " + texto)

    tokens = set(re.findall(r"\b\w+\b", contenido))
    extensiones = set(PATRON_SOSPECHOSO.findall(contenido))

    criticas = (tokens & CRITICAS_NORMALIZADAS) | extensiones
    altas = tokens & ALTAS_NORMALIZADAS

    peso_rol = PESO_ROL[rol]
    explicacion = {f"rol: {rol.value}": peso_rol}

    for palabra in criticas:
        clave = f".{palabra}" if palabra in EXTENSIONES_SOSPECHOSAS else palabra
        explicacion[clave] = BONUS_CRITICO

    for palabra in altas:
        explicacion[palabra] = BONUS_ALTO

    bonus = BONUS_CRITICO if criticas else BONUS_ALTO if altas else 0
    prioridad = min(5, peso_rol + bonus)

    return prioridad, explicacion
