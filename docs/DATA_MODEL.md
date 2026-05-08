# Data Model - Baton Studio

The schema is implemented with SQLAlchemy 2.0 typed ORM (`Mapped` and `mapped_column`) and is designed for:
- local-first persistence
- replayable audit logs
- deterministic exports
- SQLite local mode and `BATON_DATABASE_URL` compatibility with Postgres

## Migrations

Alembic migration support lives in `backend/migrations`. Fresh local startup still creates tables automatically for frictionless demos; production deployments should run:

```bash
cd backend && uv run alembic upgrade head
```

## Tables

### missions

- mission_id TEXT PK
- created_at TEXT
- title TEXT
- goal TEXT
- energy_budget INTEGER
- status TEXT (idle|running|paused|exported) DEFAULT 'idle'

### entity_types

- mission_id TEXT
- type_name TEXT
- json_schema TEXT
- invariants_json TEXT
- PK (mission_id, type_name)
- FK mission_id -> missions.mission_id

### entities

- mission_id TEXT
- entity_id TEXT
- type_name TEXT
- deleted_at TEXT NULL
- deleted_by TEXT NULL
- PK (mission_id, entity_id)
- FK mission_id -> missions.mission_id

### entity_versions

- mission_id TEXT
- entity_id TEXT
- version INTEGER
- created_at TEXT
- actor_id TEXT
- value_json TEXT
- PK (mission_id, entity_id, version)
- FK (mission_id, entity_id) -> entities
- Index: (mission_id, entity_id, version)

### patches

- mission_id TEXT
- proposal_id TEXT PK
- created_at TEXT
- actor_id TEXT
- patch_json TEXT
- violations_json TEXT
- status TEXT (pending|committed|rejected)
- Index: (mission_id, status), (mission_id, created_at)

### causal_nodes

- mission_id TEXT
- node_id TEXT
- node_type TEXT
- label TEXT
- status TEXT (valid|stale) DEFAULT 'valid'
- metadata_json TEXT
- PK (mission_id, node_id)
- Index: (mission_id, status)

### causal_edges

- mission_id TEXT
- edge_id TEXT
- from_id TEXT
- to_id TEXT
- edge_type TEXT
- metadata_json TEXT
- PK (mission_id, edge_id)
- FK (mission_id, from_id) -> causal_nodes
- FK (mission_id, to_id) -> causal_nodes
- Index: (mission_id, from_id), (mission_id, to_id)

### energy_accounts

- mission_id TEXT
- actor_id TEXT
- balance INTEGER
- PK (mission_id, actor_id)
- Index: mission_id

### baton_state

- mission_id TEXT PK
- holder_actor_id TEXT
- queue_json TEXT
- lease_expires_at TEXT

### events

- mission_id TEXT
- event_id TEXT PK
- ts TEXT
- type TEXT
- actor_json TEXT
- payload_json TEXT
- Index: (mission_id, ts, event_id), (mission_id, type, ts)

### agents

- mission_id TEXT
- actor_id TEXT
- display_name TEXT
- role TEXT
- joined_at TEXT
- last_seen_at TEXT
- status TEXT (active|idle)
- PK (mission_id, actor_id)
- Index: (mission_id, status)

## Exports: Mission Pack

A mission pack is a `.zip` archive containing only `mission_pack.json`.

The JSON root includes:

```json
{
  "schema_version": 1,
  "mission": { "mission_id": "mis_...", "title": "...", "goal": "..." },
  "entity_types": [],
  "entities": [],
  "entity_versions": [],
  "patches": [],
  "causal_nodes": [],
  "causal_edges": [],
  "energy_accounts": [],
  "baton_state": {},
  "agents": [],
  "events": []
}
```

Imports reject duplicate mission IDs and unsupported schema versions. Event payloads are stored as payload objects; legacy nested payloads are parsed during export for compatibility.
