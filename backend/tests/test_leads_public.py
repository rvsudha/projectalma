from __future__ import annotations

import pytest

from app.core.config import settings
from tests.conftest import SAMPLE_DOCX, SAMPLE_PDF, create_lead

BASE = settings.api_v1_prefix


async def test_submit_creates_pending_lead_and_sends_two_emails(client, emails):
    body = await create_lead(client, email="ada@example.com")
    assert body["state"] == "PENDING"
    assert body["id"]

    recipients = {e["to"] for e in emails.sent}
    assert "ada@example.com" in recipients
    assert settings.attorney_notification_email in recipients
    assert len(emails.sent) == 2


async def test_submit_accepts_docx(client):
    resp = await client.post(
        f"{BASE}/leads",
        data={"first_name": "Ada", "last_name": "L", "email": "a@example.com"},
        files={
            "resume": (
                "cv.docx",
                SAMPLE_DOCX,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert resp.status_code == 201


async def test_submit_rejects_declared_type_not_in_allowlist(client, emails):
    resp = await client.post(
        f"{BASE}/leads",
        data={"first_name": "Ada", "last_name": "L", "email": "a@example.com"},
        files={"resume": ("cv.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "unsupported_media_type"
    assert emails.sent == []


async def test_submit_rejects_content_type_spoofing(client):
    """Declared application/pdf but the bytes are not a PDF."""
    resp = await client.post(
        f"{BASE}/leads",
        data={"first_name": "Ada", "last_name": "L", "email": "a@example.com"},
        files={"resume": ("cv.pdf", b"this is not a pdf", "application/pdf")},
    )
    assert resp.status_code == 415


async def test_submit_rejects_empty_file(client):
    resp = await client.post(
        f"{BASE}/leads",
        data={"first_name": "Ada", "last_name": "L", "email": "a@example.com"},
        files={"resume": ("cv.pdf", b"", "application/pdf")},
    )
    assert resp.status_code == 422


async def test_submit_rejects_oversized_file(client, monkeypatch):
    monkeypatch.setattr(settings, "max_resume_bytes", 10)
    resp = await client.post(
        f"{BASE}/leads",
        data={"first_name": "Ada", "last_name": "L", "email": "a@example.com"},
        files={"resume": ("cv.pdf", SAMPLE_PDF, "application/pdf")},
    )
    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "payload_too_large"


@pytest.mark.parametrize(
    "field,value",
    [("email", "not-an-email"), ("first_name", ""), ("last_name", "   ")],
)
async def test_submit_validates_fields(client, field, value):
    data = {"first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com"}
    data[field] = value
    resp = await client.post(
        f"{BASE}/leads",
        data=data,
        files={"resume": ("cv.pdf", SAMPLE_PDF, "application/pdf")},
    )
    assert resp.status_code == 422


async def test_submit_missing_resume_is_422(client):
    resp = await client.post(
        f"{BASE}/leads",
        data={"first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com"},
    )
    assert resp.status_code == 422


async def test_rate_limit_kicks_in(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_lead_create_per_hour", 2)
    from app.core.ratelimit import reset_rate_limiter

    reset_rate_limiter()

    ok1 = await client.post(
        f"{BASE}/leads",
        data={"first_name": "A", "last_name": "B", "email": "a@example.com"},
        files={"resume": ("cv.pdf", SAMPLE_PDF, "application/pdf")},
    )
    ok2 = await client.post(
        f"{BASE}/leads",
        data={"first_name": "A", "last_name": "B", "email": "b@example.com"},
        files={"resume": ("cv.pdf", SAMPLE_PDF, "application/pdf")},
    )
    blocked = await client.post(
        f"{BASE}/leads",
        data={"first_name": "A", "last_name": "B", "email": "c@example.com"},
        files={"resume": ("cv.pdf", SAMPLE_PDF, "application/pdf")},
    )
    assert ok1.status_code == 201
    assert ok2.status_code == 201
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


async def test_response_has_request_id_and_security_headers(client):
    resp = await client.get(f"{BASE}/health")
    assert resp.headers.get("X-Request-ID")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
