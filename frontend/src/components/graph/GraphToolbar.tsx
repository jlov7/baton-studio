"use client";

import { useState } from "react";
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
    <div className="flex items-center gap-3 px-4 py-2 border-b border-white/[0.06] bg-zinc-900/80">
      {/* Search */}
      <div className="relative">
        <svg
          className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            onSearch(e.target.value);
          }}
          placeholder="Search nodes..."
          className="pl-7 pr-3 py-1 text-xs bg-zinc-800 border border-white/[0.06] rounded-lg text-zinc-300 placeholder:text-zinc-600 w-48 focus:outline-none focus:border-amber-500/40"
        />
      </div>

      {/* Lenses */}
      <div className="flex items-center gap-1">
        {LENSES.map((lens) => (
          <button
            key={lens.id}
            onClick={() => onLensChange(lens.id)}
            className={cn(
              "px-2 py-1 text-[11px] rounded-md transition-colors",
              activeLens === lens.id
                ? "bg-amber-500/15 text-amber-400"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]",
            )}
          >
            {lens.label}
          </button>
        ))}
      </div>

      <div className="flex-1" />

      {/* Stats */}
      <span className="text-[11px] text-zinc-500">
        {nodeCount} nodes &middot; {edgeCount} edges
      </span>
    </div>
  );
}
