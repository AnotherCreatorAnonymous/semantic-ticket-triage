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
    color: "text-red-600",
    borderColor: "border-red-500",
    bgColor: "bg-red-50",
    badgeColor: "bg-red-100 text-red-800",
    hex: "#d62728",
  },
  "ALTO": {
    emoji: "🟠",
    color: "text-orange-600",
    borderColor: "border-orange-500",
    bgColor: "bg-orange-50",
    badgeColor: "bg-orange-100 text-orange-800",
    hex: "#ff7f0e",
  },
  "MEDIO": {
    emoji: "🟡",
    color: "text-yellow-600",
    borderColor: "border-yellow-500",
    bgColor: "bg-yellow-50",
    badgeColor: "bg-yellow-100 text-yellow-800",
    hex: "#e3b505",
  },
  "BAJO": {
    emoji: "🟢",
    color: "text-green-600",
    borderColor: "border-green-500",
    bgColor: "bg-green-50",
    badgeColor: "bg-green-100 text-green-800",
    hex: "#2ca02c",
  },
};

export const PRIORITY_LEVELS = {
  1: "BAJO",
  2: "MEDIO",
  3: "ALTO",
  4: "CRÍTICO",
  5: "CRÍTICO",
} as const;
