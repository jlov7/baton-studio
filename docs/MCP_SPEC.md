# MCP Spec — Baton Studio

The MCP server exposes Baton Studio operations as tools for agents.

## Tool list (MVP)

### baton.health
- returns backend health + connection status

### baton.list_types
Inputs:
- mission_id
Outputs:
- array of entity type definitions (type_name, json_schema, invariants)

### baton.read_world
Inputs:
- mission_id
Outputs:
- world snapshot (types + latest versions + proposals)

### baton.propose_patch
Inputs:
- mission_id
- actor_id
- patch { ops[] }
- optional causal edges
Outputs:
- proposal_id, violations

### baton.claim_baton
Inputs:
- mission_id
- actor_id
- lease_ms (optional)
Outputs:
- baton state

### baton.release_baton
Inputs:
- mission_id
- actor_id
Outputs:
- baton state

### baton.commit_patch
Inputs:
- mission_id
- actor_id
- proposal_id
Outputs:
- committed result + new versions

### baton.add_causal_edge
Inputs:
- mission_id
- actor_id
- from_id, to_id, type, metadata
Outputs:
- edge_id

### baton.energy_balance
Inputs:
- mission_id
- actor_id
Outputs:
- balance + mission budget

### baton.energy_spend
Inputs:
- mission_id
- actor_id
- amount
- reason
Outputs:
- new balance

## Transport
- Prefer stdio for local operation.
- Backend base URL default: http://localhost:8787
- MCP server should accept env var: BATON_BACKEND_URL

## Error handling
- On invariant violation: return tool error with:
  - code
  - message
  - violations array
- On baton denied: return error with current holder and queue
