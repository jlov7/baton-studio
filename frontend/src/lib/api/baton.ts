import { get, post } from "./client";
import type { BatonStateResponse, ClaimBatonRequest, ReleaseBatonRequest } from "./types";

export function claimBaton(missionId: string, req: ClaimBatonRequest) {
  return post<BatonStateResponse>(`/missions/${missionId}/baton/claim`, req);
}

export function releaseBaton(missionId: string, req: ReleaseBatonRequest) {
  return post<BatonStateResponse>(`/missions/${missionId}/baton/release`, req);
}

export function getBatonState(missionId: string) {
  return get<BatonStateResponse>(`/missions/${missionId}/baton`);
}
