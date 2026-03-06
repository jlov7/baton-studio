# Architecture — Baton Studio

## 1) High-level

Baton Studio is a local-first system with three runtime components:

1. **Substrate Server** (FastAPI)
   - persists state (SQLite)
   - enforces invariants
   - stores causal graph
   - tracks energy budgets
   - emits an append-only event stream

2. **MCP Server** (stdio or HTTP)
   - exposes substrate operations as MCP tools
   - proxies to Substrate Server HTTP API

3. **Control Room UI** (Next.js)
   - reads state snapshots over HTTP
   - subscribes to real-time events over WebSocket
   - renders World Model + Causal Graph + Timeline + HUD

---

## 2) Data model primitives

### 2.1 World Model
- `EntityType` — schema + invariants
- `Entity` — typed object instance
- `EntityVersion` — immutable versioned snapshot created on each commit

### 2.2 Causal Graph
- `CausalNode` — evidence/decision/plan/object-version/violation
- `CausalEdge` — typed edge (supports/depends/etc)

### 2.3 Energy Pool
- `EnergyAccount` — per agent + per mission
- `EnergyEvent` — spends and allocations

### 2.4 Baton
- `BatonState` — holder + queue + lease expiry

### 2.5 Event log
Append-only event store:
- `Event` { id, ts, type, actor, payload }

---

## 3) Write flows

### Flow A: Proposal (no baton)
- agent calls `propose_patch`
- server validates schema; soft invariants may be violated
- proposal stored as `PendingPatch`
- event emitted: `patch.proposed`

### Flow B: Commit (baton required)
- agent calls `commit_patch`
- server verifies baton holder
- server verifies hard invariants
- creates new EntityVersion(s)
- writes causal edges if provided
- updates energy accounts
- event emitted: `patch.committed`

---

## 4) Baton arbitration (MVP)
- baton is a lease:
  - claim → get lease until `now + lease_ms`
  - refresh lease allowed
  - release baton early allowed
  - timeout auto-releases
- queue is FIFO by default
- optional: queue priority weighted by energy balance

---

## 5) Structural continuity metric (SCk)
For MVP, define SCk as:

- Let `V(t)` be count of invalidated nodes at time t
- Let `I(t)` be count of invariant violations at time t (hard weighted > soft)
- Let `R(t)` be count of rollbacks/rejections at time t

Then:
- `SC(t) = exp(-α·V(t) - β·I(t) - γ·R(t))`
- `SCk` is the rolling average over last k events.

Expose:
- SC timeline
- SC current value in HUD

---

## 6) API surfaces

### HTTP
- `GET /health`
- `POST /missions`
- `GET /missions/{id}`
- `GET /missions/{id}/world`
- `POST /missions/{id}/patches/propose`
- `POST /missions/{id}/patches/commit`
- `POST /missions/{id}/baton/claim`
- `POST /missions/{id}/baton/release`
- `POST /missions/{id}/causal/edge`
- `GET /missions/{id}/events?after=...`

### WebSocket
- `WS /ws?mission_id=...`
- emits events from the append-only log

### MCP tools
See `docs/MCP_SPEC.md`

---

## 7) Storage
SQLite tables:
- missions
- entity_types
- entities
- entity_versions
- causal_nodes
- causal_edges
- energy_accounts
- baton_state
- patches (pending)
- events (append-only)

---

## 8) Demo simulation mode
- backend includes a simulator that:
  - spawns N async “agents”
  - they call the same patch/baton APIs
  - deterministic random seed ensures consistent demo

---

## 9) Deployment (MVP)
- single machine
- run via `make dev`
- optional Docker compose for portability
