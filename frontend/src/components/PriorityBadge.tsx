"use client";

import { PRIORITY_STYLES } from "@/lib/priority";
import type { NivelPrioridad } from "@/types/api";

interface Props {
  nivel: NivelPrioridad;
  prioridad: number;
}

export function PriorityBadge({ nivel, prioridad }: Props) {
  const style = PRIORITY_STYLES[nivel];
  if (!style) return null;

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${style.badgeColor}`}>
      {style.emoji} {nivel} · Prioridad {prioridad}
    </span>
  );
}
