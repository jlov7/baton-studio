"use client";

import { useEffect, useRef } from "react";
import type { EventEnvelope } from "@/lib/api/types";
import { EventCard } from "./EventCard";

interface EventStreamProps {
  events: EventEnvelope[];
  onEventClick?: (event: EventEnvelope) => void;
  autoScroll?: boolean;
}

export function EventStream({
  events,
  onEventClick,
  autoScroll = true,
}: EventStreamProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && endRef.current) {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [events.length, autoScroll]);

  return (
    <div
      ref={containerRef}
      className="flex flex-col gap-0.5 overflow-y-auto flex-1 py-2"
    >
      {events.map((event) => (
        <EventCard
          key={event.event_id}
          event={event}
          onClick={() => onEventClick?.(event)}
        />
      ))}
      <div ref={endRef} />
    </div>
  );
}
