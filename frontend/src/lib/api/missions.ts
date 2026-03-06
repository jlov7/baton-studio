import { get, post } from "./client";
import type { CreateMissionRequest, MissionResponse, MissionStatus } from "./types";

export function createMission(req: CreateMissionRequest) {
  return post<MissionResponse>("/missions", req);
}

export function getMission(missionId: string) {
  return get<MissionResponse>(`/missions/${missionId}`);
}

export function updateMissionStatus(missionId: string, status: MissionStatus) {
  return post<MissionResponse>(`/missions/${missionId}/status`, { status });
}
