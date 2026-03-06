"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api/health";

export function BackendCheck({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<"checking" | "ok" | "offline">("checking");

  useEffect(() => {
    let cancelled = false;
    checkHealth()
      .then(() => { if (!cancelled) setStatus("ok"); })
      .catch(() => { if (!cancelled) setStatus("offline"); });
    return () => { cancelled = true; };
  }, []);

  if (status === "checking") {
    return (
      <div className="flex items-center justify-center h-full text-sm text-zinc-500">
        Connecting to backend...
      </div>
    );
  }

  if (status === "offline") {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-center p-8">
        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
          <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <h3 className="text-sm font-medium text-zinc-300">Backend Offline</h3>
        <p className="text-xs text-zinc-500 max-w-xs">
          Start the Baton Substrate server to get started.
        </p>
        <code className="px-3 py-1.5 bg-zinc-800 rounded-lg text-xs font-mono text-amber-400 border border-white/[0.06]">
          make dev
        </code>
        <button
          onClick={() => setStatus("checking")}
          className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors mt-2"
        >
          Retry
        </button>
      </div>
    );
  }

  return <>{children}</>;
}
