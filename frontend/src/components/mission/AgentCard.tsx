"use client";

import type { AgentDetail } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import { agentName } from "@/lib/utils/formatters";
import { EnergyBar } from "@/components/hud/EnergyBar";

interface AgentCardProps {
  agent: AgentDetail;
  isHolder: boolean;
  missionBudget: number;
}

const ROLE_COLORS: Record<string, string> = {
  researcher: "text-blue-400",
  planner: "text-emerald-400",
  critic: "text-red-400",
  implementer: "text-purple-400",
};

export function AgentCard({ agent, isHolder, missionBudget }: AgentCardProps) {
  const perAgentMax = Math.floor(missionBudget / 4) || missionBudget;

  return (
    <div
      className={cn(
        "flex flex-col gap-2 p-3 rounded-xl border transition-all duration-300",
        isHolder
          ? "border-amber-500/40 bg-amber-500/[0.05] shadow-[0_0_16px_rgba(245,158,11,0.08)]"
          : "border-white/[0.06] bg-zinc-900/60",
      )}
    >
      <div className="flex items-center gap-2">
        <div
          className={cn(
            "w-2 h-2 rounded-full",
            agent.status === "active" ? "bg-emerald-400" : "bg-zinc-600",
          )}
        />
        <span className="text-sm font-medium text-zinc-200">
          {agent.display_name || agentName(agent.actor_id)}
        </span>
        {isHolder && (
          <span className="ml-auto text-[10px] font-mono text-amber-400 animate-glow">
            BATON
          </span>
        )}
      </div>

      <span
        className={cn(
          "text-[11px] font-medium uppercase tracking-wider",
          ROLE_COLORS[agent.role] ?? "text-zinc-500",
        )}
      >
        {agent.role}
      </span>

      <EnergyBar
        current={agent.energy_balance}
        max={perAgentMax}
        size="sm"
      />
    </div>
  );
}
