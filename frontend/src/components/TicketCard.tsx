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
      alert("Error al eliminar el ticket");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className={`border-l-4 p-6 rounded-xl shadow-lg transition-all ${style.borderColor} ${style.bgColor} mb-4 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 hover:border-slate-600 hover:shadow-xl`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-bold ${style.badgeColor} mb-3`}>
            {style.emoji} {ticket.nivel_prioridad_texto} · Nivel {ticket.prioridad}
          </span>
          <h3 className="text-xl font-bold text-white mt-2">{ticket.titulo}</h3>
        </div>
      </div>

      <div className="flex gap-6 text-sm text-slate-400 mb-4">
        <span className="flex items-center gap-2">👤 <span className="text-slate-300">{ticket.rol_usuario}</span></span>
        <span className="flex items-center gap-2">🕒 <span className="text-slate-300">{formatearFecha(ticket.creado_en)}</span></span>
      </div>

      <p className="text-slate-300 whitespace-pre-wrap mb-4 leading-relaxed">{ticket.texto}</p>

      <details className="mb-4 cursor-pointer group">
        <summary className="flex items-center gap-2 font-semibold text-blue-400 hover:text-blue-300 transition-colors">
          <span className="group-open:rotate-90 inline-block transition-transform">▶</span>
          ¿Por qué esta prioridad?
        </summary>
        <div className="mt-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
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
          className="px-4 py-2 text-sm bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 hover:text-red-300 disabled:opacity-50 transition-all font-medium border border-red-500/30"
        >
          {deleting ? "Eliminando..." : "🗑️ Eliminar"}
        </button>
      )}
    </div>
  );
}
