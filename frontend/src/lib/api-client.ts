import type {
  QueueResponse,
  TicketRequest,
  TicketResponse,
  HealthResponse,
} from "@/types/api";

const TIMEOUT_MS = 5000;

const NOMBRES_CAMPOS: Record<string, string> = {
  titulo: "Título",
  texto: "Descripción",
  rol_usuario: "Rango / Rol",
};

export class BackendNoDisponible extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BackendNoDisponible";
  }
}

export class ErrorBackend extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ErrorBackend";
  }
}

export class ErrorValidacion extends Error {
  constructor(public errores: string[]) {
    super(errores.join("; "));
    this.name = "ErrorValidacion";
  }
}

async function request(
  method: string,
  ruta: string,
  body?: unknown
): Promise<Response> {
  try {
    return await fetch(ruta, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(TIMEOUT_MS),
      cache: "no-store",
    });
  } catch {
    throw new BackendNoDisponible(
      "No se pudo conectar con el backend"
    );
  }
}

function traducir422(
  detalle: Array<{ loc?: Array<string | number>; msg?: string }>
): string[] {
  return detalle.map((e) => {
    const campo = String(e.loc?.at(-1) ?? "?");
    return `${NOMBRES_CAMPOS[campo] ?? campo}: ${e.msg ?? "valor inválido"}`;
  });
}

async function json<T>(r: Response, etiqueta: string): Promise<T> {
  if (!r.ok) throw new ErrorBackend(`${etiqueta} respondió ${r.status}`);
  return r.json();
}

export async function obtenerRoles(): Promise<string[]> {
  const r = await request("GET", "/api/roles");
  return json<string[]>(r, "GET /api/roles");
}

export async function obtenerCola(): Promise<QueueResponse> {
  const r = await request("GET", "/api/queue");
  return json<QueueResponse>(r, "GET /api/queue");
}

export async function obtenerHealth(): Promise<HealthResponse> {
  const r = await request("GET", "/api/health");
  return json<HealthResponse>(r, "GET /api/health");
}

export async function enviarTicket(t: TicketRequest): Promise<TicketResponse> {
  const r = await request("POST", "/api/triage", t);
  if (r.status === 422) {
    const body = await r.json();
    throw new ErrorValidacion(
      traducir422(body.detail ?? [])
    );
  }
  return json<TicketResponse>(r, "POST /api/triage");
}

export async function eliminarTicket(id: string): Promise<void> {
  const r = await request("DELETE", `/api/queue/${encodeURIComponent(id)}`);
  if (r.status === 404) return;
  await json(r, `DELETE /api/queue/${id}`);
}
