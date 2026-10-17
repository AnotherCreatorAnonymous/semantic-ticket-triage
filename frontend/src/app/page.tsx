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
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            🛡️ SOC Triage Dashboard
          </h1>
          <HealthIndicator />
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <aside className="lg:col-span-1">
            <TicketForm roles={roles} onSuccess={agregar} />
          </aside>

          <section className="lg:col-span-2">
            <TicketQueue />
          </section>
        </div>
      </main>
    </div>
  );
}
