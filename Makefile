.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help up down logs seed migrate migrate-down \
        backend-install backend-test backend-lint backend-typecheck backend-check backend-run \
        frontend-install frontend-run frontend-build fmt

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

## ---- Docker (full stack) ----
up: ## Build & start db + backend + frontend
	docker compose up --build

down: ## Stop and remove containers
	docker compose down

logs: ## Tail all service logs
	docker compose logs -f

seed: ## Seed attorney + demo leads inside the backend container
	docker compose exec backend python -m scripts.seed --demo

## ---- Backend (host) ----
backend-install: ## Install backend dev dependencies
	cd backend && pip install -r requirements-dev.txt && pip install -e .

migrate: ## Apply DB migrations
	cd backend && alembic upgrade head

migrate-down: ## Roll back the last migration
	cd backend && alembic downgrade -1

backend-run: ## Run FastAPI with autoreload on :8000
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test: ## Run backend tests + coverage gate
	cd backend && ENVIRONMENT=test DATABASE_URL=sqlite+aiosqlite:///:memory: pytest -q

backend-lint: ## Lint & format-check
	cd backend && ruff check . && ruff format --check .

backend-typecheck: ## Static type-check
	cd backend && mypy app

backend-check: backend-lint backend-typecheck backend-test ## All backend gates

fmt: ## Auto-format & fix backend
	cd backend && ruff check --fix . && ruff format .

## ---- Frontend (host) ----
frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-run: ## Run Next.js dev server on :3000
	cd frontend && npm run dev

frontend-build: ## Production build of the frontend
	cd frontend && npm run build
