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
    return <div className="text-center py-8 text-gray-500">Cargando cola...</div>;
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
    <div>
      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-bold">Cola de Tickets ({total} total)</h2>
        <span className="text-sm text-gray-600">
          Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, tickets.length)} de {tickets.length}
        </span>
      </div>

      <div className="space-y-2">
        {paginated.map((ticket) => (
          <TicketCard
            key={ticket.id}
            ticket={ticket}
            onDelete={borrar}
          />
        ))}
      </div>

      <Pagination currentPage={page} totalPages={totalPages} onChange={setPage} />
    </div>
  );
}
