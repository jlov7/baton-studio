import { get } from "./client";
import type { EntityTypeSchema, WorldSnapshot } from "./types";

export function getWorld(missionId: string) {
  return get<WorldSnapshot>(`/missions/${missionId}/world`);
}

export function getTypes(missionId: string) {
  return get<EntityTypeSchema[]>(`/missions/${missionId}/types`);
}
