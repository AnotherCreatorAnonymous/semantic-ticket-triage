# evaluation/validate_dataset.py
"""Valida sample_tickets.json contra GUIA_ETIQUETADO.md. Solo usa la librería estándar.

Uso (desde la raíz del repo):  python evaluation/validate_dataset.py
Sale con código 1 si encuentra errores, para poder usarlo en CI.
"""
import json
import sys
from collections import Counter
from pathlib import Path

RUTA_DATASET = Path(__file__).parent / "sample_tickets.json"

# Deben coincidir con RolUsuario y TicketRequest en backend/api/schemas.py
ROLES = {
    "Empleado General",
    "Analista / Contable",
    "Supervisor / Coordinador",
    "Gerente / Director",
    "Administrador de TI",
    "CEO / Alta Dirección",
}
ROLES_PRIVILEGIADOS = {"CEO / Alta Dirección", "Gerente / Director", "Administrador de TI"}
TITULO_MIN, TITULO_MAX = 5, 100
TEXTO_MIN, TEXTO_MAX = 10, 2000

CATEGORIAS = {"seguridad", "operativo", "solicitud"}
CAMPOS = {"id", "titulo", "texto", "rol_usuario", "categoria", "prioridad", "ambiguo", "nota"}
MIN_PORCENTAJE_AMBIGUOS = 20


def validar_ticket(t: dict) -> list:
    errores = []
    faltantes = CAMPOS - t.keys()
    if faltantes:
        return [f"faltan campos: {sorted(faltantes)}"]

    if not TITULO_MIN <= len(t["titulo"].strip()) <= TITULO_MAX:
        errores.append(f"titulo debe tener {TITULO_MIN}-{TITULO_MAX} caracteres")
    if not TEXTO_MIN <= len(t["texto"].strip()) <= TEXTO_MAX:
        errores.append(f"texto debe tener {TEXTO_MIN}-{TEXTO_MAX} caracteres")
    if t["rol_usuario"] not in ROLES:
        errores.append(f"rol desconocido: {t['rol_usuario']!r}")
    if t["categoria"] not in CATEGORIAS:
        errores.append(f"categoria desconocida: {t['categoria']!r}")
    if t["prioridad"] not in {1, 2, 3, 4, 5}:
        errores.append(f"prioridad fuera de rango: {t['prioridad']!r}")
    if not isinstance(t["ambiguo"], bool):
        errores.append("ambiguo debe ser true/false")
    if t["ambiguo"] and not t["nota"].strip():
        errores.append("un ticket ambiguo necesita una nota que justifique la etiqueta")

    # Reglas de la guía que se pueden comprobar sin leer el texto
    if t["categoria"] == "solicitud" and t["prioridad"] != 1:
        errores.append("una solicitud siempre es prioridad 1 (Paso 1)")
    if t["categoria"] == "operativo" and t["prioridad"] == 1:
        errores.append("un problema operativo es al menos prioridad 2 (Paso 1)")
    if t["categoria"] == "seguridad" and t["prioridad"] < 3:
        errores.append("un ticket de seguridad es al menos prioridad 3 (Paso 1)")
    if t["categoria"] == "seguridad" and t["prioridad"] == 3 and t["rol_usuario"] in ROLES_PRIVILEGIADOS:
        errores.append("seguridad base 3 con rol privilegiado debe subir a 4 (Paso 2)")
    return errores


def main() -> int:
    tickets = json.loads(RUTA_DATASET.read_text(encoding="utf-8"))
    errores = []

    for t in tickets:
        errores += [f"{t.get('id', '?')}: {e}" for e in validar_ticket(t)]

    ids = Counter(t.get("id") for t in tickets)
    errores += [f"id repetido: {i}" for i, n in ids.items() if n > 1]
    textos = Counter(t.get("texto", "").strip().lower() for t in tickets)
    errores += [f"texto repetido: {x[:50]!r}" for x, n in textos.items() if n > 1]

    total = len(tickets)
    ambiguos = sum(1 for t in tickets if t.get("ambiguo"))
    porcentaje_ambiguos = 100 * ambiguos / total if total else 0
    if porcentaje_ambiguos < MIN_PORCENTAJE_AMBIGUOS:
        errores.append(f"solo {porcentaje_ambiguos:.0f}% ambiguos (mínimo {MIN_PORCENTAJE_AMBIGUOS}%)")

    print(f"📄 {RUTA_DATASET.name}: {total} tickets, {ambiguos} ambiguos ({porcentaje_ambiguos:.0f}%)\n")
    print("Prioridad  Tickets  Seguridad  Operativo  Solicitud")
    for nivel in range(1, 6):
        del_nivel = [t for t in tickets if t.get("prioridad") == nivel]
        cats = Counter(t.get("categoria") for t in del_nivel)
        print(f"    {nivel}       {len(del_nivel):>4}     {cats['seguridad']:>5}      {cats['operativo']:>5}      {cats['solicitud']:>5}")

    print("\nRoles:")
    for rol, n in Counter(t.get("rol_usuario") for t in tickets).most_common():
        print(f"  {n:>3}  {rol}")

    if errores:
        print(f"\n❌ {len(errores)} error(es):")
        for e in errores:
            print(f"  - {e}")
        return 1
    print("\n✅ Dataset válido según GUIA_ETIQUETADO.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
