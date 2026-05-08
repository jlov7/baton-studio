# Quality Burn-Down

This is the public hardening record for the frontier pass. It is intentionally concrete: every implementation item below has shipped and is covered by the current gates.

## Completed

- [x] Rebuild the control-room frontend around Mission, World, Graph, Timeline, and Export workflows.
- [x] Add product and design source-of-truth docs.
- [x] Upgrade vulnerable frontend dependencies and make `pnpm audit --audit-level moderate` pass.
- [x] Convert backend SQLAlchemy models to typed 2.0 ORM style.
- [x] Add Alembic migration support.
- [x] Add foreign keys, indexes, uniqueness constraints, and delete provenance.
- [x] Normalize official public contracts: `/demo/start`, `POST /missions/{mission_id}/export`, `POST /missions/import`, `WS /ws/{mission_id}`.
- [x] Add mission existence validation on child routes.
- [x] Add production mode with bearer auth.
- [x] Add scoped production tokens for `reader`, `operator`, and `admin` roles.
- [x] Replace wildcard CORS with configured origins.
- [x] Add defensive security headers.
- [x] Add request IDs and structured request logging.
- [x] Add `/ready` for deploy health checks.
- [x] Add Prometheus-style `/metrics`.
- [x] Harden mission pack import against malformed zip files, oversized uncompressed payloads, duplicate IDs, invalid nested shapes, and unsupported schema versions.
- [x] Add event cursor ordering for same-timestamp events.
- [x] Enforce energy spend validation and commit energy gates.
- [x] Rebalance demo energy so balances do not exceed mission budget.
- [x] Add MCP auth forwarding and structured backend error handling.
- [x] Include MCP dependencies in vulnerability auditing.
- [x] Add Dockerfiles, Compose, `.env.example`, and Docker ignore files.
- [x] Add frontend stale-mission recovery after backend reset.
- [x] Add Playwright regressions for mission persistence, graph lenses, timeline replay, export, mobile overflow, and stale mission recovery.
- [x] Refresh public README, API, architecture, data model, and MCP docs.
- [x] Add public GitHub CI, dependency update configuration, issue templates, PR template, and security policy.

## Current Gates

- `make check`: backend lint/format/full mypy/tests, frontend audit/lint/typecheck, MCP tests
- `make audit`: backend, frontend, and MCP dependency vulnerability audit
- `pnpm --dir frontend build`: frontend production build
- fresh SQLite `alembic upgrade head`
- `make e2e`: browser E2E and screenshot refresh
- `make demo`: demo mission pack and production frontend build
- `docker compose config`
- `docker compose build`

## Future Scale Choices

These are deliberate future product choices, not missing local-first implementation work:

- Hosted multi-tenant identity provider integration.
- Managed Postgres/Redis topology for hosted deployments.
- Long-retention telemetry warehouse beyond the in-process `/metrics` endpoint.
