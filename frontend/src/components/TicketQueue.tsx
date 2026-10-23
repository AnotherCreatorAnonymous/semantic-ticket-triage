"use client";

import { useQueue } from "@/hooks/useQueue";
import { TicketCard } from "./TicketCard";
import { Pagination } from "./Pagination";
import { Alert } from "./ui/Alert";
import { useState, useMemo } from "react";

const PAGE_SIZE = 15;

export function TicketQueue() {
  const { tickets, total, error, isLoading, borrar, getTicketNewInfo, isLive, totalNewCount } = useQueue();
  const [page, setPage] = useState(1);
  const [criterioOrden, setCriterioOrden] = useState<"recientes" | "prioridad">("recientes");

  const ticketsOrdenados = useMemo(() => {
    return [...tickets].sort((a, b) => {
      if (criterioOrden === "recientes") {
        return new Date(b.creado_en).getTime() - new Date(a.creado_en).getTime();
      }
      return b.prioridad - a.prioridad;
    });
  }, [tickets, criterioOrden]);

  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return ticketsOrdenados.slice(start, start + PAGE_SIZE);
  }, [ticketsOrdenados, page]);

  const totalPages = Math.ceil(ticketsOrdenados.length / PAGE_SIZE);
  if (page > totalPages && totalPages > 0) {
    setPage(Math.max(1, totalPages));
  }

  if (isLoading) {
    return <div className="text-center py-12 text-slate-400 text-lg">Cargando cola...</div>;
  }

  if (error) {
    return (
      <Alert type="error">
        Error al cargar la cola: {String(error)}
      </Alert>
    );
  }

  if (tickets.length === 0) {
    return (
      <Alert type="info">
        No hay tickets en la cola. ¡Bienvenido!
      </Alert>
    );
  }

  return (
    <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-2xl border border-slate-700/50 p-6">
      <div className="mb-6 flex flex-wrap gap-4 justify-between items-center border-b border-slate-700 pb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold text-white">📋 Cola de Tickets</h2>
          {isLive ? (
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Tiempo real
            </span>
          ) : (
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              Sondeo activo
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Selector de orden (Más recientes por defecto) */}
          <div className="inline-flex p-1 bg-slate-900/80 rounded-xl border border-slate-700 text-xs">
            <button
              type="button"
              onClick={() => setCriterioOrden("recientes")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                criterioOrden === "recientes"
                  ? "bg-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              🕒 Más recientes
            </button>
            <button
              type="button"
              onClick={() => setCriterioOrden("prioridad")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                criterioOrden === "prioridad"
                  ? "bg-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              ⚡ Prioridad
            </button>
          </div>

          {totalNewCount > 0 && (
            <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 rounded-full text-xs font-bold border border-cyan-400/30 animate-pulse">
              ✨ {totalNewCount} nuevo{totalNewCount > 1 ? "s" : ""}
            </span>
          )}
          <span className="px-3 py-1 bg-blue-500/30 text-blue-200 rounded-full text-sm font-bold border border-blue-400/30">
            {total} total
          </span>
        </div>
      </div>

      <div className="text-xs text-slate-400 mb-6 flex justify-between">
        <span>
          Orden: <strong className="text-slate-300">{criterioOrden === "recientes" ? "Por hora (más recientes primero)" : "Por prioridad descendente"}</strong> · Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, ticketsOrdenados.length)} de {ticketsOrdenados.length}
        </span>
        <span>Página {page} de {totalPages}</span>
      </div>


      <div className="space-y-1">
        {paginated.map((ticket) => (
          <TicketCard
            key={ticket.id}
            ticket={ticket}
            onDelete={borrar}
            newInfo={getTicketNewInfo(ticket.id)}
          />
        ))}
      </div>


      {totalPages > 1 && (
        <Pagination currentPage={page} totalPages={totalPages} onChange={setPage} />
      )}

    </div>
  );
}
