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

  const config = {
    loaded: {
      dot: "bg-emerald-500",
      label: "Modelo ML Activo",
      icon: "⚡",
    },
    heuristic_fallback: {
      dot: "bg-blue-500",
      label: "Modo Seguro",
      icon: "🔒",
    },
    loading: {
      dot: "bg-slate-500",
      label: "Conectando...",
      icon: "🔄",
    },
  };

  const current = config[status];

  return (
    <div className={`flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border ${status === 'loaded' ? 'border-emerald-400/30' : 'border-blue-400/30'} backdrop-blur-sm`}>
      <div className={`w-2.5 h-2.5 rounded-full ${current.dot} animate-pulse`} role="status" aria-label={current.label} />
      <span className="text-xs font-medium text-slate-300">{current.icon} {current.label}</span>
    </div>
  );
}
