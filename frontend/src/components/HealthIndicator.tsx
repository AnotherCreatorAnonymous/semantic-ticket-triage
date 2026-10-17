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
    <div className="flex items-center gap-2 text-sm">
      <span className={`inline-block w-2 h-2 rounded-full ${color}`} />
      <span className="text-gray-600">{label}</span>
    </div>
  );
}
