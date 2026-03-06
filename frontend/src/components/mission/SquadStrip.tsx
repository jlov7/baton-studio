"use client";

import type { AgentDetail } from "@/lib/api/types";
import { AgentCard } from "./AgentCard";

interface SquadStripProps {
  agents: AgentDetail[];
  batonHolder: string | null;
  missionBudget: number;
}

export function SquadStrip({ agents, batonHolder, missionBudget }: SquadStripProps) {
  if (agents.length === 0) {
    return (
      <div className="text-sm text-zinc-500 py-4">No agents registered yet.</div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {agents.map((agent) => (
        <AgentCard
          key={agent.actor_id}
          agent={agent}
          isHolder={agent.actor_id === batonHolder}
          missionBudget={missionBudget}
        />
      ))}
    </div>
  );
}
