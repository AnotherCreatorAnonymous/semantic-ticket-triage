export type NivelPrioridad = "BAJO" | "MEDIO" | "ALTO" | "CRÍTICO";
export type RolUsuario = "Empleado General" | "Analista / Contable" | "Supervisor / Coordinador" | "Gerente / Director" | "Administrador de TI" | "CEO / Alta Dirección";

export interface TicketResponse {
  id: string;
  titulo: string;
  creado_en: string;
  nivel_prioridad_texto: NivelPrioridad;
  prioridad: number;
  texto: string;
  rol_usuario: RolUsuario;
  explicacion_xai: Record<string, number>;
}

export interface TicketRequest {
  titulo: string;
  texto: string;
  rol_usuario: RolUsuario;
}

export interface QueueResponse {
  total: number;
  tickets: TicketResponse[];
}

export interface HealthResponse {
  status: string;
  model: "loaded" | "heuristic_fallback";
}
