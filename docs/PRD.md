# PRD — Baton Studio

## 1. Summary

**Baton Studio** is a local-first “Control Room” for coordinating *multi-agent teams* through a **shared cognitive substrate**, not message passing.

It introduces three explicit shared primitives:

1) **Shared World Model** — typed state with invariants and versioned history  
2) **Shared Causal Graph** — explicit dependencies / attribution paths across agents  
3) **Shared Energy Pool** — resource-aware arbitration under budget constraints  

Plus a coordination mechanism:

4) **Baton Arbitration** — explicit write-rights handoff to avoid conflict and “dueling agents”

The output is a visceral, demoable system that makes agent coordination *legible*:
- you can **see** who holds the baton,
- you can **see** causality and dependency chains,
- you can **see** budget burn,
- and you can **replay** the substrate event stream.

---

## 2. Problem

Teams increasingly run “agent squads” (coding agents, research agents, analyst agents).  
Even with multi-agent support, most coordination happens through **text**:
- chat messages,
- task lists,
- summaries of findings.

This creates predictable failure modes:
- information loss (typed structures collapse into prose)
- consistency failures (contradictory beliefs and overwrites)
- coordination overhead (token bandwidth becomes system bandwidth)

Baton Studio is a productized, hands-on prototype for the *next coordination paradigm*.

---

## 3. Goals

### Primary goals (MVP)
- Provide a substrate server with a **typed world model** and invariant checks.
- Provide a **causal graph** to track dependencies and provenance.
- Provide **baton arbitration** to coordinate writes.
- Provide an **energy pool** to track and allocate budgets.
- Provide a **premium UI** that makes all of this visceral and explorable.
- Provide a **demo mode** with simulated agents (no API keys).
- Provide a **real mode** via MCP so Claude Code / MCP clients can use the substrate.

### Secondary goals
- Export/share “Mission Packs” (world snapshot + causal graph + event log).
- Compute **Structural Continuity** metrics as a stability KPI.
- Provide onboarding and a demo script suitable for internal presentations.

---

## 4. Non-goals (keep scope sane)
- Not a full agent framework (LangGraph replacement).
- Not a full security product (keep minimal privacy + access controls).
- Not full distributed consensus (single-machine substrate for MVP).
- Not perfect deterministic LLM reproducibility.

---

## 5. Users and personas

### Persona A — Innovation team engineer (primary)
- Runs Claude Code daily
- Wants to coordinate multiple agents reliably and explainably
- Needs tangible artifacts to share internally

### Persona B — Tech lead / partner audience (secondary)
- Wants to “see what changed” and “who did what”
- Values provenance, accountability, and resource controls

---

## 6. User journeys (MVP)

### Journey 1 — 1-click demo (no keys)
1. Open UI → click **Load demo mission**
2. Watch 4 simulated agents contend for baton while building a plan
3. Inspect:
   - rejected invariant violations
   - causal lineage of a key decision
   - energy spend by agent
4. Export Mission Pack

### Journey 2 — Real agents via MCP (Claude Code)
1. Run backend + UI + MCP server
2. Add MCP server to Claude Code (stdio)
3. Start a Claude Code agent team (lead + 3 teammates)
4. Instruct teammates to:
   - read world model
   - propose plan steps
   - add causal edges (why)
   - request baton to commit
5. Observe mission in Control Room UI in real time

### Journey 3 — Post-mortem replay
1. Load a Mission Pack
2. Scrub timeline (event log)
3. See:
   - baton transfers
   - invalidations propagated via causal graph
   - structural continuity score over time

---

## 7. Functional requirements

### Shared World Model
- Typed entities with JSON schema per entity type
- CRUD operations via “patches”
- Invariant engine:
  - hard invariants (reject)
  - soft invariants (accept as proposal, needs baton commit)

### Shared Causal Graph
- Nodes reference:
  - world entity versions
  - evidence artifacts (file paths, URLs, tool results)
  - decisions / plan steps
- Typed edges: supports, contradicts, depends_on, derived_from, invalidates
- “Invalidate propagation”:
  - updating a node can mark downstream nodes “stale”

### Energy Pool
- Budget per mission, and per agent
- Spend events logged and visible
- Policy: baton acquisition can be weighted by remaining energy (optional)

### Baton Arbitration
- Baton is a mutex with UX:
  - holder, queue, timeout, forced release
- Two write flows:
  - propose patch (no baton)
  - commit patch (baton required)

### Export / Import
- Mission Pack includes:
  - world snapshot
  - causal graph snapshot
  - event log
  - schema versions

### Auditability
- Append-only event log; every mutation is an event.

---

## 8. UX requirements (high level)
See `docs/UX_SPEC.md` (non-negotiable).

---

## 9. Success criteria
- Demo mode works in < 60 seconds from `make dev`.
- A real MCP client can:
  - read world model
  - propose + commit patches with baton
  - add causal edges
- UI makes baton + causality + energy legible without reading docs.
