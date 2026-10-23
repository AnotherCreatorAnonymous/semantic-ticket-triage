"use client";

import { PRIORITY_STYLES } from "@/lib/priority";
import { limpiarFactor, parseXai } from "@/lib/xai";
import type { NivelPrioridad } from "@/types/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";


interface Props {
  explicacion: Record<string, number>;
  nivel: NivelPrioridad;
}

export function XaiChart({ explicacion, nivel }: Props) {
  const items = parseXai(explicacion);
  const style = PRIORITY_STYLES[nivel];
  if (!style) return null;

  const data = items.map((item) => ({
    factor: limpiarFactor(item.factor),
    aporte: item.aporte,
    tipo: item.tipo,
  }));

  const height = 80 + 40 * Math.max(1, data.length);

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout="vertical" margin={{ left: 200, right: 20, top: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="factor" type="category" width={190} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="aporte" fill={style.hex} radius={4}>
            {data.map((entry, idx) => (
              <Cell
                key={`cell-${idx}`}
                fill={entry.tipo === "rol" ? "#8c8c8c" : style.hex}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
