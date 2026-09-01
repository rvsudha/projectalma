---
name: email-integration
description: >-
  Add or change transactional email in the ProjectAlma lead app — the applicant
  confirmation and the internal attorney notification sent on lead submission,
  the Resend provider, the console fallback, message templates, or a new
  triggered email. Use when the task mentions email, notifications, Resend, SMTP,
  "notify the attorney", "send a confirmation", or changing an email template.
---

# email-integration

Email lives in two files:

- `backend/app/services/email.py` — the `EmailProvider` ABC, `ResendEmailProvider`,
  `ConsoleEmailProvider`, the selector `get_email_provider()`, the `Recipient`
  value object, and the high-level `send_new_lead_emails(*, prospect, lead_id)`.
- `backend/app/templates/email/messages.py` — pure functions returning
  `RenderedEmail(subject, html, text)`. No I/O, no side effects.

Providers are **sync** (a `BackgroundTask` sync callable runs in the threadpool).
Pass plain data / a detached `Recipient` to the background task — never an ORM
object bound to the request's async session.

## Hard rules

1. **Never block or fail the request path.** All sending is dispatched from
   FastAPI `BackgroundTasks` (see `routes/leads.py`). Provider `.send()` catches
   its own exceptions and logs them — it must not raise.
2. **Offline-first.** When `RESEND_API_KEY` is unset, `ConsoleEmailProvider`
   logs the message. Tests and `docker compose up` (no key) must exercise the
   full flow with no network. Keep this working.
3. **Always send both `html` and `text`.** Build both in the template function.
4. **No PII in logs** beyond recipient + subject + a short preview.
5. New config → field on `Settings` + line in `backend/.env.example`.

## Add a new triggered email

1. Add a builder to `templates/email/messages.py`:
   ```python
   def lead_reached_out_confirmation(*, first_name: str) -> RenderedEmail: ...
   ```
   Reuse `_html(body)` for the wrapper. Add a unit test in
   `tests/` asserting subject + that key text appears in both bodies.
2. Add a high-level function in `services/email.py` (or extend
   `send_new_lead_emails`) that calls `get_email_provider().send(...)`.
3. Trigger it from the relevant service/route via `background_tasks.add_task(...)`.
   Pass plain data or a detached ORM object — the background task runs after the
   response, outside the request's DB session.
4. If you assert on it in tests, use the `emails` fixture
   (`RecordingEmailProvider`) from `tests/conftest.py`.

## Swap / add a provider (e.g. SES, SMTP)

1. Implement `EmailProvider` in `services/email.py`.
2. Extend the selector in `get_email_provider()` (keyed off a `Settings` value
   like `EMAIL_PROVIDER`), keeping `ConsoleEmailProvider` as the no-config
   fallback.
3. Add credentials to `Settings` + `.env.example`, guarded (only read when that
   provider is selected).
4. Add the dependency to `requirements.txt` / `pyproject.toml`.

## Verify

```bash
cd backend && pytest -q -k email && ruff check .
# Manual: docker compose up, submit a lead, then:
docker compose logs backend | grep "email"
```
