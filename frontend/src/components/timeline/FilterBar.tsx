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
    <div className="flex items-center gap-2 px-4 py-2 border-b border-white/[0.06] bg-zinc-900/80">
      {EVENT_TYPES.map((type) => (
        <button
          key={type.id}
          onClick={() => onFilterChange(type.id)}
          className={cn(
            "px-2 py-1 text-[11px] rounded-md transition-colors",
            activeFilter === type.id
              ? "bg-amber-500/15 text-amber-400"
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
