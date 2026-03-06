SHELL := /bin/bash

.PHONY: dev backend frontend check test e2e demo clean

dev:
	@echo "Starting backend + frontend..."
	$(MAKE) -j2 backend frontend

backend:
	cd backend && python -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -e .[dev] && uvicorn baton_substrate.api.main:app --reload --port 8787

frontend:
	cd frontend && npm install && npm run dev

check:
	cd backend && source .venv/bin/activate && ruff check . && ruff format --check . && mypy baton_substrate && pytest -q
	cd frontend && npm run lint && npm run typecheck

test:
	cd backend && source .venv/bin/activate && pytest -q

e2e:
	cd frontend && npm run e2e

demo:
	cd backend && source .venv/bin/activate && python -m baton_substrate.scripts.run_demo --out ../dist
	cd frontend && npm run build

clean:
	rm -rf backend/.venv backend/*.sqlite frontend/node_modules frontend/.next dist
