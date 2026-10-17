"use client";

import { obtenerHealth } from "@/lib/api-client";
import { useEffect, useState } from "react";

export function HealthIndicator() {
  const [status, setStatus] = useState<"loading" | "loaded" | "heuristic_fallback">("loading");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await obtenerHealth();
        setStatus(health.model);
      } catch {
        setStatus("heuristic_fallback");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const color =
    status === "loaded" ? "bg-green-500" :
    status === "heuristic_fallback" ? "bg-yellow-500" :
    "bg-gray-400";

  const label =
    status === "loaded" ? "Modelo ML" :
    status === "heuristic_fallback" ? "Heurística S1" :
    "Conectando...";

  return (
    <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 shadow-sm">
      <div className={`w-3 h-3 rounded-full ${color} animate-pulse`} role="status" aria-label={label} />
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </div>
  );
}
