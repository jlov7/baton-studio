# API Spec — Baton Studio Substrate Server

This spec is the contract between:
- Control Room UI
- MCP server
- any SDK wrappers

All payloads are JSON.

---

## Common types

### Actor
```json
{
  "actor_id": "agent:planner-1",
  "actor_type": "agent|human|system",
  "display_name": "Planner 1"
}
```

### Event envelope
```json
{
  "event_id": "evt_...",
  "ts": "2026-03-06T12:34:56Z",
  "mission_id": "mis_...",
  "type": "patch.proposed|patch.committed|baton.claimed|...",
  "actor": { "...": "..." },
  "payload": { }
}
```

---

## Endpoints (MVP)

### GET /health
**200**
```json
{ "ok": true, "service": "baton-substrate", "version": "0.1.0" }
```

### POST /missions
Create a mission.

**Request**
```json
{
  "title": "Client delivery: API migration",
  "goal": "Ship v2 endpoints with tests",
  "energy_budget": 1000,
  "schema_pack": "default"
}
```

**Response**
```json
{
  "mission_id": "mis_123",
  "created_at": "...",
  "title": "...",
  "goal": "...",
  "energy_budget": 1000
}
```

### GET /missions/{id}/world
Returns:
- entity types
- latest entity versions
- pending proposals (optional)

### POST /missions/{id}/patches/propose
**Request**
```json
{
  "actor_id": "agent:researcher-1",
  "patch": {
    "ops": [
      { "op": "upsert", "type": "PlanStep", "id": "step:1", "value": { "text": "Provision servers", "status": "proposed" } }
    ]
  },
  "causal": {
    "edges": [
      { "from": "evidence:ticket-123", "to": "step:1", "type": "supports" }
    ]
  }
}
```

**Response**
```json
{
  "proposal_id": "prop_abc",
  "accepted": true,
  "violations": [
    { "severity": "soft", "code": "PLANSTEP_MISSING_OWNER", "message": "PlanStep.owner is recommended" }
  ]
}
```

### POST /missions/{id}/baton/claim
**Request**
```json
{ "actor_id": "agent:planner-1", "lease_ms": 20000 }
```

**Response**
```json
{
  "holder": "agent:planner-1",
  "queue": ["agent:critic-1"],
  "lease_expires_at": "..."
}
```

### POST /missions/{id}/patches/commit
Requires baton.

**Request**
```json
{
  "actor_id": "agent:planner-1",
  "proposal_id": "prop_abc"
}
```

**Response**
```json
{
  "committed": true,
  "new_versions": [
    { "entity_id": "step:1", "version": 2 }
  ]
}
```

### WebSocket /ws?mission_id=...
Server emits Event envelopes.

Client may send:
- ping
- subscribe/unsubscribe
