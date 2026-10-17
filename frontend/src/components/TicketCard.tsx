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
  const [expanded, setExpanded] = useState(false);

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
    <div 
      className={`border-l-8 p-6 rounded-2xl shadow-xl transition-all duration-300 mb-5 cursor-pointer
        hover:shadow-2xl hover:scale-[1.01] transform
        ${style.borderColor} ${style.bgColor}
        bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm
        hover:from-white/20 hover:to-white/10
      `}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className={`inline-flex items-center gap-3 px-4 py-2 rounded-full text-sm font-bold ${style.badgeColor} mb-4 shadow-lg`}>
            <span className="text-lg">{style.emoji}</span>
            <span>{ticket.nivel_prioridad_texto}</span>
            <span className="ml-2 px-2 py-0.5 bg-white/20 rounded text-xs font-bold">Prioridad {ticket.prioridad}/5</span>
          </div>
          <h3 className={`text-2xl font-bold mt-3 transition-colors ${style.color} text-white`}>
            {ticket.titulo}
          </h3>
        </div>
        <div className="text-2xl opacity-60">
          {expanded ? "▼" : "▶"}
        </div>
      </div>

      <div className="flex flex-wrap gap-6 text-sm mb-5">
        <div className="flex items-center gap-2">
          <span className="text-lg">👤</span>
          <div>
            <p className="text-slate-400 text-xs">Reportado por</p>
            <p className="text-white font-bold">{ticket.rol_usuario}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg">🕒</span>
          <div>
            <p className="text-slate-400 text-xs">Fecha</p>
            <p className="text-white font-bold">{formatearFecha(ticket.creado_en)}</p>
          </div>
        </div>
      </div>

      <div className={`${style.bgColor} p-4 rounded-xl mb-5 border-l-4 ${style.borderColor}`}>
        <p className="text-white whitespace-pre-wrap leading-relaxed text-sm font-medium">
          {ticket.texto}
        </p>
      </div>

      {expanded && (
        <div className="mt-6 pt-6 border-t-2 border-white/10 animate-in fade-in duration-300">
          <h4 className="text-white font-bold mb-4 text-lg">🔍 Análisis de Prioridad</h4>
          <div className="bg-slate-900/50 p-4 rounded-xl">
            <XaiChart
              explicacion={ticket.explicacion_xai}
              nivel={ticket.nivel_prioridad_texto}
            />
          </div>
        </div>
      )}

      {onDelete && (
        <div className="flex gap-3 mt-6">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete();
            }}
            disabled={deleting}
            className="flex-1 px-4 py-3 text-sm bg-red-500/30 text-red-300 hover:bg-red-500/50 hover:text-red-100 disabled:opacity-50 transition-all font-bold border border-red-500/50 rounded-lg hover:shadow-lg"
          >
            {deleting ? "🔄 Eliminando..." : "🗑️ Eliminar Ticket"}
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
            className="px-4 py-3 text-sm bg-blue-500/30 text-blue-300 hover:bg-blue-500/50 transition-all font-bold border border-blue-500/50 rounded-lg hover:shadow-lg"
          >
            {expanded ? "📖 Contraer" : "📖 Detalles"}
          </button>
        </div>
      )}
    </div>
  );
}
