"use client";

import { obtenerRoles } from "@/lib/api-client";
import useSWR from "swr";

export function useRoles() {
  const { data, error, isLoading } = useSWR(
    "GET /api/roles",
    () => obtenerRoles(),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    roles: data || [],
    error,
    isLoading,
  };
}
