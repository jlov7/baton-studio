"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils/cn";
import { agentName } from "@/lib/utils/formatters";

interface BatonPillProps {
  holder: string | null;
  queueLength: number;
}

export function BatonPill({ holder, queueLength }: BatonPillProps) {
  const [flash, setFlash] = useState(false);
  const prevHolder = useRef(holder);

  useEffect(() => {
    if (prevHolder.current !== holder && holder) {
      setFlash(true);
      const t = setTimeout(() => setFlash(false), 1000);
      prevHolder.current = holder;
      return () => clearTimeout(t);
    }
    prevHolder.current = holder;
  }, [holder]);

  return (
    <div className="relative">
      {flash && (
        <div className="absolute inset-0 rounded-full bg-amber-400/30 animate-pulse-ring pointer-events-none" />
      )}
      <div
        className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-all duration-300",
          holder
            ? "bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-[0_0_12px_rgba(245,158,11,0.15)]"
            : "bg-zinc-800/60 text-zinc-500 border border-white/[0.06]",
        )}
      >
        <div
          className={cn(
            "w-2 h-2 rounded-full transition-colors",
            holder ? "bg-amber-400 animate-glow" : "bg-zinc-600",
          )}
        />
        <span className="font-mono text-xs">
          {holder ? agentName(holder) : "No holder"}
        </span>
        {queueLength > 0 && (
          <span className="text-[10px] text-zinc-500 ml-1">+{queueLength} queued</span>
        )}
      </div>
    </div>
  );
}
