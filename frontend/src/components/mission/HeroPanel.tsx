"use client";

import { ArrowSquareOut, Play, Pulse } from "@phosphor-icons/react";
import type { MissionResponse } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import { BatonPill } from "@/components/hud/BatonPill";
import { EnergyBar } from "@/components/hud/EnergyBar";

interface HeroPanelProps {
  mission: MissionResponse;
  batonHolder: string | null;
  batonQueue: string[];
  totalEnergy: number;
  onStartSimulation?: () => void;
  onExport?: () => void;
  simulationRunning?: boolean;
}

export function HeroPanel({
  mission,
  batonHolder,
  batonQueue,
  totalEnergy,
  onStartSimulation,
  onExport,
  simulationRunning,
}: HeroPanelProps) {
  return (
    <section className="panel overflow-hidden">
      <div className="grid gap-5 p-4 lg:grid-cols-[1fr_320px] lg:p-5">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={cn(
                "rounded border px-2 py-0.5 text-[11px] font-semibold uppercase",
                mission.status === "running" && "border-emerald-400/25 bg-emerald-400/10 text-emerald-300",
                mission.status === "idle" && "border-zinc-500/25 bg-zinc-500/10 text-zinc-400",
                mission.status === "paused" && "border-amber-400/25 bg-amber-400/10 text-amber-300",
                mission.status === "exported" && "border-cyan-400/25 bg-cyan-400/10 text-cyan-300",
              )}
            >
              {mission.status}
            </span>
            <span className="font-mono text-[11px] text-zinc-500">{mission.mission_id}</span>
          </div>

          <h1 className="mt-3 text-xl font-semibold text-zinc-50 md:text-2xl">
            {mission.title}
          </h1>
          {mission.goal && (
            <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">{mission.goal}</p>
          )}

          <div className="mt-5 flex flex-wrap gap-2">
            {onStartSimulation && (
              <button
                onClick={onStartSimulation}
                disabled={simulationRunning}
                className={cn(
                  "focus-ring inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  simulationRunning
                    ? "bg-zinc-800 text-zinc-500"
                    : "bg-emerald-400 text-zinc-950 hover:bg-emerald-300",
                )}
              >
                <Play size={15} weight="fill" />
                {simulationRunning ? "Running" : "Run"}
              </button>
            )}
            {onExport && (
              <button
                onClick={onExport}
                className="focus-ring inline-flex items-center gap-2 rounded-md border border-white/[0.08] bg-white/[0.04] px-3 py-2 text-sm font-medium text-zinc-200 transition-colors hover:bg-white/[0.08]"
              >
                <ArrowSquareOut size={15} weight="bold" />
                Export
              </button>
            )}
          </div>
        </div>

        <div className="grid content-start gap-4 border-t border-white/[0.08] pt-4 lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
          <div className="flex items-center gap-2 text-xs font-medium uppercase text-zinc-500">
            <Pulse size={14} weight="bold" />
            Live arbitration
          </div>
          <BatonPill holder={batonHolder} queueLength={batonQueue.length} />
          <EnergyBar
            current={totalEnergy}
            max={mission.energy_budget}
            label="Mission Energy"
          />
        </div>
      </div>
    </section>
  );
}
