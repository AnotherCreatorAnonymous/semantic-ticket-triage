export function formatearFecha(isoUtc: string): string {
  try {
    const fecha = new Date(isoUtc);
    return fecha.toLocaleString("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "America/Bogota",
    });
  } catch {
    return isoUtc;
  }
}
