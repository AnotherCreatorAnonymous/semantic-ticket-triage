export function parseXai(explicacion: Record<string, number>): Array<{
  factor: string;
  aporte: number;
  tipo: "rol" | "palabra_clave";
}> {
  const items = Object.entries(explicacion).map(([factor, aporte]) => ({
    factor,
    aporte,
    tipo: factor.startsWith("rol: ") ? ("rol" as const) : ("palabra_clave" as const),
  }));

  return items.sort((a, b) => a.aporte - b.aporte);
}

export function limpiarFactor(factor: string): string {
  return factor.replace(/^rol: /, "");
}
