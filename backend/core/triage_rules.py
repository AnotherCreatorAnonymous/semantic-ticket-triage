import re
import unicodedata
from typing import Dict, Tuple

from api.schemas import RolUsuario

PESO_ROL = {
    RolUsuario.EMPLEADO: 1,
    RolUsuario.SECRETARIA: 2,
    RolUsuario.ANALISTA: 2,
    RolUsuario.SUPERVISOR: 3,
    RolUsuario.GERENTE: 4,
    RolUsuario.ADMIN_TI: 4,
    RolUsuario.CEO: 5
}

# La detección  se hace 100% a través de:
# - CATEGORIAS_INCIDENTE: patrones regex detallados que definen escenarios de ataque reales
# - PESO_ROL: para tickets rutinarios sin señales de incidente
#
# Esto reduce falsos positivos críticos y mantiene la precisión.

PALABRAS_CRITICAS = {
    # SOLO: nombres de malware/ataques que INEQUÍVOCAMENTE indican un incidente grave
    # (usados como fallback rápido para casos obvios)
    "ransomware", "malware", "virus", "troyano", "spyware", "gusano", "botnet", "adware",
    "criptolocker", "cryptolocker", "petya", "wannacry", "notpetya", "lockbit", "ryuk", "conti"
}

PALABRAS_ALTAS = {
    # Palabras clave que sugieren atención de seguridad pero no son críticas por sí solas
    # Se mantienen como señal complementaria al modelo ML
    "contraseña", "acceso", "cuenta", "permisos", "credenciales",
    "urgente", "critico", "emergencia"
}

EXTENSIONES_SOSPECHOSAS = {"lock", "locked", "encrypted", "crypt", "encrypt"}

BONUS_CRITICO = 2
BONUS_ALTO = 1

ETIQUETAS = {1: "BAJO", 2: "MEDIA_BAJA", 3: "MEDIO", 4: "ALTO", 5: "CRÍTICO"}

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
    """
    Priorización de fallback cuando el modelo ML no está disponible.
    Usa la misma lógica que ajustar_prediccion_ml para garantizar consistencia.
    """
    explicacion: Dict[str, float] = {}

    # 1. Detectar patrones de incidente (la fuente de verdad para seguridad)
    incidentes = detectar_incidentes(titulo, texto)

    if incidentes:
        # Hay señales claras de incidente -> prioridad mínima = piso máximo detectado
        piso = max(incidentes.values())
        for nombre, prio in incidentes.items():
            explicacion[f"alerta: {nombre}"] = float(prio)
        return int(piso), explicacion

    # 2. Sin patrones de incidente -> ticket rutinario, acotado al rango del rol
    contenido = normalizar_texto(titulo + " " + texto)
    tokens = set(re.findall(r"\b\w+\b", contenido))

    # Palabras clave como señal secundaria
    criticas = tokens & CRITICAS_NORMALIZADAS
    altas = tokens & ALTAS_NORMALIZADAS
    extensiones = set(PATRON_SOSPECHOSO.findall(contenido))

    # Construcción de explicación
    peso_rol = float(PESO_ROL[rol])
    explicacion[f"rol: {rol.value}"] = peso_rol

    if criticas or extensiones:
        for palabra in criticas | extensiones:
            clave = f".{palabra}" if palabra in EXTENSIONES_SOSPECHOSAS else palabra
            explicacion[clave] = float(BONUS_CRITICO)

    if altas:
        for palabra in altas:
            explicacion[palabra] = float(BONUS_ALTO)

    # Determinar prioridad dentro del rango permitido por el rol
    minimo, maximo = RANGO_POR_ROL[PESO_ROL[rol]]

    # Si hay palabras críticas o altas, aplicar bonus dentro del rango
    if criticas or extensiones:
        prioridad = min(maximo, minimo + 2)  # Subir dentro del rango
    elif altas:
        prioridad = min(maximo, minimo + 1)
    else:
        prioridad = minimo  # Valor base del rol

    return int(prioridad), explicacion


# ---------------------------------------------------------------------------
# Capa híbrida: reglas que se aplican SOBRE la predicción del modelo ML.
# El dataset es pequeño (150 tickets) y no cubre todos los tipos de incidente,
# así que el modelo solo no basta para detectar los casos graves.
#
# Cada categoría tiene una prioridad MÍNIMA (piso) que no depende del rol:
# un empleado que reporta ransomware o una caída masiva también es urgente.
# Los patrones se evalúan sobre texto normalizado (minúsculas, sin tildes).
# ---------------------------------------------------------------------------

CATEGORIAS_INCIDENTE = [
    # --- Piso 5: CRÍTICO --------------------------------------------------
    ("ransomware / cifrado de archivos", 5,
     r"\b(ransomware|criptolocker|cryptolocker|wannacry|petya|notpetya|lockbit|ryuk|conti)\b"
     r"|\b(cifrad|encriptad)\w*"
     r"|\.(lock|locked|encrypted|crypt|encrypt)\b"
     r"|como_recuperar|nota de rescate|contador de tiempo|pantalla roja"),
    ("extorsion (pagar para recuperar)", 5,
     r"\b(candado|rescate|bitcoin|btc|monero|criptomoneda)\b"
     r"|\bpag(ar|ue|o)\b.{0,40}\b(recuperar|datos|archivos|desbloquear)\b"
     r"|\b(recuperar|desbloquear)\b.{0,40}\bpag(ar|ue|o)\b"),
    ("cuenta comprometida", 5,
     r"\b(hackearon|hackeado|hackeada|hackeo|me hackearon)\b"
     r"|correos? (mios? )?que (yo )?no (envie|mande)"
     r"|reglas de reenvio"
     r"|inicio de sesion.{0,40}(otro pais|desconocid|no fui yo)"
     r"|(cambiaron|cambio) mi (contrasena|clave) sin"
     r"|no fui yo"),
    ("fuga o exposicion de datos", 5,
     r"\b(expuest[ao]s?|filtrad[ao]s?|filtracion|exfiltr\w*)\b"
     r"|fuga de (datos|informacion)|a la venta|dark ?web"
     r"|(base de datos|datos|informacion).{0,40}(publicad|accesible desde internet|sin contrasena)"
     r"|(bucket|s3|blob).{0,30}public"
     r"|(api ?key|token|credenciales|contrasenas?).{0,40}(github|gitlab|repositorio publico|pastebin)"),
    ("fraude financiero consumado", 5,
     r"(pagos?|transferencias?).{0,50}(no autoriz|nadie autoriz|falso|fraud)"
     r"|robaron (plata|dinero)|aprobe (un|una) (pago|transferencia).{0,40}(falso|nunca)"),
    ("criptomineria no autorizada", 5,
     r"\b(xmrig|cryptojacking|minero de cripto|mineria de cripto)\b"
     r"|cpu al 100.{0,40}(proceso raro|proceso desconocido|todos los servidores)"),
    ("sitio web desfigurado", 5, r"\b(desfigurad\w*|defacement)\b|mensaje de hackers"),
    ("ataque a aplicacion web o DDoS", 5,
     r"\b(ddos|dos attack|denegacion de servicio|inyeccion sql|sql injection|xss|webshell|web shell)\b"),
    ("intrusion / escalada de privilegios", 5,
     r"administrador de dominio|escalada de privilegios|movimiento lateral|\bedr\b"
     r"|cuenta de servicio.{0,30}(sospech|desconoc)"
     r"|(usuario|cuenta) (admin|administrador)\w* (nuev[ao]|desconocid[ao]) que nadie"),
    ("borrado masivo / wiper", 5,
     r"\b(wiper)\b|borrado masivo|(desaparecieron|borraron) (los|todos los) archivos"),
    ("acceso fisico no autorizado", 5,
     r"(persona|alguien) (desconocid[ao]|extran[ao]).{0,40}(datacenter|cuarto de servidores|rack)"),

    # --- Piso 4: ALTO -----------------------------------------------------
    ("credenciales entregadas en sitio falso", 4,
     r"\b(puse|ingrese|meti|escribi|di)\b (mi |mis |la |el )?(usuario|clave|contrasena|credenciales)"
     r".{0,80}\b(pagina|sitio|enlace|link|correo|formulario|falso|falsa|parecia)\b"
     r"|\b(pagina|sitio|enlace|link|formulario)\b.{0,80}\b(puse|ingrese|meti|escribi)\b"
     r" (mi |mis |la |el )?(usuario|clave|contrasena|credenciales)"),
    ("interaccion con phishing (clic / adjunto / macros)", 4,
     r"(di|le di|hice) (clic|click)|\b(clic|click)\b.{0,30}\b(enlace|link)\b"
     r"|habilit\w* (las )?macros|abri (el|un|la) (adjunto|archivo|factura)"
     r"|descargue (un|una|el|la) (archivo|adjunto|factura)"),
    ("malware detectado", 4,
     r"\b(malware|virus|troyano|spyware|keylogger|rootkit|gusano|botnet|adware|backdoor|puerta trasera)\b"),
    ("control remoto del equipo", 4,
     r"(mouse|raton|cursor) se mueve solo|se abren (programas|ventanas) solos?"
     r"|(abre|abren|instala) (programas|cosas) sin que"),
    ("acceso remoto instalado por terceros", 4,
     r"\b(anydesk|teamviewer|rustdesk|ultraviewer|quickassist)\b"
     r"|me pidieron (instalar|descargar)"
     r"|soporte tecnico.{0,40}(llamo|llamada|ventana|numero)"),
    ("ingenieria social / suplantacion", 4,
     r"haciendose pasar|se hizo pasar|dice ser|dijo ser|suplant\w*"
     r"|tarjetas de regalo|pago urgente|cambio de cuenta bancaria|deepfake|voz (clonada|del ceo)"),
    ("MFA / codigos no solicitados / SIM swap", 4,
     r"codigos? de (verificacion|seguridad|acceso).{0,30}no (pedi|solicite)"
     r"|(notificaciones|solicitudes) de (aprobacion|autenticacion)"
     r"|\bmfa\b.{0,30}(no|spam)|sim swap|duplicaron mi (sim|linea)"
     r"|celular (se quedo )?sin (senal|servicio) de repente"),
    ("fuerza bruta / intentos de acceso", 4,
     r"intentos fallidos|fuerza bruta|password spraying|cuenta bloqueada.{0,30}(sola|sin razon)"),
    ("dispositivo perdido o robado", 4,
     r"\b(perdi|robaron|se robaron|extravie|hurtaron)\b.{0,30}\b(portatil|laptop|computador|celular|telefono|tablet|disco|usb|carnet|tarjeta de acceso)"
     r"|\b(olvide|deje)\b (mi |el |la )?(portatil|laptop|computador|celular|telefono|tablet)\b"
     r".{0,40}\b(taxi|bus|aeropuerto|restaurante|hotel|avion|calle|uber|metro)\b"),
    ("dispositivo desconocido", 4,
     r"(usb|memoria|pendrive|dispositivo|cable).{0,40}(desconocid|sin marca|extran|que no es mio)"
     r"|encontre (una|un) (usb|memoria|pendrive|dispositivo)"),
    ("proteccion de seguridad desactivada", 4,
     r"(antivirus|firewall|defender|edr).{0,30}(desactivad|apagad|no (me )?deja (activar|encender))"),
    ("red wifi falsa / trafico interceptado", 4,
     r"wifi (falsa|gratis|abierta).{0,40}(empresa|corporativ)|certificado (invalido|no valido).{0,30}(correo|banco|portal)"
     r"|\b(evil twin|man in the middle|mitm)\b"),
    ("fuga interna de informacion", 4,
     r"(empleado|companero|excompanero|ex empleado).{0,50}(copio|descargo|envio|llevo).{0,30}(informacion|datos|archivos|base)"
     r"|correo personal.{0,30}(informacion|datos|archivos) de (la empresa|clientes)"),
    ("caida masiva de servicio", 4,
     r"\b(nadie|ningun\w*|toda la (empresa|red|sede|compania)|todo el (area|departamento|personal|equipo))\b"
     r".{0,60}\b(funciona|carga|responde|internet|entra|entrar|acceder|conectar\w*|trabajar|facturar|enviar|recibe|llamadas)\b"
     r"|(caid[oa]|no funciona) para (todos|nadie|el departamento|el area|toda)"
     r"|\b(sede|oficina|piso|edificio|area)\b.{0,30}sin internet"),

    # --- Piso 3: MEDIO ----------------------------------------------------
    ("intento de phishing sin interaccion", 3,
     r"\b(phishing|smishing|vishing|quishing)\b|correo (sospechoso|raro|falso|extrano)"
     r"|mensaje (sospechoso|raro)|codigo qr.{0,30}(correo|cartel|desconocid)"
     r"|no (le )?di (clic|click)|no lo abri"),
]

PATRONES_INCIDENTE = [
    (nombre, piso, re.compile(patron)) for nombre, piso, patron in CATEGORIAS_INCIDENTE
]

# Para tickets SIN ninguna señal de incidente, el rol limita el rango de prioridad.
# Ej.: "olvidé mi contraseña" -> 1-2 para un empleado, 3 (MEDIO) para un CEO.
RANGO_POR_ROL = {
    1: (1, 2),  # Empleado General
    2: (1, 2),  # Secretaria, Analista
    3: (2, 3),  # Supervisor
    4: (3, 4),  # Gerente, Admin TI
    5: (3, 4),  # CEO
}


def detectar_incidentes(titulo: str, texto: str) -> Dict[str, int]:
    """Devuelve {categoria: prioridad_minima} para cada tipo de incidente detectado."""
    contenido = normalizar_texto(f"{titulo} {texto}")
    return {nombre: piso for nombre, piso, patron in PATRONES_INCIDENTE if patron.search(contenido)}


def ajustar_prediccion_ml(
    prioridad_ml: int, titulo: str, texto: str, rol: RolUsuario, explicacion: Dict[str, float]
) -> Tuple[int, Dict[str, float]]:
    """
    Ajusta la prioridad del modelo ML:
    1. Si hay señales de incidente -> la prioridad nunca baja del piso de la categoría
       más grave (el modelo puede subirla, pero no bajarla).
    2. Sin señales -> ticket rutinario: se acota al rango permitido por el rol.
    """
    incidentes = detectar_incidentes(titulo, texto)
    explicacion = dict(explicacion)

    if incidentes:
        for nombre, piso in incidentes.items():
            explicacion[f"alerta: {nombre}"] = float(piso)
        return max(int(prioridad_ml), max(incidentes.values())), explicacion

    minimo, maximo = RANGO_POR_ROL[PESO_ROL[rol]]
    return max(minimo, min(int(prioridad_ml), maximo)), explicacion

