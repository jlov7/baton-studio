# Baton Studio

**Baton Studio** is a *substrate-native* coordination layer for multi-agent teams:

- **Shared World Model**: typed state with invariants + versioned history
- **Shared Causal Graph**: explicit dependencies + attribution paths across agents
- **Shared Energy Pool**: budget-aware arbitration across agents and tasks
- **Baton Arbitration**: explicit, visible write-rights handoff (no “who overwrote what?”)

It ships as a **local-first** app:
- **Substrate Server** (FastAPI) with a real-time event stream (WebSocket)
- **MCP Server** so Claude Code / other MCP clients can read/write the substrate
- **Control Room UI** (Next.js) to watch state, causality, and budgets evolve live

---

## Why this exists

Most agent “teams” still coordinate by **text-passing** (messages, task lists, summaries). Baton Studio implements the next step: agents coordinate through *explicit shared structures* that are **typed, auditable, and conflict-managed**.

---

## What you can do

### 1) Run a “Mission”
- Create a mission (goal, constraints, artifacts, milestones)
- Invite agents (real MCP-connected, or simulated demo agents)
- Watch the mission evolve in a single shared substrate

### 2) See a live Causal Graph
Every state update is linked to:
- upstream evidence nodes,
- dependent plan nodes,
- and downstream effects.

Click any node to see provenance and who/what it depends on.

### 3) Enforce invariants on write
The World Model is schema-bound. Writes that violate invariants:
- are rejected (hard), or
- are accepted as **proposals** awaiting baton-holder commit.

### 4) Budgeted arbitration (Energy Pool)
Agents spend “energy” to propose actions (LLM calls, tool calls, commits).  
The system can:
- throttle noisy agents,
- prioritize critical tasks,
- or allocate budgets by role.

---

## Quickstart (dev)

### Prereqs
- Python 3.11+
- Node 20+
- (Optional) Docker

### Commands
```bash
make dev
```

This runs:
- backend on `http://localhost:8787`
- frontend on `http://localhost:3000`
- mcp server (stdio) for local Claude Code integration (optional)

---

## Claude Code integration (MCP)

Baton Studio ships an MCP server so Claude Code agents can call tools like:
- `baton.read_world`
- `baton.propose_patch`
- `baton.claim_baton` / `baton.release_baton`
- `baton.add_causal_edge`
- `baton.energy_balance`

See: `docs/CLAUDE_CODE_INTEGRATION.md`

---

## Demo

Run:
```bash
make demo
```

This starts **simulated agents** (no API keys) that:
- propose plan steps in parallel,
- contend for the baton,
- update the causal graph,
- and drain/refill energy budgets.

Use the UI to:
- watch baton transfers,
- inspect rejected invariant violations,
- and track the causal lineage of each decision.

---

## Repo structure

- `backend/` FastAPI substrate server + SQLite storage + schemas
- `frontend/` Next.js control room UI
- `mcp_server/` MCP server exposing substrate operations as tools
- `docs/` PRD, UX spec, API specs, data model, troubleshooting
- `assets/` brand + diagrams

---

## Screenshots

Add screenshots after first run:
- `assets/ui/mission-control.png`
- `assets/ui/causal-graph.png`
- `assets/ui/world-model.png`

---

## License

MIT for starter pack. Adjust for your organization.
