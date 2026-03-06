"use client";

import { cn } from "@/lib/utils/cn";

interface EnergyBarProps {
  current: number;
  max: number;
  label?: string;
  size?: "sm" | "md";
}

export function EnergyBar({ current, max, label, size = "md" }: EnergyBarProps) {
  const pct = max > 0 ? Math.min(100, (current / max) * 100) : 0;
  const low = pct < 20;
  const mid = pct >= 20 && pct < 50;

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <div className="flex items-center justify-between">
          <span className="text-[11px] text-zinc-500">{label}</span>
          <span className="text-[11px] font-mono text-zinc-400">
            {current}/{max}
          </span>
        </div>
      )}
      <div
        className={cn(
          "rounded-full bg-zinc-800 overflow-hidden",
          size === "sm" ? "h-1" : "h-1.5",
        )}
      >
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
            low && "bg-red-500",
            mid && "bg-amber-500",
            !low && !mid && "bg-cyan-400",
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
