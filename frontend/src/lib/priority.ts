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
    badgeColor: "bg-red-200 text-red-900 font-semibold",
    hex: "#dc2626",
  },
  "ALTO": {
    emoji: "🟠",
    color: "text-orange-700",
    borderColor: "border-orange-600",
    bgColor: "bg-orange-50",
    badgeColor: "bg-orange-200 text-orange-900 font-semibold",
    hex: "#ea580c",
  },
  "MEDIO": {
    emoji: "🟡",
    color: "text-amber-700",
    borderColor: "border-amber-600",
    bgColor: "bg-amber-50",
    badgeColor: "bg-amber-200 text-amber-900 font-semibold",
    hex: "#ca8a04",
  },
  "BAJO": {
    emoji: "🟢",
    color: "text-emerald-700",
    borderColor: "border-emerald-600",
    bgColor: "bg-emerald-50",
    badgeColor: "bg-emerald-200 text-emerald-900 font-semibold",
    hex: "#059669",
  },
};

export const PRIORITY_LEVELS = {
  1: "BAJO",
  2: "BAJO",
  3: "MEDIO",
  4: "ALTO",
  5: "CRÍTICO",
} as const;
