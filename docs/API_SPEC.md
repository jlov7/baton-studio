# API Spec - Baton Studio Substrate Server

This spec is the contract between the Control Room UI, MCP server, and SDK wrappers. JSON endpoints use UTF-8 JSON request and response bodies. Mission pack export/import uses zip files as described below.

## Runtime Modes

`BATON_ENV=local` is the default and keeps the local demo flow frictionless. HTTP and WebSocket calls do not require auth in local mode.

`BATON_ENV=production` requires `BATON_API_KEY` or `BATON_API_KEYS`. All non-public HTTP routes require:

```http
Authorization: Bearer <token>
```

WebSocket clients can use either the same `Authorization` header or `?token=<token>`. `/health`, `/ready`, `/docs`, `/redoc`, and `/openapi.json` remain public. CORS is configured by `BATON_CORS_ORIGINS` as a comma-separated list; wildcard origins are not used in production.

`BATON_API_KEY` is a single admin token. `BATON_API_KEYS` supports scoped tokens in `token:role,token:role` form. Roles are `reader`, `operator`, and `admin`.

- `reader`: read routes, WebSocket subscription, runtime metrics
- `operator`: reader plus mutating mission operations
- `admin`: operator plus mission import

Every HTTP response includes `x-request-id`; callers may provide one with the same header.

API responses also include defensive headers: `x-content-type-options: nosniff`, `referrer-policy: no-referrer`, and `x-frame-options: DENY`. Production mode adds HSTS.

## Common Types

### Actor

```json
{
  "actor_id": "agent:planner-1",
  "actor_type": "agent|human|system",
  "display_name": "Planner 1"
}
```

### Event Envelope

```json
{
  "event_id": "evt_...",
  "ts": "2026-03-06T12:34:56Z",
  "mission_id": "mis_...",
  "type": "patch.proposed|patch.committed|baton.claimed|...",
  "actor": { "...": "..." },
  "payload": {}
}
```

Stable event taxonomy:
- `mission.created`, `mission.status_changed`
- `agent.joined`
- `baton.claimed`, `baton.queued`, `baton.transferred`, `baton.released`, `baton.timeout`
- `patch.proposed`, `patch.committed`
- `causal.edge_added`, `causal.invalidated`
- `energy.allocated`, `energy.rebalanced`, `energy.spent`

## Endpoints

### GET /health

```json
{
  "ok": true,
  "service": "baton-substrate",
  "version": "0.1.0",
  "mode": "local",
  "auth_required": false,
  "ready": true,
  "auth_modes": ["bearer"]
}
```

`ready` is false in production mode when neither `BATON_API_KEY` nor `BATON_API_KEYS` is configured.

### GET /ready

Readiness probe for deploy platforms. Returns `503` when database or production auth configuration is not ready.

```json
{ "ok": true, "database": true, "auth": true }
```

### GET /metrics

Prometheus-style runtime metrics. Requires `reader` role in production mode.

### POST /missions

Create a mission.

Request:

```json
{
  "title": "Client delivery: API migration",
  "goal": "Ship v2 endpoints with tests",
  "energy_budget": 1000,
  "schema_pack": "default"
}
```

`schema_pack` is accepted for forward compatibility; the current implementation uses the default schema pack.

Response:

```json
{
  "mission_id": "mis_123",
  "created_at": "...",
  "title": "...",
  "goal": "...",
  "energy_budget": 1000,
  "status": "idle"
}
```

### GET /missions/{mission_id}

Returns mission metadata or `404`.

### POST /missions/{mission_id}/status

```json
{ "status": "idle|running|paused|exported" }
```

### GET /missions/{mission_id}/world

Returns entity type definitions and latest non-deleted entity versions.

### GET /missions/{mission_id}/types

Returns registered entity type definitions.

### POST /missions/{mission_id}/patches/propose

```json
{
  "actor_id": "agent:researcher-1",
  "patch": {
    "ops": [
      {
        "op": "upsert",
        "type": "PlanStep",
        "id": "step:1",
        "value": { "text": "Provision servers", "status": "proposed" }
      }
    ]
  },
  "causal": {
    "edges": [
      { "from": "evidence:ticket-123", "to": "step:1", "type": "supports" }
    ]
  }
}
```

Response:

```json
{
  "proposal_id": "prop_abc",
  "accepted": true,
  "violations": []
}
```

### POST /missions/{mission_id}/baton/claim

```json
{ "actor_id": "agent:planner-1", "lease_ms": 20000 }
```

`lease_ms` must be positive and no more than 300000.

### GET /missions/{mission_id}/baton

Returns the current holder, queue, and lease expiry.

### POST /missions/{mission_id}/baton/release

```json
{ "actor_id": "agent:planner-1" }
```

### POST /missions/{mission_id}/patches/commit

Requires baton.

```json
{
  "actor_id": "agent:planner-1",
  "proposal_id": "prop_abc"
}
```

Response:

```json
{
  "committed": true,
  "new_versions": [
    { "entity_id": "step:1", "version": 2 }
  ],
  "message": ""
}
```

Commits are rejected when the actor does not hold the baton or cannot spend the estimated commit energy cost.

### POST /missions/{mission_id}/causal/edge

```json
{
  "actor_id": "agent:planner-1",
  "from_id": "evidence:ticket-123",
  "to_id": "step:1",
  "type": "supports",
  "metadata": {}
}
```

Response:

```json
{ "edge_id": "edg_..." }
```

### GET /missions/{mission_id}/causal/graph

Returns causal nodes and edges.

### GET /missions/{mission_id}/energy/{actor_id}

Returns actor balance and mission budget. Missing accounts are created with zero balance.

### POST /missions/{mission_id}/energy/spend

```json
{ "actor_id": "agent:planner-1", "amount": 20, "reason": "commit:prop_abc" }
```

`amount` must be positive. Overspends are rejected.

### GET /missions/{mission_id}/events

Query params:
- `after`: optional stable cursor in `ts|event_id` form
- `type`: optional event type filter
- `limit`: 1..`BATON_EVENT_PAGE_LIMIT_MAX`, capped server-side

Events are ordered by `(ts, event_id)` and response includes the next cursor.

### GET /missions/{mission_id}/agents

Returns mission agents.

### POST /missions/{mission_id}/agents

Registers or refreshes an agent.

### GET /missions/{mission_id}/metrics/sc

Returns structural continuity metrics.

### POST /demo/start

Runs the deterministic demo simulation and returns:

```json
{ "mission_id": "mis_...", "status": "completed" }
```

### POST /missions/{mission_id}/export

Returns `application/zip` containing exactly one file: `mission_pack.json`.

### POST /missions/import

Multipart form upload:
- field name: `file`
- max size: `BATON_MAX_MISSION_PACK_BYTES`

Success:

```json
{ "mission_id": "mis_...", "status": "imported" }
```

Duplicate mission IDs return `409`; invalid packs return `400`; oversized uploads return `413`.

### WebSocket /ws/{mission_id}

Server emits Event envelopes for the mission. In production mode, authenticate with `Authorization: Bearer <token>` or `?token=<token>`.

Clients may send any text frame to keep the socket alive; subscription is scoped by the URL mission ID.
