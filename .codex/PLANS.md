# Baton Studio Frontier System ExecPlan

## Purpose / Big Picture

Turn Baton Studio from a local prototype into a production-quality agent coordination product. The system should remain local-first and demo-friendly, while adding the backend correctness, contract stability, MCP reliability, frontend craft, and verification needed for a product people would trust and pay for.

## Progress

- [x] Review approved frontier plan and existing repo state
- [x] Establish product/design context for Impeccable and Taste-guided UI work
- [x] Upgrade frontend dependency/security baseline
- [x] Harden backend contracts, persistence, auth mode, and correctness
- [x] Expand MCP contract tests and structured error handling
- [x] Rewrite frontend control room experience
- [x] Expand regression, visual, and security verification
- [x] Update docs and final release notes

## Surprises & Discoveries

- The repository is currently on `main`; the user explicitly requested implementation of the broad plan, so this is treated as approval to proceed.
- Existing `.codex/` notes are untracked and describe a completed release-hardening pass, not the current product-expansion pass.
- Previous audit found the curated backend gates green, but full `uv run mypy baton_substrate` fails because SQLAlchemy models are still untyped classical `Column` declarations.
- Previous audit found `pnpm audit --audit-level moderate` reports critical/high Next.js and Playwright issues, so dependency baseline must happen before serious frontend work.
- Playwright had to run the app on port 3100 during verification because unrelated local processes were already using port 3000.
- Demo energy allocation originally displayed balances above the mission budget; auto-allocation now rebalances accounts across the mission budget.

## Decision Log

- Preserve local-first demo mode with no auth friction; require auth only when `BATON_ENV=production`.
- Treat the UI as a product surface for builders/operators first, with enough narrative polish for demos and OSS evaluation.
- Use Impeccable/Taste guidance as constraints for craft, but avoid decorative landing-page patterns inside the operational app.
- Prefer backend compatibility for current documented routes, with additive hardening and contract cleanup.
- Keep `/demo/start`, `POST /missions/{mission_id}/export`, `POST /missions/import`, and `WS /ws/{mission_id}` as official product contracts.
- Make `make check` run full backend mypy and frontend dependency audit so regressions cannot hide behind the previous partial gate.

## Outcomes & Retrospective

Implemented the frontier pass across backend, MCP, and frontend. The backend now has typed SQLAlchemy models, migration scaffolding, production-mode auth/CORS, stable event cursors, safer mission packs, atomic baton flows, mission existence checks, energy validation, request IDs, and expanded regression coverage. The MCP server now forwards auth and returns structured errors. The frontend now has a redesigned control-room shell, mission-scoped routing/persistence, upgraded dependencies, graph lenses/search, timeline replay controls, polished export/import, mobile layouts, and Playwright regression coverage.

Final gates passed: `make check` with backend 85 tests and MCP 8 tests, `make audit` across backend/frontend/MCP, Alembic upgrade on fresh SQLite, `make demo`, frontend production build, Docker builds, and `make e2e` with 21/21 Playwright tests.
