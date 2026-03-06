"use client";

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
    <div className="flex flex-col gap-4 p-5 rounded-2xl border border-white/[0.06] bg-gradient-to-b from-zinc-900/80 to-zinc-900/40">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
            {mission.title}
          </h1>
          {mission.goal && (
            <p className="text-sm text-zinc-400 max-w-xl">{mission.goal}</p>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {onStartSimulation && (
            <button
              onClick={onStartSimulation}
              disabled={simulationRunning}
              className={cn(
                "px-3 py-1.5 text-sm rounded-lg font-medium transition-colors",
                simulationRunning
                  ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                  : "bg-emerald-600 hover:bg-emerald-500 text-white",
              )}
            >
              {simulationRunning ? "Running..." : "Start Simulation"}
            </button>
          )}
          {onExport && (
            <button
              onClick={onExport}
              className="px-3 py-1.5 text-sm rounded-lg font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
            >
              Export
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-6">
        <BatonPill holder={batonHolder} queueLength={batonQueue.length} />
        <div className="w-48">
          <EnergyBar
            current={totalEnergy}
            max={mission.energy_budget}
            label="Mission Energy"
          />
        </div>
      </div>
    </div>
  );
}
