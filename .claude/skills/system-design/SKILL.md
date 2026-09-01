---
name: system-design
description: >-
  Produce or update the ProjectAlma design docs — overview, goals, requirements,
  architecture diagram, component design, key flows, API surface, security,
  observability, design decisions with trade-offs, local-run instructions,
  deployment, and testing strategy. Use before implementing any non-trivial
  change, when the user asks for "a design doc", "an architecture doc", "how
  should this be structured", or when a doc has drifted from the code.
---

# system-design

The design documentation lives in **`docs/`** as two PDFs, the contract the
`lead-agent` skill builds against:

- `docs/design-document_alma.pdf` — system design (sections 1–9, 11–14 below).
- `docs/design-decisions_alma.pdf` — the design decisions and their trade-offs
  (section 10 below).

## How the docs are maintained

The PDFs are exported by the author from Markdown. The repo holds only the PDFs.

1. Draft or edit the content in Markdown (keep the working copy in the session
   scratchpad; if it is missing, reconstruct it by reading the current PDF text
   plus `backend/app` and `frontend/src`, then reconcile).
2. Hand the updated Markdown to the author to re-export, or convert it yourself
   (e.g. a Markdown→PDF/DOCX helper in the scratchpad) and replace the file in
   `docs/`.
3. Keep the two documents consistent: system design in one, decisions in the
   other, no overlap.

## When to run

- The user asks for a design / architecture document.
- Before a change that adds a table, an external dependency, an auth path, or a
  new bounded responsibility.
- After a change that made the current document wrong (fix it in the same PR).

## Required sections

1. **Overview** — the three surfaces, the lead lifecycle, the stack in one line.
2. **Goals and non-goals** — including what is deliberately out of scope.
3. **Requirements** — functional (actors table, anchored on
   `PENDING ↔ REACHED_OUT`) and non-functional.
4. **Architecture** — an ASCII diagram (prospect / attorney / applicant →
   Next.js BFF → async FastAPI → Postgres / object storage / email) and *why* the
   boundaries sit where they do.
5. **Component design** — frontend, backend layering (`routes → services →
   models`, services framework-free), data model (every column, type,
   nullability, index; Alembic; `lead_events` append-only and written in the same
   transaction), storage, email.
6. **Key flows** — lead submission (validation + sniff + bounded read), state
   transition (single writer, transition table, audit event), applicant portal
   (ownership by email).
7. **API reference** — one row per endpoint: method, path, auth, purpose. Then the
   error envelope.
8. **Security and authentication** — token type + claims, where stored, how
   verified, login rate limit + anti-enumeration, the role gate, the invite-code
   branch, the `_guard_production` boot check.
9. **Observability and operations** — structured JSON logs, request-id
   correlation, access log, liveness vs readiness, security headers.
10. **Design decisions and trade-offs** — the most important section. One
    subsection per non-obvious choice: alternatives considered → reasoning → cost
    accepted → revisit-if. Be honest about shortcuts. When a decision is
    reversed, rewrite its subsection and note the change.
11. **Future work and production hardening** — a table of current state → next
    step (email verification, token revocation, durable email, virus scanning,
    distributed rate limiting, …). Never imply an unbuilt thing exists.
12. **Running it locally** — Docker one-command path and the no-Docker path
    (backend venv + frontend npm, SQLite default), demo logins, where email goes
    without an API key, the check commands, the config table.
13. **Deployment** — compose behaviour (wait-for-db, migrate, seed,
    gunicorn+uvicorn) and a suggested prod topology.
14. **Testing strategy** — what the backend suite covers, the coverage floor, and
    the lint / type / migration / test gates.

## Style

- Prose that reads as a finished document — minimal cross-references, no
  ADR-tooling jargon. The two docs may point at each other by name but should not
  duplicate content.
- Decisions and rationale over description. Every diagram earns its place.
- If you recommend something not yet implemented, say so and put it in section 11
  — never imply it exists.
- Match reality: read `backend/app` and `frontend/src` before writing. If the doc
  and code disagree, the code wins.

## After updating

Replace the affected file(s) in `docs/`, mention in the PR description that the
design changed, and check whether `README.md`'s feature table or the `lead-agent`
acceptance checklist also needs an edit.
