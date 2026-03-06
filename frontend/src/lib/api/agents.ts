import { get, post } from "./client";
import type { AgentDetail, RegisterAgentRequest } from "./types";

export function listAgents(missionId: string) {
  return get<AgentDetail[]>(`/missions/${missionId}/agents`);
}

export function registerAgent(missionId: string, req: RegisterAgentRequest) {
  return post<AgentDetail>(`/missions/${missionId}/agents`, req);
}
