"use client";

import { PRIORITY_STYLES } from "@/lib/priority";
import { formatearFecha } from "@/lib/format";
import type { TicketResponse } from "@/types/api";
import type { NewTicketInfo } from "@/context/QueueContext";
import { XaiChart } from "./XaiChart";
import { useState } from "react";

interface Props {
  ticket: TicketResponse;
  onDelete?: (id: string) => Promise<void>;
  newInfo?: NewTicketInfo | null;
}

export function TicketCard({ ticket, onDelete, newInfo }: Props) {
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

  const isNew = Boolean(newInfo);

  return (
    <div 
      className={`group mb-6 cursor-pointer transition-all duration-300 transform hover:scale-[1.01]`}
      onClick={() => setExpanded(!expanded)}
    >
      {/* Card Container */}
      <div className={`
        relative overflow-hidden rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500
        bg-gradient-to-br border-2
        ${isNew ? 'ring-2 ring-cyan-400/90 shadow-[0_0_25px_rgba(6,182,212,0.35)] animate-pulse-subtle' : ''}
        ${style.hex === '#dc2626' ? 'from-red-900/20 to-red-800/10 border-red-500/40 hover:border-red-500/60' : ''}
        ${style.hex === '#ea580c' ? 'from-orange-900/20 to-orange-800/10 border-orange-500/40 hover:border-orange-500/60' : ''}
        ${style.hex === '#ca8a04' ? 'from-amber-900/20 to-amber-800/10 border-amber-500/40 hover:border-amber-500/60' : ''}
        ${style.hex === '#65a30d' ? 'from-lime-900/20 to-lime-800/10 border-lime-500/40 hover:border-lime-500/60' : ''}
        ${style.hex === '#059669' ? 'from-emerald-900/20 to-emerald-800/10 border-emerald-500/40 hover:border-emerald-500/60' : ''}
      `}>
        {/* Accent Bar */}
        <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${
          style.hex === '#dc2626' ? 'from-red-500 to-red-400' :
          style.hex === '#ea580c' ? 'from-orange-500 to-orange-400' :
          style.hex === '#ca8a04' ? 'from-amber-500 to-amber-400' :
          style.hex === '#65a30d' ? 'from-lime-500 to-lime-400' :
          'from-emerald-500 to-emerald-400'
        }`} />

        {/* Content */}
        <div className="p-6">
          {/* Header Row */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-3 mb-3">
                {/* Priority Badge */}
                <div className={`inline-flex items-center gap-3 px-4 py-2 rounded-full text-sm font-bold ${style.badgeColor} shadow-lg backdrop-blur-sm bg-opacity-90`}>
                  <span className="text-lg">{style.emoji}</span>
                  <span className="text-xs uppercase tracking-wider">{ticket.nivel_prioridad_texto}</span>
                  <span className="ml-2 px-2.5 py-0.5 bg-white/20 rounded-full text-xs font-bold border border-white/30">
                    {ticket.prioridad}/5
                  </span>
                </div>

                {/* Badge NUEVO con temporizador según origen */}
                {newInfo && (
                  newInfo.source === "local" ? (
                    <div 
                      title="Ticket generado en esta misma pantalla. El indicador desaparece a los 60 segundos."
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-black bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white shadow-lg border border-emerald-300/40 animate-pulse"
                    >
                      <span className="w-2 h-2 rounded-full bg-white animate-ping" />
                      <span>✨ NUEVO</span>
                      <span className="text-[11px] bg-black/30 px-2 py-0.5 rounded-full font-mono font-bold tracking-tight">
                        {newInfo.secondsRemaining}s
                      </span>
                    </div>
                  ) : (
                    <div 
                      title={
                        newInfo.interactionStartedAt
                          ? `Generado desde el backend u otra pantalla. Desaparece en ${newInfo.secondsRemaining}s tras tu interacción.`
                          : "Generado desde el backend u otra pantalla. El contador de 1 minuto comenzará cuando interactúes con la pantalla."
                      }
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-black bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 text-white shadow-lg border border-cyan-300/40"
                    >
                      <span className="w-2 h-2 rounded-full bg-cyan-200 animate-ping" />
                      <span>✨ NUEVO (Remoto)</span>
                      {newInfo.interactionStartedAt ? (
                        <span className="text-[11px] bg-black/30 px-2 py-0.5 rounded-full font-mono font-bold tracking-tight">
                          {newInfo.secondsRemaining}s
                        </span>
                      ) : (
                        <span className="text-[11px] bg-amber-400 text-slate-900 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider animate-bounce">
                          ¡Por revisar!
                        </span>
                      )}
                    </div>
                  )
                )}
              </div>
              
              {/* Title */}
              <h3 className="text-2xl font-bold text-white leading-tight mt-3 transition-colors">
                {ticket.titulo}
              </h3>
            </div>


            {/* Expand Arrow */}
            <div className={`text-2xl opacity-40 group-hover:opacity-100 transition-all transform ${expanded ? 'rotate-180' : ''} ml-4`}>
              ▼
            </div>
          </div>

          {/* Metadata Row */}
          <div className="flex flex-wrap gap-8 mb-6 pb-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <span className="text-2xl">👤</span>
              <div>
                <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">Reportado por</p>
                <p className="text-white font-bold text-lg">{ticket.rol_usuario}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl">🕐</span>
              <div>
                <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">Fecha</p>
                <p className="text-white font-bold text-lg">{formatearFecha(ticket.creado_en)}</p>
              </div>
            </div>
          </div>

          {/* Description Box */}
          <div className={`p-5 rounded-xl mb-6 border-l-4 ${style.borderColor} backdrop-blur-sm bg-white/5 border border-white/10`}>
            <p className="text-white whitespace-pre-wrap leading-relaxed text-base font-medium">
              {ticket.texto}
            </p>
          </div>

          {/* Expanded Content */}
          {expanded && (
            <div className="mt-8 pt-8 border-t border-white/20 animate-in fade-in duration-300 space-y-4">
              <h4 className="text-white font-bold text-lg flex items-center gap-2">
                🔍 Análisis de Prioridad
              </h4>
              <div className="bg-slate-900/80 p-6 rounded-xl border border-white/10 backdrop-blur-sm">
                <XaiChart
                  explicacion={ticket.explicacion_xai}
                  nivel={ticket.nivel_prioridad_texto}
                />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 mt-6 pt-6 border-t border-white/10">
            {onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete();
                }}
                disabled={deleting}
                className={`flex-1 px-4 py-3 text-sm font-bold rounded-lg transition-all duration-300 border
                  ${deleting ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg'}
                  ${style.hex === '#dc2626' ? 'bg-red-500/20 text-red-300 border-red-500/40 hover:bg-red-500/30 hover:text-red-100' :
                    style.hex === '#ea580c' ? 'bg-orange-500/20 text-orange-300 border-orange-500/40 hover:bg-orange-500/30 hover:text-orange-100' :
                    'bg-red-500/20 text-red-300 border-red-500/40 hover:bg-red-500/30 hover:text-red-100'}
                `}
              >
                {deleting ? '🔄 Eliminando...' : '🗑️ Eliminar'}
              </button>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="flex-1 px-4 py-3 text-sm font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40 rounded-lg hover:bg-blue-500/30 hover:text-blue-100 transition-all duration-300 hover:shadow-lg"
            >
              {expanded ? '📖 Cerrar' : '📖 Detalles'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
