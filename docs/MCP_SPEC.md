# MCP Spec - Baton Studio

The MCP server exposes Baton Studio operations as tools for agents.

## Transport And Configuration

- Transport: stdio
- Backend URL: `BATON_BACKEND_URL`, default `http://localhost:8787`
- Production auth: set `BATON_API_KEY`; the MCP server forwards it as `Authorization: Bearer <token>`

All tools return JSON text content. Non-2xx backend responses are normalized into structured tool errors with `code`, `status`, `message`, and optional `detail`. Connection failures return an actionable `backend_unreachable` error that includes the configured backend URL.

## Tool List

### baton.health

Returns backend health and connection status.

### baton.list_types

Inputs:
- `mission_id`

Outputs:
- array of entity type definitions (`type_name`, `json_schema`, `invariants`)

### baton.read_world

Inputs:
- `mission_id`

Outputs:
- world snapshot with types, latest entity versions, and proposals

### baton.propose_patch

Inputs:
- `mission_id`
- `actor_id`
- `patch` with `ops[]`
- optional causal edges

Outputs:
- `proposal_id`
- `violations`

### baton.claim_baton

Inputs:
- `mission_id`
- `actor_id`
- `lease_ms` optional

Outputs:
- baton state

### baton.release_baton

Inputs:
- `mission_id`
- `actor_id`

Outputs:
- baton state

### baton.commit_patch

Inputs:
- `mission_id`
- `actor_id`
- `proposal_id`

Outputs:
- committed result and new versions

Failures:
- structured error when the actor does not hold the baton
- structured error when energy is insufficient

### baton.add_causal_edge

Inputs:
- `mission_id`
- `actor_id`
- `from_id`
- `to_id`
- `type`
- `metadata`

Outputs:
- `edge_id`

### baton.energy_balance

Inputs:
- `mission_id`
- `actor_id`

Outputs:
- balance and mission budget

### baton.energy_spend

Inputs:
- `mission_id`
- `actor_id`
- `amount`
- `reason`

Outputs:
- new balance

## Error Handling

Tool errors are JSON objects. Common `code` values:
- `backend_unreachable`
- `backend_http_error`
- `invalid_arguments`
- `unknown_tool`

Backend-originated `detail` is preserved when it is JSON; raw backend text is wrapped as `message`.
