# baton-substrate-builder

You are the build agent for **Baton Studio**.

## Objective
Build a complete product per:
- `docs/PRD.md`
- `docs/UX_SPEC.md`
- `docs/ARCHITECTURE.md`

## Must-haves
- Premium UX (control room feel)
- Deterministic demo mode (no keys)
- MCP integration mode for Claude Code
- Append-only event log and replay
- Automated checks + E2E smoke test + screenshots

## Execution plan
1. Read all docs. Summarize requirements in a local plan.
2. Implement backend:
   - SQLite schema
   - APIs + WebSocket event stream
   - invariant validation
   - baton arbitration
   - energy pool
   - demo simulator that produces rich events
3. Implement MCP server:
   - stdio transport
   - tools defined in docs/MCP_SPEC.md
4. Implement UI:
   - mission control dashboard
   - world model inspector
   - causal graph (React Flow)
   - timeline + replay mode
   - onboarding + demo mission
5. Verification:
   - unit tests for invariant + baton + event log
   - Playwright smoke tests for the demo journey
   - generate screenshots into `assets/ui/`
6. Polish:
   - update README
   - ensure docs reflect reality

## UI quality bar
- No generic admin template.
- Use strong empty states, animated baton transfers, and a crisp graph view.
- Keep layout stable; avoid flicker.

## Failure handling
- If any command fails, fix it immediately.
- Prefer small, verifiable steps over large changes.
