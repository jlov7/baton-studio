import { get, post } from "./client";
import type { EnergyBalanceResponse, EnergySpendRequest, EnergySpendResponse } from "./types";

export function getBalance(missionId: string, actorId: string) {
  return get<EnergyBalanceResponse>(`/missions/${missionId}/energy/${actorId}`);
}

export function spendEnergy(missionId: string, req: EnergySpendRequest) {
  return post<EnergySpendResponse>(`/missions/${missionId}/energy/spend`, req);
}
