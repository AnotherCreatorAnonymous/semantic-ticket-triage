from api.schemas import RolUsuario
from core.triage_rules import calcular_prioridad


def payload(titulo, texto, rol_usuario="Empleado General"):
    return {
        "titulo": titulo,
        "texto": texto,
        "rol_usuario": rol_usuario,
    }


def test_antivirus_no_cuenta_como_virus():
    prioridad, explicacion = calcular_prioridad("Problema PC", "el antivirus pide actualizar", RolUsuario.EMPLEADO)
    assert prioridad == 1
    assert "virus" not in explicacion


def test_rol_invalido_devuelve_422(client):
    payload = {"titulo": "Hola mundo", "texto": "Necesito ayuda urgente", "rol_usuario": "Rey del Universo"}
    response = client.post("/api/triage", json=payload)
    assert response.status_code == 422


def test_texto_en_blanco_devuelve_422(client):
    response = client.post("/api/triage", json=payload("Problema de VPN", "   "))

    assert response.status_code == 422


def test_palabra_critica_en_titulo(client):
    response = client.post(
        "/api/triage",
        json=payload("RANSOMWARE en equipo", "Se detecto una amenaza", "Empleado General"),
    )

    assert response.status_code == 200
    assert response.json()["prioridad"] == 3


def test_extension_lock_es_critica(client):
    response = client.post(
        "/api/triage",
        json=payload("Archivos bloqueados", "El informe.lock no puede abrirse"),
    )

    assert response.status_code == 200
    assert response.json()["prioridad"] == 3
    assert response.json()["explicacion_xai"][".lock"] == 2


def test_sin_tildes_detecta_contrasena(client):
    respuesta_con_tilde = client.post(
        "/api/triage",
        json=payload("Problema de acceso", "La contraseña esta bloqueada"),
    )
    respuesta_sin_tilde = client.post(
        "/api/triage",
        json=payload("Problema de acceso", "La contrasena esta bloqueada"),
    )

    assert respuesta_con_tilde.status_code == 200
    assert respuesta_sin_tilde.status_code == 200
    assert respuesta_con_tilde.json()["prioridad"] == respuesta_sin_tilde.json()["prioridad"]


def test_cola_ordenada_por_prioridad(client):
    client.post(
        "/api/triage",
        json=payload("Consulta de monitor", "La pantalla no enciende"),
    )
    client.post(
        "/api/triage",
        json=payload("Alerta de ransomware", "Se detecto malware"),
    )

    response = client.get("/api/queue")

    assert response.status_code == 200
    tickets = response.json()["tickets"]
    assert tickets[0]["prioridad"] > tickets[1]["prioridad"]
    assert tickets[0]["titulo"] == "Alerta de ransomware"


def test_empate_respeta_orden_de_llegada(client):
    client.post(
        "/api/triage",
        json=payload("Consulta de monitor", "La pantalla no enciende"),
    )
    client.post(
        "/api/triage",
        json=payload("Consulta de teclado", "La tecla espacio no funciona"),
    )

    response = client.get("/api/queue")

    assert response.status_code == 200
    tickets = response.json()["tickets"]
    assert [ticket["titulo"] for ticket in tickets] == [
        "Consulta de monitor",
        "Consulta de teclado",
    ]


def test_roles_endpoint(client):
    response = client.get("/api/roles")

    assert response.status_code == 200
    assert len(response.json()) == 6