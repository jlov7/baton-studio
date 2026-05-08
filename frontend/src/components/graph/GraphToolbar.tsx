"use client";

import { useState } from "react";
import { MagnifyingGlass } from "@phosphor-icons/react";
import { cn } from "@/lib/utils/cn";

const LENSES = [
  { id: "all", label: "All" },
  { id: "disputed", label: "Disputed" },
  { id: "stale", label: "Stale Chain" },
  { id: "attribution", label: "Agent Attribution" },
] as const;

interface GraphToolbarProps {
  activeLens: string;
  onLensChange: (lens: string) => void;
  onSearch: (query: string) => void;
  nodeCount: number;
  edgeCount: number;
}

export function GraphToolbar({
  activeLens,
  onLensChange,
  onSearch,
  nodeCount,
  edgeCount,
}: GraphToolbarProps) {
  const [search, setSearch] = useState("");

  return (
    <div className="flex flex-wrap items-center gap-3 border-b border-white/[0.08] bg-[#0b0d10]/88 px-4 py-2 backdrop-blur">
      <div className="relative">
        <MagnifyingGlass
          size={14}
          weight="bold"
          className="absolute left-2 top-1/2 -translate-y-1/2 text-zinc-500"
        />
        <input
          type="text"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            onSearch(e.target.value);
          }}
          placeholder="Search nodes..."
          className="focus-ring w-52 rounded-md border border-white/[0.08] bg-zinc-950 py-1.5 pl-7 pr-3 text-xs text-zinc-300 placeholder:text-zinc-600 focus:border-cyan-400/40"
        />
      </div>

      <div className="flex min-w-0 items-center gap-1 overflow-x-auto">
        {LENSES.map((lens) => (
          <button
            key={lens.id}
            onClick={() => onLensChange(lens.id)}
            className={cn(
              "focus-ring whitespace-nowrap rounded-md px-2 py-1 text-[11px] transition-colors",
              activeLens === lens.id
                ? "bg-cyan-400/15 text-cyan-300"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]",
            )}
          >
            {lens.label}
          </button>
        ))}
      </div>

      <div className="flex-1" />

      <span className="text-[11px] text-zinc-500">
        {nodeCount} nodes &middot; {edgeCount} edges
      </span>
    </div>
  );
}
