# <Project Name>

<One-sentence description.>

- **Backend:** FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · <email provider> · JWT auth
- **Frontend:** Next.js 14 (App Router, TypeScript)
- **Infra:** Docker Compose (<services>), pluggable resume storage (local disk / S3)

Design docs in [`docs/`](docs/) — system design, and the design decisions with
their trade-offs.

## Features

| Capability | Where |
| --- | --- |
| <capability> | <path / endpoint> |

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

- Web app: <http://localhost:3000>
- API docs: <http://localhost:8000/docs>

Seed demo data: `docker compose exec backend python -m scripts.seed --demo`

**Seeded login:** `<SEED_ATTORNEY_EMAIL>` / `<SEED_ATTORNEY_PASSWORD>`
(override via env).

## Local development

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
cp .env.example .env
alembic upgrade head && python -m scripts.seed --demo
uvicorn app.main:app --reload --port 8000
pytest -q
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

`make help` lists all wrapped commands.

## Configuration

Per-service env vars — see `backend/.env.example` and `frontend/.env.example`.
Fill in the key table here: `DATABASE_URL`, `SECRET_KEY`, `<EMAIL_KEY>`,
`STORAGE_BACKEND`, `API_BASE_URL`, `COOKIE_SECURE`.

## Project layout

```
backend/    routes → services → models, Alembic, pytest
frontend/   Next.js App Router: public form, login, guarded dashboard
docs/       design docs (system design · design decisions)
.claude/    Claude Code skills
```

## Claude Code skills

| Skill | Purpose |
| --- | --- |
| `lead-agent` | Build / extend the app end-to-end |
| `system-design` | Maintain the design docs in `docs/` |
| `email-integration` | Transactional email |
| `git` | Repo conventions + README upkeep |
