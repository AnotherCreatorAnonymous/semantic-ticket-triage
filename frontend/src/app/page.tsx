"use client";

import { HealthIndicator } from "@/components/HealthIndicator";
import { TicketForm } from "@/components/TicketForm";
import { TicketQueue } from "@/components/TicketQueue";
import { useRoles } from "@/hooks/useRoles";
import { QueueProvider, useQueue } from "@/context/QueueContext";
import type { TicketResponse } from "@/types/api";

function DashboardContent() {
  const { roles } = useRoles();
  const { agregarTicketLocal, isLive, totalNewCount } = useQueue();

  const handleTicketSuccess = (ticket?: TicketResponse) => {
    if (ticket) {
      agregarTicketLocal(ticket);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header Premium */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/5 border-b border-white/10 shadow-2xl">
        <div className="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              🛡️
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold text-white">SOC Triage</h1>
                {isLive ? (
                  <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    En vivo (SSE)
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    Sondeo activo
                  </span>
                )}
                {totalNewCount > 0 && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-400/30 animate-pulse">
                    ✨ {totalNewCount} nuevo{totalNewCount > 1 ? "s" : ""}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-400">
                Semantic Security Incident Management Platform
              </p>
            </div>
          </div>
          <HealthIndicator />
        </div>
      </header>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-blue-500/10 to-transparent border-b border-blue-400/20 py-12">
        <div className="max-w-7xl mx-auto px-8">
          <h2 className="text-5xl font-bold text-white mb-3">Centro de Reportes</h2>
          <p className="text-lg text-slate-300">
            Triage automático y análisis explicable de incidentes de seguridad
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar - Formulario */}
          <aside className="lg:col-span-1">
            <div className="sticky top-32">
              <TicketForm roles={roles} onSuccess={handleTicketSuccess} />
            </div>
          </aside>

          {/* Main - Cola de Tickets */}
          <section className="lg:col-span-2">
            <TicketQueue />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-20 py-12 px-8 bg-gradient-to-t from-blue-500/5 to-transparent">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-sm text-slate-400">
            SOC Triage • Triage semántico inteligente de incidentes de seguridad
          </p>
          <p className="text-xs text-slate-500 mt-2">
            S1 Heurística • S2 ML Baseline • S3 Explicabilidad
          </p>
        </div>
      </footer>
    </div>
  );
}

export default function Home() {
  return (
    <QueueProvider>
      <DashboardContent />
    </QueueProvider>
  );
}
