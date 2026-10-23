"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import useSWR from "swr";
import { eliminarTicket, obtenerCola } from "@/lib/api-client";
import type { TicketResponse } from "@/types/api";

export type TicketSource = "local" | "remote";

export interface NewTicketInfo {
  id: string;
  source: TicketSource;
  receivedAt: number;
  interactionStartedAt?: number;
  expiresAt?: number;
  secondsRemaining: number;
}

interface QueueContextType {
  tickets: TicketResponse[];
  total: number;
  isLoading: boolean;
  error: unknown;
  isLive: boolean;
  borrar: (id: string) => Promise<void>;
  agregarTicketLocal: (ticket: TicketResponse) => void;
  getTicketNewInfo: (id: string) => NewTicketInfo | null;
  isNewTicket: (id: string) => boolean;
  totalNewCount: number;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

const EXPIRATION_DURATION_MS = 60_000; // 60 segundos

export function QueueProvider({ children }: { children: React.ReactNode }) {
  // SWR para caché y sincronización automática
  const { data, error, isLoading, mutate } = useSWR(
    "GET /api/queue",
    () => obtenerCola(),
    {
      revalidateOnFocus: true,
      revalidateIfStale: true,
      refreshInterval: 3000, // Sondeo de respaldo cada 3s
    }
  );

  const [isLive, setIsLive] = useState(false);
  const [newTickets, setNewTickets] = useState<Record<string, NewTicketInfo>>({});

  // Referencias para controlar tickets conocidos y actividad del usuario
  const knownTicketIdsRef = useRef<Set<string>>(new Set());
  const initialLoadDoneRef = useRef(false);
  const lastUserInteractionTimeRef = useRef<number>(Date.now());
  const localTicketIdsRef = useRef<Set<string>>(new Set());

  // Registrar interacción de usuario (movimiento, tecla, scroll, clic o foco)
  useEffect(() => {
    const handleUserInteraction = () => {
      const now = Date.now();
      lastUserInteractionTimeRef.current = now;

      // Si hay tickets remotos esperando que el usuario interactúe, iniciar su temporizador de 60s
      setNewTickets((prev) => {
        let changed = false;
        const updated = { ...prev };

        for (const id of Object.keys(updated)) {
          const item = updated[id];
          if (item.source === "remote" && !item.interactionStartedAt) {
            changed = true;
            updated[id] = {
              ...item,
              interactionStartedAt: now,
              expiresAt: now + EXPIRATION_DURATION_MS,
              secondsRemaining: 60,
            };
          }
        }

        return changed ? updated : prev;
      });
    };

    const events = ["mousemove", "mousedown", "keydown", "scroll", "touchstart", "focus"];
    events.forEach((evt) =>
      window.addEventListener(evt, handleUserInteraction, { passive: true })
    );

    return () => {
      events.forEach((evt) =>
        window.removeEventListener(evt, handleUserInteraction)
      );
    };
  }, []);

  // Conexión Server-Sent Events (SSE) para actualización en tiempo real desde el backend
  useEffect(() => {
    let eventSource: EventSource | null = null;
    let retryTimeout: NodeJS.Timeout | null = null;

    const connectSSE = () => {
      try {
        eventSource = new EventSource("/api/queue/stream");

        eventSource.onopen = () => {
          setIsLive(true);
        };

        eventSource.addEventListener("queue_update", () => {
          // Revalidar inmediatamente la cola ante cambios en el backend
          mutate();
        });

        eventSource.onerror = () => {
          setIsLive(false);
          if (eventSource) {
            eventSource.close();
            eventSource = null;
          }
          // Reconectar en 4 segundos
          retryTimeout = setTimeout(connectSSE, 4000);
        };
      } catch {
        setIsLive(false);
      }
    };

    connectSSE();

    return () => {
      if (eventSource) eventSource.close();
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, [mutate]);

  // Detección de tickets nuevos cuando se actualiza la cola
  const currentTickets = data?.tickets || [];
  useEffect(() => {
    if (!data || !data.tickets) return;

    const now = Date.now();

    // En la primera carga
    if (!initialLoadDoneRef.current) {
      initialLoadDoneRef.current = true;
      const initialMap: Record<string, NewTicketInfo> = {};

      for (const t of data.tickets) {
        knownTicketIdsRef.current.add(t.id);
        const createdAt = new Date(t.creado_en).getTime();
        const ageMs = now - createdAt;

        // Si fue creado hace menos de 60 segundos antes de cargar la página, marcarlo como reciente
        if (ageMs >= 0 && ageMs < EXPIRATION_DURATION_MS) {
          const remaining = Math.max(1, Math.ceil((EXPIRATION_DURATION_MS - ageMs) / 1000));
          initialMap[t.id] = {
            id: t.id,
            source: "remote",
            receivedAt: createdAt,
            interactionStartedAt: now,
            expiresAt: now + (EXPIRATION_DURATION_MS - ageMs),
            secondsRemaining: remaining,
          };
        }
      }

      if (Object.keys(initialMap).length > 0) {
        setNewTickets(initialMap);
      }
      return;
    }

    // En cargas posteriores: detectar tickets que no estaban en la lista conocida
    const newItemsFound: Record<string, NewTicketInfo> = {};
    const isWindowActive =
      typeof document !== "undefined" &&
      document.visibilityState === "visible" &&
      now - lastUserInteractionTimeRef.current < 4000;

    for (const t of data.tickets) {
      if (!knownTicketIdsRef.current.has(t.id)) {
        knownTicketIdsRef.current.add(t.id);

        const isLocal = localTicketIdsRef.current.has(t.id);

        if (isLocal) {
          // Ticket generado desde la misma pantalla:
          // Desaparece exactamente 60 segundos después de su creación
          newItemsFound[t.id] = {
            id: t.id,
            source: "local",
            receivedAt: now,
            interactionStartedAt: now,
            expiresAt: now + EXPIRATION_DURATION_MS,
            secondsRemaining: 60,
          };
        } else {
          // Ticket generado desde backend u otra pantalla:
          if (isWindowActive) {
            // Usuario está interactuando activamente en la pantalla
            newItemsFound[t.id] = {
              id: t.id,
              source: "remote",
              receivedAt: now,
              interactionStartedAt: now,
              expiresAt: now + EXPIRATION_DURATION_MS,
              secondsRemaining: 60,
            };
          } else {
            // Pantalla en segundo plano o usuario inactivo:
            // Permanece como NUEVO hasta que el usuario interactúe con la pantalla
            newItemsFound[t.id] = {
              id: t.id,
              source: "remote",
              receivedAt: now,
              secondsRemaining: 60,
            };
          }
        }
      }
    }

    if (Object.keys(newItemsFound).length > 0) {
      setNewTickets((prev) => ({ ...prev, ...newItemsFound }));
    }
  }, [data]);

  // Intervalo periódico para decrementar el tiempo y expirar el efecto "NUEVO"
  useEffect(() => {
    const timer = setInterval(() => {
      const now = Date.now();

      setNewTickets((prev) => {
        let changed = false;
        const next: Record<string, NewTicketInfo> = {};

        for (const id of Object.keys(prev)) {
          const item = prev[id];

          // Si aún no ha iniciado interacción (remoto en espera de usuario), no expira
          if (item.source === "remote" && !item.expiresAt) {
            next[id] = item;
            continue;
          }

          if (item.expiresAt) {
            if (now >= item.expiresAt) {
              // El efecto "NUEVO" ha expirado después de 60 segundos
              changed = true;
              continue;
            } else {
              const remaining = Math.max(0, Math.ceil((item.expiresAt - now) / 1000));
              if (remaining !== item.secondsRemaining) {
                changed = true;
                next[id] = { ...item, secondsRemaining: remaining };
              } else {
                next[id] = item;
              }
            }
          } else {
            next[id] = item;
          }
        }

        return changed ? next : prev;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Actualizar título del navegador si hay tickets nuevos mientras la ventana está en segundo plano
  useEffect(() => {
    const totalNew = Object.keys(newTickets).length;
    const baseTitle = "SOC Triage";

    if (typeof document !== "undefined") {
      if (totalNew > 0 && document.visibilityState === "hidden") {
        document.title = `(${totalNew} NUEVO${totalNew > 1 ? "S" : ""}) ${baseTitle}`;
      } else {
        document.title = baseTitle;
      }
    }
  }, [newTickets]);

  // Registrar que un ticket fue generado en esta misma pantalla
  const agregarTicketLocal = useCallback(
    (ticket: TicketResponse) => {
      const now = Date.now();
      localTicketIdsRef.current.add(ticket.id);
      knownTicketIdsRef.current.add(ticket.id);

      setNewTickets((prev) => ({
        ...prev,
        [ticket.id]: {
          id: ticket.id,
          source: "local",
          receivedAt: now,
          interactionStartedAt: now,
          expiresAt: now + EXPIRATION_DURATION_MS,
          secondsRemaining: 60,
        },
      }));

      // Forzar actualización inmediata en SWR
      mutate();
    },
    [mutate]
  );

  const borrar = useCallback(
    async (id: string) => {
      await eliminarTicket(id);
      setNewTickets((prev) => {
        if (!prev[id]) return prev;
        const copy = { ...prev };
        delete copy[id];
        return copy;
      });
      mutate();
    },
    [mutate]
  );

  const getTicketNewInfo = useCallback(
    (id: string): NewTicketInfo | null => {
      return newTickets[id] || null;
    },
    [newTickets]
  );

  const isNewTicket = useCallback(
    (id: string): boolean => {
      return Boolean(newTickets[id]);
    },
    [newTickets]
  );

  const tickets = currentTickets;
  const total = data?.total ?? tickets.length;
  const totalNewCount = Object.keys(newTickets).length;

  return (
    <QueueContext.Provider
      value={{
        tickets,
        total,
        isLoading,
        error,
        isLive,
        borrar,
        agregarTicketLocal,
        getTicketNewInfo,
        isNewTicket,
        totalNewCount,
      }}
    >
      {children}
    </QueueContext.Provider>
  );
}

export function useQueue(): QueueContextType {
  const context = useContext(QueueContext);
  if (!context) {
    throw new Error("useQueue must be used within a QueueProvider");
  }
  return context;
}
