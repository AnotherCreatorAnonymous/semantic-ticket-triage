"use client";

import { PRIORITY_STYLES } from "@/lib/priority";
import { formatearFecha } from "@/lib/format";
import type { TicketResponse } from "@/types/api";
import { XaiChart } from "./XaiChart";
import { useState } from "react";

interface Props {
  ticket: TicketResponse;
  onDelete?: (id: string) => Promise<void>;
}

export function TicketCard({ ticket, onDelete }: Props) {
  const style = PRIORITY_STYLES[ticket.nivel_prioridad_texto];
  const [deleting, setDeleting] = useState(false);

  if (!style) return null;

  const handleDelete = async () => {
    if (!onDelete) return;
    if (!confirm("¿Eliminar este ticket?")) return;
    try {
      setDeleting(true);
      await onDelete(ticket.id);
    } catch (err) {
      console.error("Error al eliminar:", err);
      alert("Error al eliminar el ticket");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div
      className={`border-l-4 p-5 rounded-r-lg shadow-sm ${style.borderColor} ${style.bgColor} mb-4`}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${style.badgeColor} mb-2`}>
            {style.emoji} {ticket.nivel_prioridad_texto} · Prioridad {ticket.prioridad}
          </span>
          <h3 className="text-lg font-semibold text-gray-900 mt-2">{ticket.titulo}</h3>
        </div>
      </div>

      <div className="flex gap-4 text-sm text-gray-600 mb-3">
        <span>👤 {ticket.rol_usuario}</span>
        <span>🕒 {formatearFecha(ticket.creado_en)}</span>
      </div>

      <p className="text-gray-700 whitespace-pre-wrap mb-3">{ticket.texto}</p>

      <details className="mb-3 cursor-pointer group">
        <summary className="flex items-center gap-2 font-medium text-blue-600 hover:text-blue-700">
          <span className="group-open:rotate-90 inline-block transition-transform">▶</span>
          ¿Por qué esta prioridad?
        </summary>
        <div className="mt-4 p-3 bg-white rounded border border-gray-200">
          <XaiChart
            explicacion={ticket.explicacion_xai}
            nivel={ticket.nivel_prioridad_texto}
          />
        </div>
      </details>

      {onDelete && (
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 disabled:opacity-50"
        >
          {deleting ? "Eliminando..." : "Eliminar"}
        </button>
      )}
    </div>
  );
}
