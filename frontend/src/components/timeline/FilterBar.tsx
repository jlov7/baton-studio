"use client";

import { cn } from "@/lib/utils/cn";

const EVENT_TYPES = [
  { id: "all", label: "All" },
  { id: "baton", label: "Baton" },
  { id: "patch", label: "Patches" },
  { id: "invariant", label: "Violations" },
  { id: "causal", label: "Causal" },
  { id: "energy", label: "Energy" },
  { id: "agent", label: "Agents" },
] as const;

interface FilterBarProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
  eventCount: number;
}

export function FilterBar({ activeFilter, onFilterChange, eventCount }: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.08] bg-[#0b0d10]/88 px-4 py-2 backdrop-blur">
      {EVENT_TYPES.map((type) => (
        <button
          key={type.id}
          onClick={() => onFilterChange(type.id)}
          className={cn(
            "focus-ring rounded-md px-2 py-1 text-[11px] transition-colors",
            activeFilter === type.id
              ? "bg-cyan-400/15 text-cyan-300"
              : "text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]",
          )}
        >
          {type.label}
        </button>
      ))}
      <div className="flex-1" />
      <span className="text-[11px] text-zinc-500">{eventCount} events</span>
    </div>
  );
}
