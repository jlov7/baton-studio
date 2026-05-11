"use client";

import { useCallback, useMemo, useState } from "react";
import { EmptyState } from "@/components/shared/EmptyState";
import { useMissionContext } from "@/lib/state/MissionContext";
import { useInspector } from "@/components/layout/InspectorDrawer";
import { EventStream } from "@/components/timeline/EventStream";
import { FilterBar } from "@/components/timeline/FilterBar";
import { MonoText } from "@/components/shared/MonoText";
import { Badge } from "@/components/shared/Badge";
import { formatDate, agentName } from "@/lib/utils/formatters";
import type { EventEnvelope } from "@/lib/api/types";

export default function TimelinePage() {
  const { mission, events } = useMissionContext();
  const { openInspector } = useInspector();
  const [filter, setFilter] = useState("all");
  const [replayIndex, setReplayIndex] = useState(Number.MAX_SAFE_INTEGER);

  const filteredEvents = useMemo(() => {
    if (filter === "all") return events;
    return events.filter((e) => e.type.startsWith(filter));
  }, [events, filter]);

  const replayPosition = Math.min(replayIndex, filteredEvents.length);
  const visibleEvents = filteredEvents.slice(0, replayPosition);
  const handleFilterChange = useCallback((nextFilter: string) => {
    setFilter(nextFilter);
    setReplayIndex(Number.MAX_SAFE_INTEGER);
  }, []);

  const handleEventClick = useCallback(
    (event: EventEnvelope) => {
      openInspector(
        event.type,
        <div className="flex flex-col gap-3">
          <MonoText>{event.event_id}</MonoText>
          <div className="flex items-center gap-2">
            <Badge variant="amber">{event.type}</Badge>
            <span className="text-xs text-zinc-500">{formatDate(event.ts)}</span>
          </div>
          <div>
            <h4 className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
              Actor
            </h4>
            <p className="text-sm text-zinc-300">
              {event.actor.display_name || agentName(event.actor.actor_id)}{" "}
              <span className="text-zinc-500">({event.actor.actor_type})</span>
            </p>
          </div>
          <div>
            <h4 className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
              Payload
            </h4>
            <pre className="text-xs font-mono text-zinc-400 bg-zinc-900/80 rounded-lg p-3 border border-white/[0.06] overflow-x-auto">
              {JSON.stringify(event.payload, null, 2)}
            </pre>
          </div>
        </div>,
      );
    },
    [openInspector],
  );

  if (!mission) {
    return (
      <EmptyState
        title="No Mission Loaded"
        description="Load a mission from Mission Control to view the event timeline."
      />
    );
  }

  if (events.length === 0) {
    return (
      <EmptyState
        title="No Events Yet"
        description="Load a demo mission or import a mission pack to view the event stream."
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      <FilterBar
        activeFilter={filter}
        onFilterChange={handleFilterChange}
        eventCount={visibleEvents.length}
      />
      <div className="flex items-center gap-3 border-b border-white/[0.08] bg-[#0b0d10]/70 px-4 py-2">
        <span className="text-[11px] font-semibold uppercase text-zinc-500">Replay</span>
        <input
          aria-label="Replay position"
          type="range"
          min={0}
          max={filteredEvents.length}
          value={replayPosition}
          onChange={(event) => setReplayIndex(Number(event.target.value))}
          className="h-1 flex-1 accent-cyan-300"
        />
        <span
          className="w-20 text-right font-mono text-[11px] text-zinc-500"
          data-testid="timeline-replay-counter"
        >
          {replayPosition}/{filteredEvents.length}
        </span>
      </div>
      <EventStream events={visibleEvents} onEventClick={handleEventClick} />
    </div>
  );
}
