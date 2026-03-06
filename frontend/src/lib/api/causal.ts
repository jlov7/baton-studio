import { get, post } from "./client";
import type { AddEdgeRequest, AddEdgeResponse, CausalGraphSnapshot } from "./types";

export function addEdge(missionId: string, req: AddEdgeRequest) {
  return post<AddEdgeResponse>(`/missions/${missionId}/causal/edge`, req);
}

export function getGraph(missionId: string) {
  return get<CausalGraphSnapshot>(`/missions/${missionId}/causal/graph`);
}
