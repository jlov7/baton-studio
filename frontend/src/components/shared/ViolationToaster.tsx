"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useMissionContext } from "@/lib/state/MissionContext";
import { useToast } from "@/components/shared/Toast";

export function ViolationToaster() {
  const { events } = useMissionContext();
  const { toast } = useToast();
  const router = useRouter();
  const seenCount = useRef(0);

  useEffect(() => {
    const newEvents = events.slice(seenCount.current);
    seenCount.current = events.length;

    for (const event of newEvents) {
      if (event.type === "invariant.violation") {
        const payload = event.payload as Record<string, unknown>;
        const message =
          typeof payload?.message === "string"
            ? payload.message
            : "Invariant violation detected";
        toast(message, {
          variant: "warning",
          action: {
            label: "View in Graph",
            onClick: () => router.push("/graph"),
          },
        });
      }
    }
  }, [events, toast, router]);

  return null;
}
