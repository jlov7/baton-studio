SHELL := /bin/bash

.PHONY: dev backend frontend check test e2e demo clean

dev:
	@echo "Starting backend + frontend..."
	$(MAKE) -j2 backend frontend

backend:
	cd backend && uv sync --dev && uv run uvicorn baton_substrate.api.main:app --reload --port 8787

frontend:
	cd frontend && pnpm install && pnpm dev

check:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy baton_substrate && uv run pytest -q
	cd frontend && pnpm lint && pnpm typecheck

test:
	cd backend && uv run pytest -q

e2e:
	cd frontend && pnpm e2e

demo:
	cd backend && uv run python -m baton_substrate.scripts.run_demo --out ../dist
	cd frontend && pnpm build

clean:
	rm -rf backend/.venv backend/*.sqlite frontend/node_modules frontend/.next dist
