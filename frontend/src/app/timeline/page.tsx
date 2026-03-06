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

  const filteredEvents = useMemo(() => {
    if (filter === "all") return events;
    return events.filter((e) => e.type.startsWith(filter));
  }, [events, filter]);

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
        description="Start the simulation to generate events."
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      <FilterBar
        activeFilter={filter}
        onFilterChange={setFilter}
        eventCount={filteredEvents.length}
      />
      <EventStream events={filteredEvents} onEventClick={handleEventClick} />
    </div>
  );
}
