# Architecture - Baton Studio

## 1. High-Level

Baton Studio is a local-first system with three runtime components:

1. **Substrate Server** (FastAPI)
   - persists state with SQLite by default and Postgres-compatible `BATON_DATABASE_URL`
   - enforces invariants, baton ownership, mission existence, and energy spending
   - stores causal graph, world state, and append-only events
   - enforces production-mode scoped API key auth and configured CORS origins
   - exposes readiness and Prometheus-style runtime metrics

2. **MCP Server** (stdio)
   - exposes substrate operations as MCP tools
   - proxies to the Substrate Server HTTP API
   - forwards production API keys and normalizes backend errors

3. **Control Room UI** (Next.js)
   - reads state snapshots over HTTP
   - stores selected mission in `?mission=<mission_id>` with localStorage fallback
   - subscribes to real-time events over `WS /ws/{mission_id}`
   - renders Mission Control, World Model, Causal Graph, Timeline, and Export/Import

## 2. Data Model Primitives

### World Model

- `EntityType`: schema plus invariants
- `Entity`: typed object instance with optional delete provenance
- `EntityVersion`: immutable versioned snapshot created on commit

### Causal Graph

- `CausalNode`: evidence, decision, plan, object-version, violation, or derived node
- `CausalEdge`: typed edge such as supports or depends

### Energy Pool

- `EnergyAccount`: per agent and per mission
- energy events: allocations, rebalances, spends

### Baton

- `BatonState`: holder, FIFO queue, lease expiry

### Event Log

Append-only `Event` rows: id, timestamp, type, actor, payload.

## 3. Write Flows

### Proposal

- agent calls `propose_patch`
- server validates schema and invariants
- proposal is stored as `PatchRow`
- event emitted: `patch.proposed`

### Commit

- agent calls `commit_patch`
- server verifies mission, baton holder, hard invariants, and energy
- server creates new `EntityVersion` rows
- server writes causal edges and invalidates downstream nodes when needed
- event emitted: `patch.committed`

## 4. Baton Arbitration

- baton is a lease: claim, release, queue, timeout
- queue is FIFO
- claim/release/commit use row-level locking semantics where supported and preserve SQLite local mode

## 5. Structural Continuity Metric

For MVP:

- Let `V(t)` be invalidated nodes at time t
- Let `I(t)` be invariant violations at time t
- Let `R(t)` be rollbacks or rejections at time t

`SC(t) = exp(-alpha * V(t) - beta * I(t) - gamma * R(t))`

The backend exposes current and rolling structural continuity through `GET /missions/{id}/metrics/sc`.

## 6. Public Surfaces

### HTTP

- `GET /health`
- `GET /ready`
- `GET /metrics`
- `POST /missions`
- `GET /missions/{id}`
- `POST /missions/{id}/status`
- `GET /missions/{id}/world`
- `GET /missions/{id}/types`
- `POST /missions/{id}/patches/propose`
- `POST /missions/{id}/patches/commit`
- `POST /missions/{id}/baton/claim`
- `POST /missions/{id}/baton/release`
- `GET /missions/{id}/baton`
- `POST /missions/{id}/causal/edge`
- `GET /missions/{id}/causal/graph`
- `GET /missions/{id}/energy/{actor_id}`
- `POST /missions/{id}/energy/spend`
- `GET /missions/{id}/events?after=...`
- `GET /missions/{id}/agents`
- `POST /missions/{id}/agents`
- `GET /missions/{id}/metrics/sc`
- `POST /demo/start`
- `POST /missions/{id}/export`
- `POST /missions/import`

### WebSocket

- `WS /ws/{mission_id}`
- emits append-only event envelopes
- production mode accepts bearer auth or `?token=<token>`

### MCP

See `docs/MCP_SPEC.md`.

## 7. Storage And Runtime Controls

Schema details, indexes, foreign keys, and mission pack semantics are in `docs/DATA_MODEL.md`.

Runtime controls:
- `BATON_ENV=local|production`
- `BATON_DATABASE_URL=sqlite+aiosqlite:///...` or async Postgres URL
- `BATON_API_KEY=<admin-token>` for production compatibility mode
- `BATON_API_KEYS=read-token:reader,ops-token:operator,admin-token:admin` for scoped team mode
- `BATON_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
- `BATON_MAX_MISSION_PACK_BYTES=5000000`
- `BATON_EVENT_PAGE_LIMIT_MAX=500`

## 8. Demo Simulation Mode

The backend includes a deterministic simulator behind `POST /demo/start`. It creates a mission, agents, world state, causal edges, timeline events, and a balanced mission energy pool.

## 9. Verification

Before shipping changes:
- `make check`
- `make audit`
- `make e2e`
- frontend production build through `make demo` or `cd frontend && pnpm build`
