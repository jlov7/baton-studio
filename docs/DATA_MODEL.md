# Data Model — Baton Studio (SQLite)

This is the recommended baseline schema. It is designed for:
- local-first persistence
- replayable audit logs
- deterministic exports

---

## Tables

### missions
- mission_id TEXT PK
- created_at TEXT
- title TEXT
- goal TEXT
- energy_budget INTEGER

### entity_types
- mission_id TEXT
- type_name TEXT
- json_schema TEXT
- invariants_json TEXT
PK (mission_id, type_name)

### entities
- mission_id TEXT
- entity_id TEXT
- type_name TEXT
PK (mission_id, entity_id)

### entity_versions
- mission_id TEXT
- entity_id TEXT
- version INTEGER
- created_at TEXT
- actor_id TEXT
- value_json TEXT
PK (mission_id, entity_id, version)

### patches (pending proposals)
- mission_id TEXT
- proposal_id TEXT PK
- created_at TEXT
- actor_id TEXT
- patch_json TEXT
- violations_json TEXT
- status TEXT (pending|committed|rejected)

### causal_nodes
- mission_id TEXT
- node_id TEXT
- node_type TEXT
- label TEXT
- metadata_json TEXT
PK (mission_id, node_id)

### causal_edges
- mission_id TEXT
- edge_id TEXT
- from_id TEXT
- to_id TEXT
- edge_type TEXT
- metadata_json TEXT
PK (mission_id, edge_id)

### energy_accounts
- mission_id TEXT
- actor_id TEXT
- balance INTEGER
PK (mission_id, actor_id)

### baton_state
- mission_id TEXT PK
- holder_actor_id TEXT
- queue_json TEXT
- lease_expires_at TEXT

### events (append-only)
- mission_id TEXT
- event_id TEXT PK
- ts TEXT
- type TEXT
- actor_json TEXT
- payload_json TEXT

---

## Exports (“Mission Pack”)
A mission pack is a folder (and zipped file) containing:
- mission.json
- world_snapshot.json
- causal_graph.json
- events.ndjson
- schemas.json
