# Contributing to Baton Studio

Thank you for your interest in contributing. This guide covers everything you need to go from zero to a merged PR.

---

## Table of Contents

- [Development setup](#development-setup)
- [Project structure](#project-structure)
- [Running tests](#running-tests)
- [Code conventions](#code-conventions)
- [Making changes](#making-changes)
- [Pull request process](#pull-request-process)
- [What we welcome](#what-we-welcome)
- [What to avoid](#what-to-avoid)

---

## Development Setup

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://www.python.org/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) or `fnm install 20` |
| pnpm | 9+ | `npm install -g pnpm` |

### First-time setup

```bash
# Clone the repo
git clone <repo-url> baton-studio
cd baton-studio

# Start both services in watch mode
make dev
```

This installs all dependencies (Python via `uv sync`, Node via `pnpm install`) and starts:
- Backend: `http://localhost:8787` (FastAPI, hot-reload)
- Frontend: `http://localhost:3000` (Next.js, HMR)

The SQLite database is created automatically at `backend/baton.db` on first run.

---

## Project Structure

```
backend/baton_substrate/
  api/           HTTP routes + WebSocket
  db/            SQLAlchemy async engine + schema migrations
  demo/          Deterministic demo simulator + agent behaviors
  invariants/    Hard + soft invariant engine
  models/        Pydantic request/response types
  services/      Business logic (pure, testable)
  ws/            WebSocket connection manager + broadcaster

frontend/src/
  app/           Next.js App Router pages
  components/    UI components (graph, hud, layout, mission, timeline, world)
  lib/           API clients, hooks, context, state

mcp_server/baton_mcp/
  server.py      Tool registrations
  client.py      httpx wrapper for backend
  tools/         One module per tool group
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full technical design.

---

## Running Tests

```bash
# Full quality gate (run before every commit)
make check

# Individual checks
cd backend
uv run ruff check .                         # Python lint
uv run mypy baton_substrate                  # Python type check
uv run pytest tests/ -v                     # 70 unit + integration tests

cd frontend
pnpm lint                                    # ESLint
pnpm typecheck                              # tsc --noEmit
```

```bash
# End-to-end tests (requires make dev running in another terminal)
make e2e

# Single E2E spec
cd frontend && pnpm exec playwright test tests/mission-control.spec.ts
```

**Backend tests use an in-memory SQLite database.** They don't touch `baton.db`. Tests are fast (~1 second total).

---

## Code Conventions

### Python

- **Type hints on all public functions** — mypy strict mode, no `Any`
- **Pydantic models** for all request/response types — never raw dicts across boundaries
- **`async`/`await` everywhere** — all service functions are async; never block the event loop
- **Services are pure** — no direct DB access in API routes; always go through a service
- **uv only** — `uv add <package>`, never `pip install`
- **Formatter**: `ruff format` (runs automatically in `make check`)
- **Linter**: `ruff check` — fix all warnings before submitting

```python
# Good — typed, async, through service layer
@router.post("/missions/{mission_id}/patches/propose")
async def propose_patch(
    mission_id: str,
    req: ProposePatchRequest,
    db: AsyncSession = Depends(get_db),
) -> ProposePatchResponse:
    return await patch_service.propose(db, mission_id, req)
```

### TypeScript / React

- **TypeScript strict** — no `any`, no `as unknown as X`
- **Component files** — one component per file, PascalCase filename
- **Hooks** — `use` prefix, in `lib/hooks/`, return typed objects not arrays (for >2 values)
- **API calls** — always go through `lib/api/` wrappers, never `fetch()` directly in components
- **Tailwind** — utility classes only; no inline styles; no CSS modules (Tailwind config is the design system)
- **pnpm only** — `pnpm add <package>`, never `npm install`

```tsx
// Good — typed props, hook for data, Tailwind styling
interface AgentCardProps {
  agent: AgentDetail;
  isActive: boolean;
}

export function AgentCard({ agent, isActive }: AgentCardProps) {
  return (
    <div className={cn("rounded-lg border p-4", isActive && "border-amber-500")}>
      {/* ... */}
    </div>
  );
}
```

### Git commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(baton): add priority-weighted queue ordering
fix(causal): prevent duplicate edge creation on replay
docs(api): add missing /metrics/sc endpoint
test(energy): cover depletion + auto-allocate edge cases
refactor(world): extract invariant check into engine module
```

- **One logical change per commit** — small, reviewable, revertable
- **Imperative mood** in subject — "add X", not "added X"
- **Explain why, not what** — the diff shows what; the message explains why
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` on AI-assisted commits

---

## Making Changes

### For bug fixes

1. Write a failing test that reproduces the bug
2. Fix the root cause (not the symptom)
3. Verify the test now passes
4. Run `make check` — all 70 tests must pass

### For new features

1. Check [docs/PRD.md](docs/PRD.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the design intent
2. Open an issue or discussion first for anything non-trivial
3. Write the implementation
4. Add tests (unit + integration as appropriate)
5. Update relevant docs if the API or data model changed
6. Run `make check` and `make e2e`

### For UI changes

After any visual change:
1. Run `make e2e` — Playwright will capture screenshots to `assets/ui/`
2. Verify the screenshots look correct (no regressions)
3. Commit the updated screenshots with your PR

The visual spec is [docs/UX_SPEC.md](docs/UX_SPEC.md) — all UI work must align with it.

---

## Pull Request Process

1. **Fork** the repo and create a branch: `feat/my-feature` or `fix/the-bug`
2. Make your changes following the conventions above
3. Run `make check` — must pass clean
4. Open a PR with:
   - A clear title (Conventional Commit format)
   - What the change does and why
   - How to test it manually
   - Screenshots/video for UI changes
5. Address review feedback — we aim to review within 48 hours

**PR checklist:**
- [ ] `make check` passes (lint + types + 70 tests)
- [ ] New logic has test coverage
- [ ] No new `any` types in TypeScript
- [ ] No new untyped Python functions
- [ ] Docs updated if API/schema changed
- [ ] Screenshots committed if UI changed

---

## What We Welcome

- **Bug fixes** — especially edge cases in baton arbitration and invariant enforcement
- **New entity type examples** — additional `schema_pack.py` presets (e.g., code review mission, research mission)
- **MCP client libraries** — thin wrappers for other agent frameworks
- **Frontend polish** — animations, accessibility, keyboard navigation improvements
- **Performance** — timeline virtualization, graph layout throttling
- **Documentation** — typos, clarifications, better examples
- **Tests** — more coverage for services, especially causal invalidation cascade

---

## What to Avoid

- **Scope creep** — Baton Studio is intentionally local-first and single-machine for MVP. Don't add distributed consensus, cloud sync, or persistent auth.
- **Breaking the event log** — the append-only `events` table is sacred. Never add update/delete operations to it.
- **Bypassing the service layer** — API routes must not contain business logic. All logic lives in `services/`.
- **Silent invariant downgrades** — if you change invariant behavior, it must be an explicit, documented decision.
- **Framework churn** — the tech stack is intentional. Don't swap libraries without a strong reason and discussion.

---

## Questions?

- Open a [GitHub Discussion](../../discussions) for design questions
- Open a [GitHub Issue](../../issues) for bugs or concrete feature requests
- Read [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common dev environment issues

---

*Baton Studio — substrate-native coordination for multi-agent teams.*
