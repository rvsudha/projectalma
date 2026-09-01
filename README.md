# ProjectAlma — Lead Management

A public lead-intake form, an auth-guarded internal **attorney dashboard**, and a
read-only **applicant portal** for prospects to track their own case.

- **Backend:** FastAPI (async) · SQLAlchemy 2 (asyncpg) · Alembic · PostgreSQL ·
  Resend · JWT auth · in-process rate limiting · structured logging · audit trail
- **Frontend:** Next.js 14 (App Router, TS) · CSS-Module design system ·
  react-hook-form + zod · server actions · route-handler API proxy (token stays server-side)
- **Infra:** Docker Compose (db + api + web), pluggable resume storage (local / S3)

Design documentation:

- [`docs/design-document_alma.pdf`](docs/design-document_alma.pdf) — system
  design: architecture, data model, API, security, deployment.
- [`docs/design-decisions_alma.pdf`](docs/design-decisions_alma.pdf) — the design
  decisions and their trade-offs.

---

## Features

| Capability | Where |
| --- | --- |
| Public lead form: first/last name, email, resume upload — **no account needed** | `/` (Next) → `POST /api/v1/leads` |
| Upload hardening: allow-list + magic-byte sniff + size cap + filename sanitize | `app/services/storage.py`, `routes/leads.py` |
| Confirmation email to prospect **and** notification to an attorney | `app/services/email.py` (background task) |
| Role-aware sign-up (`/signup`): **applicant** (open) or **attorney** (invite code) | `POST /api/v1/auth/register` |
| **Attorney dashboard** — status tiles, every field, current-milestone column, search / filter / pagination, sortable columns, recent-activity feed | `/leads` → `GET /api/v1/leads`, `/leads/stats`, `/leads/activity` |
| Lead state machine `PENDING ↔ REACHED_OUT` — attorney marks it (or reopens a mis-click) via a confirm dialog; every move is logged | `PATCH /api/v1/leads/{id}` |
| **Applicant portal** — read-only view of your own case(s): status, milestone, resume, progress timeline (ownership matched by email) | `/my` → `GET /api/v1/my/leads` |
| Per-case activity timeline, backed by an append-only audit trail | `lead_events` table, `GET /api/v1/leads/{id}/events` |
| Public landing page + accessible lead form (drag-drop upload, client + server validation) | `/` |
| Consistent error envelope + `X-Request-ID` correlation on every response | `app/core/errors.py`, `app/api/middleware.py` |
| Rate limiting on public submit + login | `app/core/ratelimit.py` |
| Liveness / readiness probes | `GET /api/v1/health`, `GET /api/v1/ready` |

---

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env      # optional: add RESEND_API_KEY to really send email
docker compose up --build
```

- Web app: <http://localhost:3000>
- API docs (Swagger): <http://localhost:8000/docs>  (disabled when `ENVIRONMENT=production`)
- The backend container waits for Postgres, runs migrations, and seeds the attorney on start.

**Seed demo data:** `docker compose exec backend python -m scripts.seed --demo`
(demo leads + a demo applicant login).

**Demo logins** at <http://localhost:3000/login>:

| Role | Email | Password | Lands on |
| --- | --- | --- | --- |
| Attorney | `attorney@projectalma.com` | `changeme123` | `/leads` (internal dashboard) |
| Applicant | `applicant@example.com` | `changeme123` | `/my` (their own case) |

Or **sign up** at <http://localhost:3000/signup> — pick a role: applicants
register openly; attorneys need the invite code `welcome`
(`ATTORNEY_SIGNUP_CODE` — rotate or disable in production). Submitting the public
form never requires an account.

Without `RESEND_API_KEY`, emails are **printed to the backend logs**
(`docker compose logs -f backend`) — the full flow works offline.

---

## Local development (no Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
cp .env.example .env
# .env ships with DATABASE_URL=sqlite+aiosqlite:///./var/dev.db for a zero-infra run;
# switch to postgresql+asyncpg://… when you have Postgres.

alembic upgrade head
python -m scripts.seed --demo
uvicorn app.main:app --reload --port 8000
```

Quality gates (all run in CI):

```bash
make backend-check      # ruff + mypy + pytest (coverage gate 85%)
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local        # API_BASE_URL=http://localhost:8000/api/v1
npm run dev                        # http://localhost:3000

npm run lint && npm run typecheck && npm run build   # CI gates
```

See [`frontend/README.md`](frontend/README.md) for the component/route layout.

`make help` lists every wrapped command. `pre-commit install` wires the hooks in
`.pre-commit-config.yaml`.

---

## Configuration

Env vars per service — see `backend/.env.example` / `frontend/.env.example`.

| Variable | Service | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | backend | async DSN (`postgresql+asyncpg://…` or `sqlite+aiosqlite://…`) |
| `SECRET_KEY` | backend | JWT signing — **required in production** (boot fails on the default) |
| `RESEND_API_KEY` | backend | unset ⇒ emails log to console |
| `RATE_LIMIT_*` | backend | per-route fixed-window limits |
| `ATTORNEY_SIGNUP_ENABLED` / `ATTORNEY_SIGNUP_CODE` | backend | gate (or disable) attorney self-registration |
| `STORAGE_BACKEND` | backend | `local` or `s3` |
| `ATTORNEY_NOTIFICATION_EMAIL` | backend | recipient of new-lead notices |
| `API_BASE_URL` | frontend | server-side only |
| `COOKIE_SECURE` | frontend | `1` behind HTTPS |

In `ENVIRONMENT=production` the backend refuses to start with an insecure
`SECRET_KEY`/seed password or `DEBUG=true`.

---

## Project layout

```
backend/    FastAPI service — core/ db/ models/ schemas/ services/ api/ ; Alembic ; pytest
frontend/   Next.js App Router — public form, login, guarded dashboard + audit timeline
docs/       design-document_alma.pdf · design-decisions_alma.pdf
.claude/    Claude Code skills used to build & maintain this repo
.github/    CI (backend + frontend + docker build)
```

---

## Claude Code skills

`.claude/skills/` — see [`.claude/skills/README.md`](.claude/skills/README.md):

| Skill | Purpose |
| --- | --- |
| `lead-agent` | Scaffold / extend the end-to-end lead app |
| `system-design` | Maintain the design docs in `docs/` |
| `email-integration` | Transactional email (Resend + console fallback) |
| `git` | Repo conventions: branches, commits, PRs, README upkeep |
