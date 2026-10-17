"use client";

import { enviarTicket, ErrorValidacion } from "@/lib/api-client";
import type { RolUsuario, TicketRequest } from "@/types/api";
import { Alert } from "./ui/Alert";
import { useState } from "react";

interface Props {
  roles: string[];
  onSuccess?: () => void;
}

export function TicketForm({ roles, onSuccess }: Props) {
  const [titulo, setTitulo] = useState("");
  const [texto, setTexto] = useState("");
  const [rol, setRol] = useState(roles[0] || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError([]);
    setSuccess(false);

    try {
      setLoading(true);
      await enviarTicket({
        titulo,
        texto,
        rol_usuario: rol as RolUsuario,
      });
      setTitulo("");
      setTexto("");
      setSuccess(true);
      onSuccess?.();
      setTimeout(() => setSuccess(false), 4000);
    } catch (err) {
      if (err instanceof ErrorValidacion) {
        setError(err.errores);
      } else {
        setError([String(err)]);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-8 bg-white rounded-xl border border-gray-200 shadow-lg hover:shadow-xl transition-shadow">
      <div className="mb-4">
        <div className="inline-block bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-1 rounded-full">
          <h2 className="text-sm font-bold text-white">📝 NUEVO TICKET</h2>
        </div>
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-7">Reportar Incidente</h3>

      {error.length > 0 && (
        <Alert type="error">
          <ul className="list-disc pl-5 space-y-1">
            {error.map((e, i) => (
              <li key={`error-${i}`} className="text-sm">{e}</li>
            ))}
          </ul>
        </Alert>
      )}

      {success && (
        <Alert type="success">
          <div className="text-sm font-medium">✅ Ticket enviado exitosamente</div>
        </Alert>
      )}

      <div className="mb-5">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Título del Incidente
        </label>
        <input
          type="text"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          placeholder="Ej: Acceso denegado a base de datos"
          maxLength={100}
          required
        />
        <span className="text-xs text-gray-500 mt-1 block">{titulo.length}/100 caracteres</span>
      </div>

      <div className="mb-5">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Descripción Detallada
        </label>
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition font-mono text-sm"
          placeholder="Describe el incidente con el máximo detalle posible..."
          rows={6}
          maxLength={2000}
          required
        />
        <span className="text-xs text-gray-500 mt-1 block">{texto.length}/2000 caracteres</span>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Rango / Rol Responsable
        </label>
        <select
          value={rol}
          onChange={(e) => setRol(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          required
        >
          {roles && roles.length > 0 ? (
            roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))
          ) : (
            <option disabled>Cargando roles...</option>
          )}
        </select>
      </div>

      <button
        type="submit"
        disabled={loading || !roles.length}
        className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-lg hover:shadow-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {loading ? "⏳ Enviando..." : "🚀 Enviar Ticket"}
      </button>
    </form>
  );
}
