# 🏷️ Guía de Etiquetado de Tickets

Criterio único para asignar la **prioridad real (1–5)** a cada ticket del dataset. Todo integrante que etiquete tickets debe seguir esta guía, de modo que dos personas distintas lleguen a la misma etiqueta.

> **Regla de oro:** la prioridad mide el **riesgo real del incidente**, no lo importante que es quien lo reporta. El rol solo agrava incidentes de **seguridad**, porque una cuenta privilegiada comprometida tiene más alcance.

---

## Paso 1 — Nivel base según el incidente (ignorando el rol)

| Nivel | Nombre | Criterio | Ejemplos |
|:-----:|--------|----------|----------|
| **5** | Crítico | Incidente de seguridad **activo y confirmado** con impacto en datos u operación, o caída total de un servicio crítico para toda la organización | Archivos cifrados / extensión `.lock` / nota de rescate; exfiltración de datos; cuenta usada para transferencias o envíos masivos; servidor principal caído para todos |
| **4** | Alto | Incidente de seguridad **probable** sobre un usuario o equipo, o un sistema crítico caído para un área completa | Clic en phishing **y** credenciales ingresadas; antivirus detecta malware activo; inicio de sesión desde otro país; ERP/nómina caído para todo un departamento |
| **3** | Medio | **Sospecha** de seguridad sin evidencia de compromiso, o falla que **impide trabajar** a una persona sin alternativa | Correo sospechoso recibido (sin clic); USB desconocida encontrada; cuenta bloqueada; equipo no enciende; VPN caída para un usuario remoto |
| **2** | Bajo | Falla o degradación **con alternativa** (se puede seguir trabajando) | Lentitud; impresora atascada; Outlook se cierra a veces; monitor parpadea; Wi-Fi intermitente en una sala |
| **1** | Muy bajo | **Solicitud** o consulta sin falla real, o tema estético | Instalar un programa; cambiar fondo de pantalla; pedir un mouse nuevo; preguntar cómo configurar la firma del correo |

---

## Paso 2 — Ajuste por rol (solo incidentes de seguridad)

Si el ticket es **de seguridad** (`categoria = "seguridad"`) y el nivel base es **3 o 4**, se suma **+1** cuando el rol es uno de:

- **CEO / Alta Dirección**
- **Gerente / Director**
- **Administrador de TI**

Motivo: estas cuentas tienen acceso a información sensible, aprobaciones financieras o privilegios de administración, así que un compromiso tiene mayor alcance.

| Caso | Base | Ajuste | Final |
|------|:----:|:------:|:-----:|
| Empleado recibe correo sospechoso (sin clic) | 3 | — | **3** |
| CEO recibe correo sospechoso (sin clic) | 3 | +1 | **4** |
| Gerente ingresó su clave en un phishing | 4 | +1 | **5** |
| Empleado con archivos `.lock` (ransomware) | 5 | — | **5** |
| CEO pide cambiar el fondo de pantalla | 1 | — (no es seguridad) | **1** |
| CEO con el portátil lento | 2 | — (no es seguridad) | **2** |

> ⚠️ Los dos últimos casos son **intencionales**: sirven para medir si un modelo aprende el **sesgo por cargo** (darle prioridad alta a todo lo que reporta un directivo).

---

## Paso 3 — Categoría

| Categoría | Cuándo |
|-----------|--------|
| `seguridad` | Hay indicio de amenaza: malware, phishing, accesos extraños, pérdida o robo de datos o equipos, ingeniería social |
| `operativo` | Algo dejó de funcionar o funciona mal, sin indicio de amenaza |
| `solicitud` | Pedido o consulta; nada está fallando |

---

## Paso 4 — ¿Es ambiguo?

Marca `"ambiguo": true` cuando el ticket esté **mal escrito, sea muy vago, use jerga o no deje claro si es seguridad**. Ejemplos: `"no me sirve nada ayuda"`, `"me salio un mensaje raro pidiendo plata"`. Etiquétalo con la **interpretación más probable** y explica tu decisión en `nota`.

Objetivo: **≥ 20 %** del dataset ambiguo. Los usuarios reales escriben así, y la investigación lo señala como el caso más difícil.

---

## Formato de cada ticket (`sample_tickets.json`)

```json
{
  "id": "T001",
  "titulo": "Archivos con extensión .lock",
  "texto": "Desde esta mañana ningún archivo abre y todos terminan en .lock",
  "rol_usuario": "Empleado General",
  "categoria": "seguridad",
  "prioridad": 5,
  "ambiguo": false,
  "nota": ""
}
```

| Campo | Regla |
|-------|-------|
| `titulo` | 5–100 caracteres (igual que la API) |
| `texto` | 10–2000 caracteres (igual que la API) |
| `rol_usuario` | Uno de los 6 roles exactos de `GET /api/roles` |
| `prioridad` | Resultado de los Pasos 1 y 2 |
| `nota` | Obligatoria si `ambiguo` es `true` |

Valida el archivo con:

```bash
python evaluation/validate_dataset.py
```

---

## Buenas prácticas

- **Vocabulario variado:** no repitas siempre "ransomware" para los nivel 5. Usa "archivos cifrados", "nota de rescate", "piden bitcoin"… Si cada nivel usa palabras fijas, el modelo memoriza palabras en lugar de aprender, y el F1 sale inflado.
- **Todos los roles en todos los niveles**, siempre que la regla lo permita.
- **Revisión cruzada:** que otra persona re-etiquete unos 20 tickets al azar sin ver la etiqueta original. Si coinciden menos del 80 %, la guía necesita aclararse.
