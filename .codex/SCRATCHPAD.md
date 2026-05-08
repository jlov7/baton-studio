## Current Task

Implement the Baton Studio Frontier System Plan: production backend hardening, MCP contract reliability, and a world-class control-room frontend rewrite.

## Status

Implemented and verified.

## Plan

1. [x] Replace release-hardening notes with the active frontier-system ExecPlan
2. [x] Add PRODUCT.md and DESIGN.md context for Impeccable/Taste-guided UI work
3. [x] Upgrade frontend dependencies and resolve audit findings
4. [x] Harden backend persistence, auth mode, events, export/import, and correctness
5. [x] Expand MCP contract tests and error handling
6. [x] Rebuild frontend app shell and primary screens
7. [x] Expand verification gates and docs

## Decisions Made

- Treat the user's implementation request as approval for the broad multi-file checkpoint.
- Keep demo mode frictionless, but add explicit production mode protections.
- Do backend contract fixes before the UI rewrite so the UI can rely on stable semantics.
- Use port 3100 for deterministic frontend E2E/manual verification when port 3000 is occupied.
- Keep local demo mode unauthenticated; require bearer auth only under `BATON_ENV=production`.

## Verification

- `make check` passed with backend 85 tests and MCP 8 tests.
- `make audit` passed across backend, frontend, and MCP.
- Alembic upgrade against a fresh SQLite database passed.
- `make demo` passed after mission-pack hardening.
- Frontend `pnpm lint && pnpm typecheck && pnpm build` passed after final UI polish.
- `make e2e` passed with 21/21 Playwright tests.
- `docker compose config` and Docker builds passed.

## Open Questions

- None blocking. Scope is intentionally broad and approved.
