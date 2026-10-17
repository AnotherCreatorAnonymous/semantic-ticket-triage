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
      setTimeout(() => setSuccess(false), 3000);
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
    <form onSubmit={handleSubmit} className="p-5 bg-white rounded-lg border border-gray-200 shadow-sm">
      <h2 className="text-xl font-bold mb-4">Reportar Ticket</h2>

      {error.length > 0 && (
        <Alert type="error">
          <ul className="list-disc pl-5">
            {error.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </Alert>
      )}

      {success && (
        <Alert type="success">✅ Ticket enviado correctamente</Alert>
      )}

      <div className="mb-4">
        <label className="block font-medium mb-1">Título (5-100 caracteres)</label>
        <input
          type="text"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded"
          maxLength={100}
          required
        />
        <span className="text-sm text-gray-500">{titulo.length}/100</span>
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Descripción (10-2000 caracteres)</label>
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded font-mono text-sm"
          rows={5}
          maxLength={2000}
          required
        />
        <span className="text-sm text-gray-500">{texto.length}/2000</span>
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Rango / Rol</label>
        <select
          value={rol}
          onChange={(e) => setRol(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded"
          required
        >
          {roles.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="px-6 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Enviando..." : "Enviar Ticket"}
      </button>
    </form>
  );
}
