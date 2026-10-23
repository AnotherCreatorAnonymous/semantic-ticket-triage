"""
Amplía evaluation/sample_tickets.json con incidentes de ciberseguridad que el
dataset original no cubría y con casos de contraste por rol.

Es idempotente: si un título + rol ya existe, no lo vuelve a agregar.
Uso: python evaluation/ampliar_dataset.py
"""
import json
from pathlib import Path

DATASET = Path(__file__).parent / "sample_tickets.json"

EMP, SEC, ANA = "Empleado General", "Secretaria", "Analista / Contable"
SUP, GER, ADM, CEO = "Supervisor / Coordinador", "Gerente / Director", "Administrador de TI", "CEO / Alta Dirección"

# (titulo, texto, rol, prioridad, categoria, nota)
NUEVOS = [
    # --- Ataques a infraestructura / aplicaciones ---
    ("Página caída por ataque", "El proveedor de hosting dice que estamos recibiendo un ataque DDoS y la tienda en línea no carga.", ADM, 5, "seguridad", "DDoS"),
    ("Errores raros en el formulario web", "En los logs del portal veo peticiones con ' OR 1=1 y comandos SQL en el campo de usuario.", ADM, 5, "seguridad", "inyección SQL"),
    ("Actualización del software contable sospechosa", "El proveedor del software contable avisó que su última actualización traía código malicioso y ya la instalamos en todos los equipos.", ADM, 5, "seguridad", "cadena de suministro"),
    ("Claves de AWS en GitHub", "Un desarrollador subió por error las claves de AWS a un repositorio público de GitHub.", ADM, 5, "seguridad", "secretos filtrados"),
    ("Bucket con documentos público", "Descubrimos que el bucket de S3 con contratos firmados estaba público desde hace meses.", ADM, 5, "seguridad", "nube mal configurada"),
    ("Usuario administrador que nadie creó", "En el directorio activo apareció un usuario administrador nuevo que nadie de TI creó.", ADM, 5, "seguridad", "persistencia / cuenta falsa"),
    ("Alertas de inicios fallidos en Microsoft 365", "Microsoft 365 muestra miles de intentos fallidos contra muchas cuentas desde varios países.", ADM, 4, "seguridad", "password spraying"),
    ("Wifi con el nombre de la empresa", "En la cafetería del edificio aparece una red wifi abierta con el nombre de la empresa y no es la nuestra.", ADM, 4, "seguridad", "evil twin"),
    ("Los discos aparecen vacíos", "Varios equipos reiniciaron solos y ahora los discos aparecen vacíos, se borró todo.", SUP, 5, "seguridad", "wiper"),
    ("La intranet lleva a otro sitio", "Cuando escribo la dirección de la intranet me lleva a una página parecida que me pide la clave.", EMP, 4, "seguridad", "DNS hijacking / pharming"),

    # --- Cuentas y autenticación ---
    ("Me llegan muchas notificaciones de aprobación", "El celular no para de pedirme aprobar inicios de sesión que no estoy haciendo, ya van como 20.", GER, 4, "seguridad", "fatiga MFA"),
    ("le di aprobar sin querer", "me llegaban muchas notificaciones de autenticacion y por error le di aprobar a una.", EMP, 5, "seguridad", "fatiga MFA consumada"),
    ("Mi celular se quedó sin señal", "De repente el celular corporativo se quedó sin señal y luego me llegó un correo de que cambiaron la clave del banco.", CEO, 5, "seguridad", "SIM swap"),
    ("Sesión abierta en un dispositivo desconocido", "En la lista de sesiones activas de mi correo aparece una sesión en un dispositivo que no conozco.", GER, 5, "seguridad", "robo de sesión"),

    # --- Ingeniería social ---
    ("Llamada con la voz del gerente", "Me llamaron con una voz idéntica a la del gerente general pidiendo una transferencia urgente a un proveedor nuevo.", ANA, 4, "seguridad", "deepfake de voz"),
    ("Proveedor cambió la cuenta bancaria", "Un proveedor escribió pidiendo que le paguemos a una cuenta bancaria nueva, el correo se ve un poco distinto.", ANA, 4, "seguridad", "BEC / fraude de proveedor"),
    ("Ventana dice que tengo virus y que llame", "Salió una ventana con alarma diciendo que mi pc tiene virus y que llame a un número de soporte técnico de Microsoft.", SEC, 4, "seguridad", "falso soporte técnico"),
    ("Me pidieron instalar AnyDesk", "Me llamaron del banco y me pidieron instalar AnyDesk para ayudarme; ya lo instalé y se conectaron a mi equipo.", ANA, 5, "seguridad", "acceso remoto fraudulento"),
    ("Código QR en el parqueadero", "Hay carteles con un código QR para registrar el carro en el parqueadero; lleva a una página que pide el usuario corporativo.", SUP, 3, "seguridad", "quishing"),
    ("SMS de paquete retenido", "Me llegó un mensaje de texto diciendo que tengo un paquete retenido y que pague en un link, no lo abrí.", EMP, 3, "seguridad", "smishing sin interacción"),
    ("Correo raro pidiendo validar cuenta", "Me llegó un correo raro pidiendo validar mi cuenta de correo, no le di clic.", CEO, 3, "seguridad", "phishing sin interacción"),

    # --- Amenaza interna y física ---
    ("Excompañero descargó la base de clientes", "Vimos que un empleado que renunció descargó toda la base de clientes a una USB su último día.", GER, 5, "seguridad", "amenaza interna"),
    ("Envía archivos a su correo personal", "Un analista está enviando archivos de clientes a su correo personal todos los días.", SUP, 4, "seguridad", "fuga interna"),
    ("Aparato entre el teclado y el pc", "Encontré un aparatito conectado entre el cable del teclado y el computador de recepción.", SEC, 5, "seguridad", "keylogger físico"),
    ("Persona desconocida en el cuarto de servidores", "Vi a alguien desconocido saliendo del cuarto de servidores sin carnet.", SUP, 5, "seguridad", "acceso físico"),

    # --- Malware en endpoint ---
    ("Extensión rara en el navegador", "Apareció una extensión en Chrome que no instalé y me cambia los resultados de búsqueda.", EMP, 3, "seguridad", "extensión maliciosa"),
    ("Ventilador a tope todo el día", "El portátil está siempre lento y el ventilador a tope; el administrador de tareas muestra un proceso desconocido usando toda la CPU.", EMP, 4, "seguridad", "posible criptominería"),
    ("me sale un candado", "no me deja entrar, sale un candado rojo y dice que pague para recuperar mis datos.", SEC, 5, "seguridad", "ransomware (lenguaje informal)"),
    ("el fondo de pantalla cambió solo", "el fondo de pantalla cambió solo a un mensaje que dice que mis archivos están secuestrados.", EMP, 5, "seguridad", "ransomware (lenguaje informal)"),

    # --- Contrastes por rol: mismo problema rutinario, distinta prioridad ---
    ("olvidé mi contraseña", "No puedo entrar al computador porque olvidé la contraseña.", EMP, 1, "soporte", "contraste por rol"),
    ("olvidé mi clave", "hola no puedo usar mi pc porque olvidé mi clave.", SEC, 2, "soporte", "contraste por rol"),
    ("No recuerdo la contraseña", "No recuerdo la contraseña del correo, necesito que me la restablezcan.", ANA, 2, "soporte", "contraste por rol"),
    ("Restablecer contraseña", "Olvidé la contraseña de mi equipo, por favor restablecerla.", SUP, 2, "soporte", "contraste por rol"),
    ("Olvidé la contraseña del equipo", "Olvidé la contraseña y no puedo entrar al computador.", GER, 3, "soporte", "contraste por rol"),
    ("olvidé mi contraseña", "No puedo entrar a mi equipo porque olvidé la contraseña y tengo junta en 20 minutos.", CEO, 3, "soporte", "contraste por rol"),
    ("Cambiar fondo de pantalla", "Quiero poner el logo nuevo de la empresa como fondo de pantalla.", EMP, 1, "soporte", "contraste por rol"),
    ("Cambiar fondo de pantalla", "Quiero poner el logo nuevo de la empresa como fondo de pantalla.", CEO, 2, "soporte", "contraste por rol"),
    ("La impresora no imprime", "La impresora de mi puesto no imprime, sale papel en blanco.", SEC, 2, "soporte", "contraste por rol"),
    ("La impresora no imprime", "La impresora de mi oficina no imprime y necesito el contrato para firmar hoy.", CEO, 3, "soporte", "contraste por rol"),
]


def main():
    tickets = json.loads(DATASET.read_text(encoding="utf-8"))
    existentes = {(t["titulo"], t["rol_usuario"]) for t in tickets}
    siguiente = max(int(t["id"][1:]) for t in tickets) + 1

    agregados = 0
    for titulo, texto, rol, prioridad, categoria, nota in NUEVOS:
        if (titulo, rol) in existentes:
            continue
        tickets.append({
            "id": f"T{siguiente}",
            "titulo": titulo,
            "texto": texto,
            "rol_usuario": rol,
            "categoria": categoria,
            "prioridad": prioridad,
            "ambiguo": False,
            "nota": f"ampliación: {nota}",
        })
        siguiente += 1
        agregados += 1

    DATASET.write_text(json.dumps(tickets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Agregados {agregados} tickets. Total: {len(tickets)}")


if __name__ == "__main__":
    main()
