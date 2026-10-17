"use client";

import { enviarTicket, ErrorValidacion } from "@/lib/api-client";
import type { RolUsuario } from "@/types/api";
import { Alert } from "./ui/Alert";
import { useEffect, useState } from "react";

interface Props {
  roles: string[];
  onSuccess?: () => void;
}

export function TicketForm({ roles, onSuccess }: Props) {
  const [titulo, setTitulo] = useState("");
  const [texto, setTexto] = useState("");
  const [rol, setRol] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);
  const [showRoleDropdown, setShowRoleDropdown] = useState(false);

  useEffect(() => {
    if (roles.length > 0 && !rol) {
      setRol(roles[0]);
    }
  }, [roles, rol]);

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
    <form onSubmit={handleSubmit} className="p-8 bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-blue-400/20 shadow-2xl backdrop-blur-sm hover:border-blue-400/40 transition-all">
      <div className="mb-8">
        <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-cyan-500 px-4 py-2 rounded-full mb-4 shadow-lg">
          <span className="text-white text-sm font-bold">📋 NUEVO REPORTE</span>
        </div>
        <h2 className="text-3xl font-bold text-white">Reportar Incidente</h2>
        <p className="text-sm text-slate-400 mt-2">Describe el problema de seguridad para análisis automático</p>
      </div>

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
          <div className="text-sm font-medium">✅ Ticket enviado exitosamente y agregado a la cola</div>
        </Alert>
      )}

      <div className="mb-6">
        <label className="block text-sm font-semibold text-white mb-3">
          Título del Incidente
        </label>
        <input
          type="text"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          placeholder="Ej: Acceso no autorizado a base de datos"
          maxLength={100}
          required
        />
        <span className="text-xs text-slate-500 mt-2 block">{titulo.length}/100 caracteres</span>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-white mb-3">
          Descripción Detallada
        </label>
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all font-mono text-sm"
          placeholder="Describe el incidente: qué pasó, cuándo, quién, qué sistemas afecta..."
          rows={7}
          maxLength={2000}
          required
        />
        <span className="text-xs text-slate-500 mt-2 block">{texto.length}/2000 caracteres</span>
      </div>

      <div className="mb-8">
        <label className="block text-sm font-semibold text-white mb-3">
          Rol / Departamento
        </label>
        
        {/* Custom Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowRoleDropdown(!showRoleDropdown)}
            className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white text-left flex justify-between items-center hover:bg-slate-700/70 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all font-medium"
          >
            <span>{rol || 'Selecciona un rol...'}</span>
            <span className={`transition-transform ${showRoleDropdown ? 'rotate-180' : ''}`}>▼</span>
          </button>

          {/* Dropdown Menu */}
          {showRoleDropdown && roles.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-slate-600 rounded-xl shadow-xl z-50 overflow-hidden backdrop-blur-sm">
              {roles.map((r, idx) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => {
                    setRol(r);
                    setShowRoleDropdown(false);
                  }}
                  className={`w-full px-4 py-3 text-left font-medium transition-all text-white
                    ${r === rol ? 'bg-blue-600/40 border-l-4 border-blue-500' : 'hover:bg-slate-700/50'}
                    ${idx !== roles.length - 1 ? 'border-b border-slate-700' : ''}
                  `}
                >
                  <span className="flex items-center gap-3">
                    <span>{r === rol ? '✓' : '◯'}</span>
                    <span>{r}</span>
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !titulo.trim() || !texto.trim() || !rol}
        className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-semibold rounded-xl hover:shadow-lg hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 text-lg"
      >
        {loading ? "⏳ Procesando..." : "🚀 Enviar Reporte"}
      </button>
    </form>
  );
}
