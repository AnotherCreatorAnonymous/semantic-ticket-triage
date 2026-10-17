"use client";

import { ReactNode } from "react";

export interface AlertProps {
  type: "error" | "success" | "info" | "warning";
  children: ReactNode;
}

export function Alert({ type, children }: AlertProps) {
  const styles = {
    error: "bg-red-50 border border-red-200 text-red-700",
    success: "bg-green-50 border border-green-200 text-green-700",
    info: "bg-blue-50 border border-blue-200 text-blue-700",
    warning: "bg-yellow-50 border border-yellow-200 text-yellow-700",
  };

  return (
    <div className={`p-4 rounded-md ${styles[type]}`} role="alert">
      {children}
    </div>
  );
}
