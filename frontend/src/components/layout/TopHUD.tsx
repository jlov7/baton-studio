"use client";

import type { ReactNode } from "react";
import { Lightning, Pulse, RadioButton, ShieldCheck } from "@phosphor-icons/react";
import { useMissionContext } from "@/lib/state/MissionContext";
import { cn } from "@/lib/utils/cn";
import { agentName } from "@/lib/utils/formatters";

export function TopHUD() {
  const { mission, baton, agents, scMetric, wsStatus } = useMissionContext();
  const energy = agents.reduce((sum, agent) => sum + agent.energy_balance, 0);
  const sc = scMetric?.sc_current ?? 1;

  return (
    <header className="z-10 flex h-14 shrink-0 items-center gap-3 border-b border-white/[0.08] bg-[#08090b]/88 px-3 backdrop-blur-xl md:px-5">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-semibold text-zinc-100 md:max-w-[420px]">
            {mission?.title ?? "No Mission"}
          </span>
          {mission && (
            <span
              className={cn(
                "hidden rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase md:inline-flex",
                mission.status === "running" && "border-emerald-400/25 bg-emerald-400/10 text-emerald-300",
                mission.status === "idle" && "border-zinc-500/25 bg-zinc-500/10 text-zinc-400",
                mission.status === "paused" && "border-amber-400/25 bg-amber-400/10 text-amber-300",
                mission.status === "exported" && "border-cyan-400/25 bg-cyan-400/10 text-cyan-300",
              )}
            >
              {mission.status}
            </span>
          )}
        </div>
        <div className="mt-0.5 hidden items-center gap-2 text-[11px] text-zinc-500 sm:flex">
          <span className="font-mono">{mission?.mission_id ?? "local-first substrate"}</span>
          {mission && <span>{agents.length} agents</span>}
        </div>
      </div>

      <HudPill
        icon={<RadioButton size={14} weight="fill" />}
        label={baton?.holder ? agentName(baton.holder) : "free"}
        tone={baton?.holder ? "amber" : "zinc"}
        suffix={baton?.queue?.length ? `+${baton.queue.length}` : undefined}
      />
      <HudPill
        icon={<Lightning size={14} weight="fill" />}
        label={mission ? `${energy}/${mission.energy_budget}` : String(energy)}
        tone="cyan"
      />
      <HudPill
        icon={<ShieldCheck size={14} weight="fill" />}
        label={`SC ${sc.toFixed(2)}`}
        tone={sc >= 0.7 ? "emerald" : sc >= 0.4 ? "amber" : "red"}
        className="hidden sm:flex"
      />
      <div
        className={cn(
          "flex h-8 w-8 items-center justify-center rounded-md border",
          wsStatus === "connected" && "border-emerald-400/25 bg-emerald-400/10 text-emerald-300",
          wsStatus === "connecting" && "border-amber-400/25 bg-amber-400/10 text-amber-300",
          wsStatus === "disconnected" && "border-zinc-700 bg-zinc-900 text-zinc-500",
        )}
        title={`WebSocket: ${wsStatus}`}
      >
        <Pulse size={15} weight="bold" />
      </div>
    </header>
  );
}

function HudPill({
  icon,
  label,
  tone,
  suffix,
  className,
}: {
  icon: ReactNode;
  label: string;
  tone: "amber" | "cyan" | "emerald" | "red" | "zinc";
  suffix?: string;
  className?: string;
}) {
  const toneClass = {
    amber: "border-amber-400/25 bg-amber-400/10 text-amber-300",
    cyan: "border-cyan-400/25 bg-cyan-400/10 text-cyan-300",
    emerald: "border-emerald-400/25 bg-emerald-400/10 text-emerald-300",
    red: "border-red-400/25 bg-red-400/10 text-red-300",
    zinc: "border-zinc-700 bg-zinc-900 text-zinc-400",
  }[tone];

  return (
    <div
      className={cn(
        "flex h-8 items-center gap-1.5 rounded-md border px-2 text-[11px] font-medium",
        toneClass,
        className,
      )}
    >
      {icon}
      <span className="max-w-[90px] truncate font-mono">{label}</span>
      {suffix && <span className="text-zinc-500">{suffix}</span>}
    </div>
  );
}
