SHELL := /bin/bash

.PHONY: dev backend frontend check audit test e2e demo clean

dev:
	@echo "Starting backend + frontend..."
	$(MAKE) -j2 backend frontend

backend:
	cd backend && uv sync --dev && uv run uvicorn baton_substrate.api.main:app --reload --port 8787

frontend:
	cd frontend && pnpm install --frozen-lockfile && pnpm dev

check:
	cd backend && uv sync --extra dev && uv run ruff check . && uv run ruff format --check . && uv run mypy baton_substrate && uv run pytest -q
	cd frontend && pnpm install --frozen-lockfile && pnpm audit --audit-level moderate && pnpm lint && pnpm typecheck
	cd mcp_server && uv sync --extra dev && uv run pytest -q

audit:
	cd backend && uv sync --extra dev && bash -lc 'uv run --with pip-audit pip-audit --strict --disable-pip --no-deps -r <(uv export --extra dev --no-hashes --no-emit-project --format requirements.txt)'
	cd frontend && pnpm install --frozen-lockfile && pnpm audit --audit-level moderate
	cd mcp_server && uv sync --extra dev && bash -lc 'uv run --with pip-audit pip-audit --strict --disable-pip --no-deps -r <(uv export --extra dev --no-hashes --no-emit-project --format requirements.txt)'

test:
	cd backend && uv sync --extra dev && uv run pytest -q

e2e:
	cd frontend && pnpm install --frozen-lockfile && pnpm exec playwright install chromium && pnpm e2e

demo:
	cd backend && uv sync --extra dev && uv run python -m baton_substrate.scripts.run_demo --out ../dist
	cd frontend && pnpm install --frozen-lockfile && pnpm build

clean:
	rm -rf backend/.venv backend/*.sqlite frontend/node_modules frontend/.next dist
