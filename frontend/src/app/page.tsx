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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/10 border-b border-white/20 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🛡️</div>
            <div>
              <h1 className="text-2xl font-bold text-white">SOC Triage</h1>
              <p className="text-xs text-blue-200">Semantic Security Incident Management</p>
            </div>
          </div>
          <HealthIndicator />
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-white mb-2">Centro de Reportes</h2>
          <p className="text-lg text-blue-100">Gestiona y prioriza incidentes de seguridad con IA explicable</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar - Formulario */}
          <aside className="lg:col-span-1">
            <div className="sticky top-32">
              <TicketForm roles={roles} onSuccess={agregar} />
            </div>
          </aside>

          {/* Main - Cola de Tickets */}
          <section className="lg:col-span-2">
            <div className="rounded-xl overflow-hidden">
              <TicketQueue />
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-16 py-8 px-6">
        <div className="max-w-7xl mx-auto text-center text-sm text-blue-200">
          <p>SOC Triage • Triage semántico inteligente de incidentes de seguridad</p>
        </div>
      </footer>
    </div>
  );
}
