"use client";

import { HealthIndicator } from "@/components/HealthIndicator";
import { TicketForm } from "@/components/TicketForm";
import { TicketQueue } from "@/components/TicketQueue";
import { useRoles } from "@/hooks/useRoles";
import { useQueue } from "@/hooks/useQueue";

export default function Home() {
  const { roles } = useRoles();
  const { agregar } = useQueue();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header Premium */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/5 border-b border-white/10 shadow-2xl">
        <div className="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">🛡️</div>
            <div>
              <h1 className="text-3xl font-bold text-white">SOC Triage</h1>
              <p className="text-sm text-slate-400">Semantic Security Incident Management Platform</p>
            </div>
          </div>
          <HealthIndicator />
        </div>
      </header>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-blue-500/10 to-transparent border-b border-blue-400/20 py-12">
        <div className="max-w-7xl mx-auto px-8">
          <h2 className="text-5xl font-bold text-white mb-3">Centro de Reportes</h2>
          <p className="text-lg text-slate-300">Triage automático y análisis explicable de incidentes de seguridad</p>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar - Formulario */}
          <aside className="lg:col-span-1">
            <div className="sticky top-32">
              <TicketForm roles={roles} onSuccess={agregar} />
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
          <p className="text-sm text-slate-400">SOC Triage • Triage semántico inteligente de incidentes de seguridad</p>
          <p className="text-xs text-slate-500 mt-2">S1 Heurística • S2 ML Baseline • S3 Explicabilidad</p>
        </div>
      </footer>
    </div>
  );
}
