"use client";

import { obtenerRoles } from "@/lib/api-client";
import useSWR from "swr";

export function useRoles() {
  const { data, error, isLoading, mutate } = useSWR(
    "GET /api/roles",
    () => obtenerRoles(),
    {
      revalidateOnFocus: true,
      dedupingInterval: 0,
      revalidateIfStale: true,
    }
  );

  return {
    roles: data || [],
    error,
    isLoading,
    mutate,
  };
}
