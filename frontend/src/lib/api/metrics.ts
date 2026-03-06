import { get } from "./client";
import type { SCMetricResponse } from "./types";

export function getSCMetric(missionId: string) {
  return get<SCMetricResponse>(`/missions/${missionId}/metrics/sc`);
}
