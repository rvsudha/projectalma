---
name: lead-agent
description: >-
  Build or extend the ProjectAlma lead-management application end-to-end — the public
  lead form, the async FastAPI lead APIs, the auth-guarded internal review UI,
  applicant + attorney email notifications, resume storage, the audit trail, and
  the PENDING→REACHED_OUT state machine. Use when the task is "create the lead
  app", "add a field to the lead form", "add a lead endpoint", "change the lead
  lifecycle", or any change spanning the API, the Next.js UI, email, and storage.
---

# lead-agent

Production-shaped lead app: **async FastAPI + Next.js + Postgres + Resend**,
structured as `backend/` and `frontend/`.

## The domain (do not drift)

A **lead** is a publicly submitted form: `first_name`, `last_name`, `email`,
`resume` (PDF/DOC/DOCX).

1. Submit → create lead `PENDING`, store resume, write a `CREATED` audit event,
   send **two** emails (applicant confirmation + internal attorney notice).
2. Auth-guarded internal UI lists every lead + all fields; shows the audit trail.
3. `PENDING → REACHED_OUT` only when an attorney marks it manually.
   `REACHED_OUT` is terminal (reverse → HTTP 409). Each transition writes a
   `STATE_CHANGED` event in the same transaction.

## Architecture rules

- **Layering:** `app/api/routes/*` (thin async HTTP) → `app/services/*` (all
  business logic, async, **no FastAPI imports**) → `app/models/*` (async
  SQLAlchemy). Contracts in `app/schemas/*`.
- **Async all the way:** `async def` handlers and services; `AsyncSession`;
  `await db.execute/scalar/get`. Never call blocking IO in the request path —
  wrap third-party sync SDKs with `anyio.to_thread.run_sync` (see
  `S3StorageBackend`).
- **Errors:** raise typed exceptions from `app/core/errors.py`
  (`NotFoundError`, `ConflictError`, `ValidationAppError`, …) in services. The
  handlers in `install_exception_handlers` render the single envelope
  `{"error": {code, message, details, request_id}}`. Never return ad-hoc dicts.
- **Browser only talks to its own origin.** Next route handlers
  (`frontend/src/app/api/**`) proxy to FastAPI. Attorney JWT in an `httpOnly`
  cookie via `/api/auth/login`; server components read it (`lib/session.ts`) and
  call the API through `lib/api.ts`.
- **State transitions are data-driven** in `services/leads.py::_TRANSITIONS`.
- **Config:** add a field to `core/config.py::Settings` + a line in
  `backend/.env.example`. Never read `os.environ` elsewhere. Keep the
  `_guard_production` validator honest.
- **Email + storage + rate limiter are behind ABCs** with offline-friendly
  defaults (console email, local disk, in-memory limiter). Keep the app runnable
  with zero external services.
- **Audit trail:** any state-affecting change appends a `LeadEvent` via
  `_record_event(db, lead, …)` (uses `lead_id`, never the lazy `lead.events`
  collection) in the same transaction.

## Workflow for a change

1. Non-trivial? Run **`system-design`** and update the design docs in `docs/`
   first (system design + design decisions).
2. **Backend:** model → migration (`alembic revision -m "…"` or hand-write in
   `alembic/versions/` matching `0001_initial`) → schema → async service fn
   (+ unit test) → async route (+ API test).
3. **Frontend:** `lib/types.ts` → `lib/api.ts` (server-only, `cache()`-wrapped)
   → server component / page → `"use client"` island for interactivity →
   route-handler proxy in `app/api/**` if the browser needs a new path. Forms:
   react-hook-form + zod, schemas in `lib/validation.ts` mirroring the API rules.
   Dashboard filters/search/pagination go through the URL, not client state.
   Reuse `components/ui/*` primitives; new styling is a CSS Module + the tokens
   in `app/globals.css` (no CSS framework).
4. **Email changes:** use **`email-integration`**.
5. Verify:
   ```bash
   make backend-check                               # ruff + mypy + pytest (85% gate)
   cd frontend && npm run lint && npm run typecheck
   ```
6. Update `README.md` if the surface moved; commit via **`git`**.

## Building from scratch

Scaffold in this order, keeping each step runnable:

1. `pyproject.toml` + `requirements*.txt`; `app/core/{config,logging,security,errors,ratelimit,context}.py`
2. `app/db/{base,session}.py` (async engine); `app/models/*`; `alembic/` + `0001_initial`
3. `app/schemas/*`; `app/services/{storage,email,users,leads}.py`; `templates/email/`
4. `app/api/{deps,middleware,routes/*}.py`; `app/main.py` (factory + lifespan + handlers);
   `scripts/{seed.py,entrypoint.sh}`
5. `tests/` — async fixtures (`httpx.AsyncClient`, in-memory aiosqlite); cover
   submission (happy + validation + spoof + size + rate limit), auth, internal
   CRUD + search + pagination, state machine both ways, audit trail, units
6. `frontend/` — `/` form, `/login`, `/leads`, `/leads/[id]` (+ audit timeline),
   `middleware.ts`, `src/app/api/**` proxies, `src/lib/**`
7. `docker-compose.yml`, `Dockerfile`s (multi-stage, non-root, healthcheck,
   gunicorn+uvicorn workers), `Makefile`, `.pre-commit-config.yaml`, CI,
   `README.md`, `docs/` design docs

## Acceptance checklist

- [ ] `POST /api/v1/leads` — multipart, validates 4 fields + resume
      (allow-list **and** magic-byte sniff) + size cap; `201 {id, state:"PENDING"}`;
      rate-limited.
- [ ] Exactly two emails per submission via `BackgroundTasks`; failures logged,
      never surfaced.
- [ ] `CREATED` event on submit; `STATE_CHANGED` event on transition, same txn.
- [ ] `GET /leads*`, `PATCH`, `/events`, `/resume` require a valid attorney JWT.
- [ ] `PATCH` enforces the state machine; illegal → 409 with the error envelope.
- [ ] Every response has `X-Request-ID`; every error uses the envelope.
- [ ] Internal UI renders all fields, working resume link, and the audit trail.
- [ ] `make backend-check` green; frontend `lint` + `typecheck` green.
