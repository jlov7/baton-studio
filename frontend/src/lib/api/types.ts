// Mirrors backend Pydantic models exactly

export interface Actor {
  actor_id: string;
  actor_type: "agent" | "human" | "system";
  display_name: string;
}

export interface EventEnvelope {
  event_id: string;
  ts: string;
  mission_id: string;
  type: string;
  actor: Actor;
  payload: Record<string, unknown>;
}

export interface PatchOp {
  op: "upsert" | "delete";
  type: string;
  id: string;
  value: Record<string, unknown>;
}

export interface Patch {
  ops: PatchOp[];
}

export interface Violation {
  severity: "hard" | "soft";
  code: string;
  message: string;
}

// Mission
export interface CreateMissionRequest {
  title: string;
  goal?: string;
  energy_budget?: number;
  schema_pack?: string;
}

export interface MissionResponse {
  mission_id: string;
  created_at: string;
  title: string;
  goal: string;
  energy_budget: number;
  status: string;
}

export type MissionStatus = "idle" | "running" | "paused" | "exported";

// World
export interface EntityTypeSchema {
  type_name: string;
  json_schema: Record<string, unknown>;
  invariants: Record<string, unknown>[];
}

export interface EntityVersionDetail {
  version: number;
  created_at: string;
  actor_id: string;
  value: Record<string, unknown>;
}

export interface EntityDetail {
  entity_id: string;
  type_name: string;
  latest_version: number;
  value: Record<string, unknown>;
  versions: EntityVersionDetail[];
}

export interface WorldSnapshot {
  mission_id: string;
  entity_types: EntityTypeSchema[];
  entities: EntityDetail[];
  pending_proposals: number;
}

// Patches
export interface CausalEdgeInput {
  from: string;
  to: string;
  type: string;
  metadata?: Record<string, unknown>;
}

export interface ProposePatchRequest {
  actor_id: string;
  patch: Patch;
  causal?: { edges: CausalEdgeInput[] };
}

export interface ProposePatchResponse {
  proposal_id: string;
  accepted: boolean;
  violations: Violation[];
}

export interface CommitPatchRequest {
  actor_id: string;
  proposal_id: string;
}

export interface CommitPatchResponse {
  committed: boolean;
  new_versions: Record<string, unknown>[];
  message: string;
}

// Baton
export interface ClaimBatonRequest {
  actor_id: string;
  lease_ms?: number;
}

export interface BatonStateResponse {
  holder: string | null;
  queue: string[];
  lease_expires_at: string | null;
}

export interface ReleaseBatonRequest {
  actor_id: string;
}

// Causal
export interface AddEdgeRequest {
  actor_id: string;
  from_id: string;
  to_id: string;
  type: string;
  metadata?: Record<string, unknown>;
}

export interface AddEdgeResponse {
  edge_id: string;
}

export interface CausalNodeDetail {
  node_id: string;
  node_type: string;
  label: string;
  metadata: Record<string, unknown>;
  status: string;
}

export interface CausalEdgeDetail {
  edge_id: string;
  from_id: string;
  to_id: string;
  edge_type: string;
  metadata: Record<string, unknown>;
}

export interface CausalGraphSnapshot {
  mission_id: string;
  nodes: CausalNodeDetail[];
  edges: CausalEdgeDetail[];
}

// Energy
export interface EnergyBalanceResponse {
  actor_id: string;
  balance: number;
  mission_budget: number;
}

export interface EnergySpendRequest {
  actor_id: string;
  amount: number;
  reason?: string;
}

export interface EnergySpendResponse {
  new_balance: number;
}

// Events
export interface EventListResponse {
  events: EventEnvelope[];
  cursor: string | null;
}

// Agents
export interface RegisterAgentRequest {
  actor_id: string;
  display_name?: string;
  role?: string;
}

export interface AgentDetail {
  actor_id: string;
  display_name: string;
  role: string;
  joined_at: string;
  last_seen_at: string;
  status: string;
  energy_balance: number;
}

// Metrics
export interface SCPoint {
  ts: string;
  value: number;
}

export interface SCMetricResponse {
  sc_current: number;
  sc_history: SCPoint[];
}

// Health
export interface HealthResponse {
  ok: boolean;
  service: string;
  version: string;
}
