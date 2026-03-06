"use client";

import { useMissionContext } from "@/lib/state/MissionContext";
import { cn } from "@/lib/utils/cn";
import { agentName } from "@/lib/utils/formatters";

export function TopHUD() {
  const { mission, baton, agents, scMetric, wsStatus } = useMissionContext();

  return (
    <header className="flex items-center h-11 px-4 bg-zinc-950/80 backdrop-blur border-b border-white/[0.06] gap-4 text-sm shrink-0">
      {/* Mission name */}
      <span className="font-semibold text-zinc-200 truncate max-w-[200px]">
        {mission?.title ?? "No Mission"}
      </span>

      {mission && (
        <span
          className={cn(
            "px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider",
            mission.status === "running" && "bg-emerald-500/20 text-emerald-400",
            mission.status === "idle" && "bg-zinc-700/40 text-zinc-400",
            mission.status === "paused" && "bg-amber-500/20 text-amber-400",
            mission.status === "exported" && "bg-blue-500/20 text-blue-400",
          )}
        >
          {mission.status}
        </span>
      )}

      <div className="flex-1" />

      {/* Baton holder pill */}
      <div className="flex items-center gap-2">
        <div
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs",
            baton?.holder
              ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
              : "bg-zinc-800 text-zinc-500 border border-white/[0.06]",
          )}
        >
          <div
            className={cn(
              "w-1.5 h-1.5 rounded-full",
              baton?.holder ? "bg-amber-400 animate-glow" : "bg-zinc-600",
            )}
          />
          <span className="font-mono">
            {baton?.holder ? agentName(baton.holder) : "free"}
          </span>
          {baton?.queue && baton.queue.length > 0 && (
            <span className="text-zinc-500">+{baton.queue.length}</span>
          )}
        </div>
      </div>

      {/* Energy */}
      <div className="flex items-center gap-1.5 text-xs text-cyan-400">
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span className="font-mono">
          {agents.reduce((s, a) => s + a.energy_balance, 0)}
          {mission && `/${mission.energy_budget}`}
        </span>
      </div>

      {/* SC metric */}
      {scMetric && (
        <div className="text-xs font-mono text-zinc-400">
          SC {scMetric.sc_current.toFixed(2)}
        </div>
      )}

      {/* Connection dots */}
      <div className="flex items-center gap-1.5">
        <div
          className={cn(
            "w-2 h-2 rounded-full",
            wsStatus === "connected" && "bg-emerald-400",
            wsStatus === "connecting" && "bg-amber-400 animate-pulse",
            wsStatus === "disconnected" && "bg-zinc-600",
          )}
          title={`WebSocket: ${wsStatus}`}
        />
      </div>
    </header>
  );
}
