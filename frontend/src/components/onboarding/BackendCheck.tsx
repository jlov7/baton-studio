"use client";

import { useEffect, useState } from "react";
import { WarningCircle } from "@phosphor-icons/react";
import { checkHealth } from "@/lib/api/health";

export function BackendCheck({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<"checking" | "ok" | "offline">("checking");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    checkHealth()
      .then(() => { if (!cancelled) setStatus("ok"); })
      .catch(() => { if (!cancelled) setStatus("offline"); });
    return () => { cancelled = true; };
  }, [attempt]);

  if (status === "checking") {
    return (
      <div className="flex h-full items-center justify-center text-sm text-zinc-500">
        Connecting to backend...
      </div>
    );
  }

  if (status === "offline") {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 p-8 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-md border border-red-400/20 bg-red-400/10 text-red-300">
          <WarningCircle size={25} weight="duotone" />
        </div>
        <h3 className="text-sm font-medium text-zinc-300">Backend Offline</h3>
        <p className="text-xs text-zinc-500 max-w-xs">
          Start the Baton Substrate server to get started.
        </p>
        <code className="px-3 py-1.5 bg-zinc-800 rounded-lg text-xs font-mono text-amber-400 border border-white/[0.06]">
          make dev
        </code>
        <button
          onClick={() => {
            setStatus("checking");
            setAttempt((value) => value + 1);
          }}
          className="focus-ring mt-2 rounded px-3 py-1 text-xs text-zinc-500 transition-colors hover:bg-white/[0.05] hover:text-zinc-300"
        >
          Retry
        </button>
      </div>
    );
  }

  return <>{children}</>;
}
