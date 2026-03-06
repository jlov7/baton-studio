import { get } from "./client";
import type { HealthResponse } from "./types";

export function checkHealth() {
  return get<HealthResponse>("/health");
}
