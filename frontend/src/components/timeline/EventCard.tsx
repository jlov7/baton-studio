"use client";

import type { EventEnvelope } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import { formatDate, agentName, eventLabel } from "@/lib/utils/formatters";

interface EventCardProps {
  event: EventEnvelope;
  onClick?: () => void;
}

const EVENT_COLORS: Record<string, { dot: string; bg: string }> = {
  "baton.claimed": { dot: "bg-amber-400", bg: "bg-amber-500/5" },
  "baton.released": { dot: "bg-amber-400/50", bg: "" },
  "baton.queued": { dot: "bg-amber-400/30", bg: "" },
  "patch.proposed": { dot: "bg-blue-400", bg: "bg-blue-500/5" },
  "patch.committed": { dot: "bg-emerald-400", bg: "bg-emerald-500/5" },
  "patch.rejected": { dot: "bg-red-400", bg: "bg-red-500/5" },
  "invariant.violation": { dot: "bg-red-500", bg: "bg-red-500/5" },
  "causal.edge_added": { dot: "bg-purple-400", bg: "" },
  "causal.invalidated": { dot: "bg-red-400", bg: "bg-red-500/5" },
  "energy.spent": { dot: "bg-cyan-400", bg: "" },
  "agent.joined": { dot: "bg-emerald-400", bg: "" },
  "mission.created": { dot: "bg-zinc-400", bg: "" },
};

export function EventCard({ event, onClick }: EventCardProps) {
  const colors = EVENT_COLORS[event.type] ?? { dot: "bg-zinc-500", bg: "" };

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-start gap-3 w-full text-left px-4 py-2.5 rounded-lg transition-colors hover:bg-white/[0.04]",
        colors.bg,
      )}
    >
      {/* Timeline dot */}
      <div className="flex flex-col items-center pt-1.5 shrink-0">
        <div className={cn("w-2 h-2 rounded-full", colors.dot)} />
      </div>

      {/* Content */}
      <div className="flex flex-col gap-0.5 flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-zinc-200">
            {eventLabel(event.type)}
          </span>
          <span className="text-[10px] text-zinc-600 font-mono ml-auto shrink-0">
            {formatDate(event.ts)}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-zinc-500">
          <span>{agentName(event.actor.actor_id)}</span>
          {"entity_id" in event.payload && (
            <>
              <span>&middot;</span>
              <span className="font-mono truncate">
                {String(event.payload.entity_id)}
              </span>
            </>
          )}
          {"proposal_id" in event.payload && (
            <>
              <span>&middot;</span>
              <span className="font-mono truncate">
                {String(event.payload.proposal_id)}
              </span>
            </>
          )}
        </div>
      </div>
    </button>
  );
}
