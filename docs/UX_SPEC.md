# UX / UI Spec — Baton Studio

**Design intent:** Baton Studio should feel like a *control room* for a live multi-agent mission.
Think: air traffic control + strategy game HUD + Figma-level polish.

**The UI is a primary deliverable**. Do not ship a generic dashboard template.

---

## 1) Visual identity

### Theme
- Dark, high-contrast base
- “Energy” and “Baton” use one accent color each
- Use subtle gradients + glow *sparingly* (tasteful)

### Typography
- System sans is fine, but use:
  - a distinct display weight for “Mission” title and hero states
  - monospaced font for IDs, hashes, schema versions, and patch diffs

### Layout language
- **Three-layer hierarchy**
  1. Mission HUD (always visible)
  2. Primary canvas (graph / world model)
  3. Inspector drawer (details / evidence / diff)

### Motion
- Baton transfers animate (short, snappy, satisfying)
- Energy drains animate (smooth; avoid jitter)
- Graph updates animate with spring transitions
- Never animate everything; only what communicates state change

---

## 2) Navigation and core screens

### Global layout (desktop first)
- Left rail:
  - Mission Control
  - World Model
  - Causal Graph
  - Timeline
  - Export / Packs
  - Settings
- Top HUD:
  - Mission name
  - Baton holder pill + queue length
  - Total energy + per-agent energy
  - Connection status (Backend + MCP)
- Right Inspector (resizable):
  - Context-sensitive details of selected entity/node/event

### Screen A: Mission Control (home)
**Hero panel**
- Mission title + status (Idle / Running / Paused / Exported)
- CTA buttons:
  - Load demo mission
  - Start simulation
  - Connect MCP agents
  - Export Mission Pack

**Squad strip**
- Cards per agent:
  - role
  - current activity
  - energy remaining
  - last commit / last proposal
  - error badge (if any)

**KPIs**
- Structural Continuity (SCk)
- Invariant violations (hard/soft)
- Causal invalidations triggered

**“Demo mode” callout**
- 1 click to load demo mission; no API keys.

### Screen B: World Model
- Left: typed object list grouped by entity type
- Center: object detail canvas
  - show version history as a vertical timeline
- Inspector:
  - Schema + invariant list
  - Diffs between versions
  - Provenance: which causal nodes reference this object

**Interactions**
- Filter by:
  - type
  - tag
  - owner agent
  - changed in last N minutes
- “Proposals” vs “Committed” toggle

### Screen C: Causal Graph (the wow view)
- Center: interactive graph (React Flow)
- Node types:
  - Evidence (file/tool/url)
  - Decision
  - Plan Step
  - World Object Version
  - Invariant Violation
- Edge types:
  - supports / contradicts / depends_on / derived_from / invalidates

**Graph affordances**
- Hover: preview tooltip (title, agent, timestamp, status)
- Click: pin selection → inspector shows full details
- Search: find nodes by ID, label, tag
- Lenses (toggle overlays):
  - “Show only disputed nodes”
  - “Show stale/invalidation chain”
  - “Show agent attribution heatmap”
  - “Show energy spend along edges” (optional)

### Screen D: Timeline (replay)
- Scrollable event stream with:
  - baton transfers
  - proposals
  - commits
  - invariant violations
  - energy spend
  - invalidation propagations
- Time scrubber:
  - playback controls (play/pause/step)
  - jump to next violation / next baton transfer
- “Replay mode”
  - loads a Mission Pack and replays events deterministically

### Screen E: Export / Mission Packs
- Export:
  - snapshot + graph + event log
  - optional HTML summary
- Import:
  - load a pack and open in replay mode
- “Share”
  - generate a single-file `report.html` for stakeholders

---

## 3) Onboarding that doesn’t suck

### First run
- Auto-detect backend; if missing show:
  - “Start backend: make dev”
- Primary CTA is **Load demo mission**
- After loading demo:
  - show a guided tour (3 steps max)
  - highlight baton, energy, graph node click

### Empty states
- Always show a clear next action:
  - “Load demo mission”
  - “Connect MCP”
  - “Start simulation”

---

## 4) Micro-interactions (the “sexy” part)

- Baton pill animates on transfer:
  - short glow pulse + subtle slide to new holder
- Agent card:
  - activity indicator (typing / thinking / committing)
  - energy bar drains smoothly
- Invariant violation:
  - toast with “view in graph” button
  - graph auto-focuses to violation chain (optional)
- Commit success:
  - satisfying “snap” animation as proposal becomes committed

---

## 5) Accessibility & polish
- Keyboard navigation:
  - search focus `/`
  - next/prev node `j/k`
- Color contrast:
  - do not rely on color alone; use icons/labels
- Performance:
  - virtualize long lists (timeline)
  - throttle graph layout recomputation

---

## 6) Visual verification
- Include Playwright smoke tests that:
  - load home page
  - load demo mission
  - start simulation
  - verify baton holder updates at least once
  - verify at least 10 events rendered in timeline
- Generate screenshots to `assets/ui/`:
  - mission-control.png
  - causal-graph.png
  - world-model.png
