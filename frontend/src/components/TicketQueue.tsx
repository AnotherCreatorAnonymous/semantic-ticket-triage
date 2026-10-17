"use client";

import { useQueue } from "@/hooks/useQueue";
import { TicketCard } from "./TicketCard";
import { Pagination } from "./Pagination";
import { Alert } from "./ui/Alert";
import { useState, useMemo } from "react";

const PAGE_SIZE = 15;

export function TicketQueue() {
  const { tickets, total, error, isLoading, borrar } = useQueue();
  const [page, setPage] = useState(1);

  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return tickets.slice(start, start + PAGE_SIZE);
  }, [tickets, page]);

  const totalPages = Math.ceil(tickets.length / PAGE_SIZE);
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
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-4">
        <h2 className="text-2xl font-bold text-white">📋 Cola de Tickets</h2>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-blue-500/30 text-blue-200 rounded-full text-sm font-bold border border-blue-400/30">
            {total} total
          </span>
        </div>
      </div>

      <div className="text-xs text-slate-400 mb-6 flex justify-between">
        <span>Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, tickets.length)} de {tickets.length} tickets</span>
        <span>Página {page} de {totalPages}</span>
      </div>

      <div className="space-y-1">
        {paginated.map((ticket) => (
          <TicketCard key={ticket.id} ticket={ticket} onDelete={borrar} />
        ))}
      </div>

      {totalPages > 1 && (
        <Pagination page={page} totalPages={totalPages} onChange={setPage} />
      )}
    </div>
  );
}
