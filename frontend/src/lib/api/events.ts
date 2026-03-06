import { get } from "./client";
import type { EventListResponse } from "./types";

export function getEvents(
  missionId: string,
  params?: { after?: string; type?: string; limit?: number },
) {
  const qs = new URLSearchParams();
  if (params?.after) qs.set("after", params.after);
  if (params?.type) qs.set("type", params.type);
  if (params?.limit) qs.set("limit", String(params.limit));
  const q = qs.toString();
  return get<EventListResponse>(
    `/missions/${missionId}/events${q ? `?${q}` : ""}`,
  );
}
