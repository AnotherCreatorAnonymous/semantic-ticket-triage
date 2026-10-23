import type { NivelPrioridad } from "@/types/api";

export const PRIORITY_STYLES: Record<NivelPrioridad, {
  emoji: string;
  color: string;
  borderColor: string;
  bgColor: string;
  badgeColor: string;
  hex: string;
}> = {
  "CRÍTICO": {
    emoji: "🔴",
    color: "text-red-700",
    borderColor: "border-red-600",
    bgColor: "bg-red-50",
    badgeColor: "bg-red-300 text-red-950 font-bold",
    hex: "#dc2626",
  },
  "ALTO": {
    emoji: "🟠",
    color: "text-orange-700",
    borderColor: "border-orange-600",
    bgColor: "bg-orange-50",
    badgeColor: "bg-orange-300 text-orange-950 font-bold",
    hex: "#ea580c",
  },
  "MEDIO": {
    emoji: "🟡",
    color: "text-amber-700",
    borderColor: "border-amber-600",
    bgColor: "bg-amber-50",
    badgeColor: "bg-amber-300 text-amber-950 font-bold",
    hex: "#ca8a04",
  },
  "MEDIA_BAJA": {
    emoji: "🟢",
    color: "text-lime-700",
    borderColor: "border-lime-600",
    bgColor: "bg-lime-50",
    badgeColor: "bg-lime-300 text-lime-950 font-bold",
    hex: "#65a30d",
  },
  "BAJO": {
    emoji: "🟩",
    color: "text-emerald-700",
    borderColor: "border-emerald-600",
    bgColor: "bg-emerald-50",
    badgeColor: "bg-emerald-300 text-emerald-950 font-bold",
    hex: "#059669",
  },
};

export const PRIORITY_LEVELS = {
  1: "BAJO",
  2: "MEDIA_BAJA",
  3: "MEDIO",
  4: "ALTO",
  5: "CRÍTICO",
} as const;
