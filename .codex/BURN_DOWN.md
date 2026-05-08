# Baton Studio Elite Burn-Down

## Status

Active hardening pass started after the frontier implementation. Goal: remove remaining practical gaps across backend, frontend, MCP, verification, and release hygiene.

## Burn-Down

- [x] Include MCP dependencies in security audit gates.
- [x] Upgrade MCP dev dependencies covered by current Python advisories.
- [x] Reject zip mission packs whose uncompressed `mission_pack.json` exceeds upload limits.
- [x] Convert malformed nested mission-pack payloads into `400` responses instead of accidental `500` errors.
- [x] Add regression tests for malformed mission-pack nested objects.
- [x] Add security headers to API responses.
- [x] Log failed WebSocket broadcasts instead of silently discarding them.
- [x] Clear stale persisted frontend mission IDs when the backend no longer has that mission.
- [x] Add frontend regression coverage for stale mission recovery.
- [x] Add scoped production API keys for reader/operator/admin team mode.
- [x] Add readiness and Prometheus-style runtime metrics endpoints.
- [x] Add Docker and Compose production deployment scaffolding.
- [x] Rewrite README around product positioning, production mode, ops, MCP, and quality gates.
- [x] Re-run full `make check`, `make audit`, production build, and E2E.

## Final Verification

- `make check` passed: backend 85 tests, frontend audit/lint/typecheck, MCP 8 tests.
- `make audit` passed across backend, frontend, and MCP.
- Fresh SQLite `alembic upgrade head` passed.
- `pnpm build` passed.
- `make e2e` passed: 21/21 Playwright tests.
- `make demo` passed after mission-pack hardening.
- `docker compose config` and Docker builds passed.

## Watch List

These are future scale choices rather than implementation gaps in the current local-first scope:

- External identity provider integration if Baton Studio becomes a hosted multi-tenant service.
- Managed Postgres/Redis choice for hosted deployments.
- Long-running observability warehouse for request/event traces beyond the in-process `/metrics` endpoint.
