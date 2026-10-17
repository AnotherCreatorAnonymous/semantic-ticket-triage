"use client";

import { eliminarTicket, obtenerCola } from "@/lib/api-client";
import type { TicketResponse } from "@/types/api";
import useSWR from "swr";

export function useQueue() {
  const { data, error, isLoading, mutate } = useSWR(
    "GET /api/queue",
    () => obtenerCola(),
    {
      revalidateOnFocus: false,
      refreshInterval: 10000,
    }
  );

  const tickets = data?.tickets || [];
  const total = data?.total || 0;

  const borrar = async (id: string) => {
    await eliminarTicket(id);
    mutate();
  };

  const agregar = () => {
    mutate();
  };

  return {
    tickets,
    total,
    error,
    isLoading,
    borrar,
    agregar,
  };
}
