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

# CRÍTICAS: SOLO palabras que INEQUÍVOCAMENTE indican ataques de seguridad
PALABRAS_CRITICAS = {
    # Tipos de malware/ataques
    "ransomware", "malware", "virus", "troyano", "phishing", "spyware", "gusano", "botnet",
    # Síntomas específicos de ransomware
    "candado", "encriptado", "cifrado", "bloqueado_archivos",
    # Comportamiento de malware
    "no_puedo_cerrar", "abre_solo", "reinicia_solo", "ventanas_infinitas",
    # Extorsión/rescate
    "pagar", "rescate", "bitcoin", "dinero_rescate", "desbloquear_pago",
    # Compromiso
    "brecha", "hackeo", "ataque", "datos_robados", "acceso_no_autorizado", "penetracion",
    # Síntomas de compromiso severo
    "criptolocker", "petya", "wannacry", "notpetya"
}

# ALTAS: palabras de seguridad importantes pero no críticas
PALABRAS_ALTAS = {
    "contraseña", "acceso", "cuenta", "permisos", "credenciales",
    "urgente", "critico", "emergencia", "alerta",
    "error_sistema", "falla_critica", "problema_seguridad"
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

    # LÓGICA MEJORADA: Prioridad basada en RIESGO, no en CARGO
    if criticas:
        # CRÍTICO: cualquier palabra crítica = prioridad MÁXIMA (5)
        prioridad = 5
    elif altas:
        # ALTO: palabras de seguridad altas = nivel 3
        # El cargo ANALISTA/SUPERVISOR/GERENTE/ADMIN/CEO no suma aquí
        prioridad = 3
    else:
        # BAJO: sin riesgo = SIEMPRE nivel 1, rol irrelevante
        prioridad = 1

    return int(prioridad), explicacion
