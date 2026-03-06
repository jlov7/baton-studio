import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Baton Studio",
  description: "Shared Cognitive Substrate Control Room for multi-agent teams",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
