"""Unit tests for pure logic that doesn't need the HTTP stack."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.ratelimit import InMemoryRateLimiter
from app.services.storage import sanitize_filename, sniff_matches
from app.templates.email import messages


def test_sniff_matches_pdf():
    assert sniff_matches("application/pdf", b"%PDF-1.7 ...")
    assert not sniff_matches("application/pdf", b"GIF89a")
    assert not sniff_matches("image/png", b"\x89PNG")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("../../etc/passwd", "passwd"),
        ("/tmp/x/../y.pdf", "y.pdf"),
        ("my resume (final).pdf", "my_resume_final_.pdf"),
        ("", "resume"),
        ("...", "resume"),
    ],
)
def test_sanitize_filename(raw, expected):
    assert sanitize_filename(raw) == expected


def test_rate_limiter_window():
    limiter = InMemoryRateLimiter()
    assert limiter.check("k", limit=2, window_seconds=60).allowed
    assert limiter.check("k", limit=2, window_seconds=60).allowed
    blocked = limiter.check("k", limit=2, window_seconds=60)
    assert not blocked.allowed
    assert blocked.retry_after > 0
    # a different key is unaffected
    assert limiter.check("other", limit=2, window_seconds=60).allowed


def test_email_templates_have_html_and_text():
    m = messages.prospect_confirmation(first_name="Ada")
    assert "Ada" in m.html and "Ada" in m.text
    n = messages.attorney_notification(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        lead_id="abc",
        dashboard_url="http://x/leads/abc",
    )
    assert "Lovelace" in n.html and "ada@example.com" in n.text
    assert "http://x/leads/abc" in n.html


def test_production_config_rejects_insecure_secret():
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(
            _env_file=None,
            environment="production",
            debug=False,
            secret_key="dev-only-insecure-secret-change-me",
            seed_attorney_password="a-strong-unique-password",
        )


def test_production_config_rejects_debug_true():
    with pytest.raises(ValueError, match="DEBUG"):
        Settings(
            _env_file=None,
            environment="production",
            debug=True,
            secret_key="x" * 48,
            seed_attorney_password="a-strong-unique-password",
        )


def test_production_config_rejects_default_signup_code():
    with pytest.raises(ValueError, match="ATTORNEY_SIGNUP_CODE"):
        Settings(
            _env_file=None,
            environment="production",
            debug=False,
            secret_key="x" * 48,
            seed_attorney_password="a-strong-unique-password",
        )


def test_production_config_accepts_hardened_values():
    s = Settings(
        _env_file=None,
        environment="production",
        debug=False,
        secret_key="x" * 48,
        seed_attorney_password="a-strong-unique-password",
        attorney_signup_code="a-rotated-invite-code",
    )
    assert s.environment == "production"


def test_sync_database_url_derivation():
    s = Settings(_env_file=None, database_url="postgresql+asyncpg://u:p@h/db")
    assert s.sync_database_url == "postgresql+psycopg://u:p@h/db"
    s2 = Settings(_env_file=None, database_url="sqlite+aiosqlite:///./x.db")
    assert s2.sync_database_url == "sqlite+pysqlite:///./x.db"


def test_cors_origins_parsed_from_csv():
    s = Settings(_env_file=None, cors_origins="http://a.com, http://b.com")
    assert s.cors_origins == ["http://a.com", "http://b.com"]
