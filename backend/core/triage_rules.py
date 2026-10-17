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

PALABRAS_CRITICAS = {
    "ransomware", "brecha", "ataque", "hackeo", "virus", "malware", "phishing", "spyware", "troyano",
    "fondo", "pantalla", "rojo", "candado", "ventana", "popup", "popups", "dialogo",
    "lento", "congelado", "bloqueado", "no abre", "no puedo", "se cierra", "abre solo",
    "reinicia", "cuelga", "se congela", "desaparece", "extrano", "sospechosa",
    "pagar", "rescate", "recuperar", "desbloquear", "dinero", "bitcoin",
    "cifrado", "encriptado", "protegido", "datos", "archivo", "corrupto", "critico"
}

PALABRAS_ALTAS = {
    "acceso", "contrasena", "urgente", "error", "falla", "problema", "permisos", "cuenta"
}

EXTENSIONES_SOSPECHOSAS = {"lock", "locked", "encrypted", "crypt", "encrypt"}

BONUS_CRITICO = 2
BONUS_ALTO = 1

ETIQUETAS = {1: "BAJO", 2: "BAJO", 3: "MEDIO", 4: "ALTO", 5: "CRÍTICO"}

def normalizar_texto(texto:str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")

# Se calculan una sola vez al importar el módulo, no en cada petición
CRITICAS_NORMALIZADAS = {normalizar_texto(palabra) for palabra in PALABRAS_CRITICAS}
ALTAS_NORMALIZADAS = {normalizar_texto(palabra) for palabra in PALABRAS_ALTAS}

# Extensión sospechosa: con o sin nombre de archivo, ej. "informe.lock" o "termina en .lock"
_EXTENSIONES_REGEX = "|".join(EXTENSIONES_SOSPECHOSAS)
PATRON_SOSPECHOSO = re.compile(rf"\.({_EXTENSIONES_REGEX})\b")

def calcular_prioridad(titulo: str, texto: str, rol: RolUsuario) -> Tuple[int, Dict[str, float]]:
    contenido = normalizar_texto(titulo + " " + texto)

    tokens = set(re.findall(r"\b\w+\b", contenido))
    extensiones_encontradas = PATRON_SOSPECHOSO.findall(contenido)
    extensiones = set(extensiones_encontradas)

    criticas = (tokens & CRITICAS_NORMALIZADAS) | extensiones
    altas = tokens & ALTAS_NORMALIZADAS

    peso_rol = float(PESO_ROL[rol])
    explicacion = {f"rol: {rol.value}": peso_rol}

    for palabra in criticas:
        clave = f".{palabra}" if palabra in EXTENSIONES_SOSPECHOSAS else palabra
        explicacion[clave] = float(BONUS_CRITICO)

    for palabra in altas:
        explicacion[palabra] = float(BONUS_ALTO)

    # LÓGICA MEJORADA: Prioridad = Riesgo de Seguridad (primero), rol solo suma si hay riesgo
    if criticas:
        # CRÍTICO: hay palabras de seguridad críticas → rol suma para urgencia
        bonus = BONUS_CRITICO
        prioridad = min(5, peso_rol + bonus)
    elif altas:
        # ALTO: hay palabras de seguridad altas → rol suma pero limitado
        bonus = BONUS_ALTO
        prioridad = min(4, peso_rol + bonus)
    else:
        # BAJO: sin riesgo de seguridad detectado → rol NO suma, máx nivel 2
        bonus = 0
        prioridad = min(2, peso_rol) if peso_rol > 1 else 1

    return int(prioridad), explicacion
