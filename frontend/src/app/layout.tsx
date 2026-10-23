import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SOC Triage Dashboard",
  description: "Semantic triage of IT/Security tickets with Explainable AI",
  icons: "🛡️",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="bg-gray-100">
        {children}
      </body>
    </html>
  );
}
