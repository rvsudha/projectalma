from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-" + "x" * 40)
os.environ.setdefault("RESEND_API_KEY", "")
os.environ.setdefault("SEED_ATTORNEY_EMAIL", "attorney@projectalma.com")
os.environ.setdefault("SEED_ATTORNEY_PASSWORD", "test-password-123")

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.ratelimit import reset_rate_limiter
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import create_app
from app.services import email as email_module
from app.services import storage as storage_module
from app.services.email import EmailProvider
from app.services.users import ensure_seed_attorney

# A valid PDF header so the magic-byte sniffer accepts it.
SAMPLE_PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\ntest resume\n%%EOF"
SAMPLE_DOCX = b"PK\x03\x04" + b"\x00" * 60


class RecordingEmailProvider(EmailProvider):
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send(self, *, to: str, subject: str, html: str, text: str) -> None:
        self.sent.append({"to": to, "subject": subject, "html": html, "text": text})


@pytest.fixture(autouse=True)
async def _schema() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        await ensure_seed_attorney(db)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def _isolation(tmp_path) -> Iterator[None]:
    settings.storage_local_dir = str(tmp_path / "resumes")
    storage_module.reset_storage_cache()
    email_module.reset_email_cache()
    reset_rate_limiter()
    yield
    storage_module.reset_storage_cache()
    email_module.reset_email_cache()
    reset_rate_limiter()


@pytest.fixture
def emails() -> RecordingEmailProvider:
    provider = RecordingEmailProvider()
    email_module._provider = provider
    return provider


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    resp = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        json={
            "email": settings.seed_attorney_email,
            "password": settings.seed_attorney_password,
        },
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def create_lead(
    client: AsyncClient,
    *,
    first_name: str = "Ada",
    last_name: str = "Lovelace",
    email: str = "ada@example.com",
    file: tuple[str, bytes, str] = ("cv.pdf", SAMPLE_PDF, "application/pdf"),
) -> dict:
    resp = await client.post(
        f"{settings.api_v1_prefix}/leads",
        data={"first_name": first_name, "last_name": last_name, "email": email},
        files={"resume": file},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
