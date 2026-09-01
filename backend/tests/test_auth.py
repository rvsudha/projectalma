from __future__ import annotations

import jwt

from app.core.config import settings
from app.core.security import create_access_token

BASE = settings.api_v1_prefix


async def test_login_success(client):
    resp = await client.post(
        f"{BASE}/auth/login",
        json={"email": settings.seed_attorney_email, "password": settings.seed_attorney_password},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.access_token_expire_minutes * 60
    jwt.decode(
        body["access_token"],
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
    )


async def test_login_wrong_password(client):
    resp = await client.post(
        f"{BASE}/auth/login",
        json={"email": settings.seed_attorney_email, "password": "nope"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


async def test_login_unknown_user(client):
    resp = await client.post(
        f"{BASE}/auth/login",
        json={"email": "ghost@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_me_without_token(client):
    resp = await client.get(f"{BASE}/auth/me")
    assert resp.status_code == 401


async def test_me_with_token(client, auth_headers):
    resp = await client.get(f"{BASE}/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == settings.seed_attorney_email
    assert resp.json()["role"] == "attorney"


async def test_me_with_garbage_token(client):
    resp = await client.get(f"{BASE}/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401


async def test_me_rejects_wrong_issuer(client):
    bad = jwt.encode(
        {"sub": "x", "exp": 9999999999, "iat": 1, "iss": "evil"},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    resp = await client.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {bad}"})
    assert resp.status_code == 401


async def test_me_rejects_token_for_deleted_user(client):
    token = create_access_token("00000000-0000-0000-0000-000000000000")
    resp = await client.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_login_rate_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_login_per_15min", 1)
    from app.core.ratelimit import reset_rate_limiter

    reset_rate_limiter()
    await client.post(f"{BASE}/auth/login", json={"email": "a@a.com", "password": "x"})
    resp = await client.post(f"{BASE}/auth/login", json={"email": "a@a.com", "password": "x"})
    assert resp.status_code == 429


# --- registration ---

_ATTY = {
    "full_name": "New Attorney",
    "email": "new.attorney@projectalma.com",
    "password": "a-strong-passphrase",
    "role": "attorney",
    "invite_code": "welcome",
}
_APPLICANT = {
    "full_name": "New Applicant",
    "email": "new.applicant@example.com",
    "password": "a-strong-passphrase",
    "role": "applicant",
}


async def test_register_attorney_then_login(client):
    resp = await client.post(f"{BASE}/auth/register", json=_ATTY)
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "attorney"
    token = resp.json()["access_token"]

    me = await client.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == _ATTY["email"]
    assert me.json()["role"] == "attorney"

    login = await client.post(
        f"{BASE}/auth/login",
        json={"email": _ATTY["email"], "password": _ATTY["password"]},
    )
    assert login.status_code == 200
    assert login.json()["role"] == "attorney"


async def test_register_applicant_no_invite_code_needed(client):
    resp = await client.post(f"{BASE}/auth/register", json=_APPLICANT)
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "applicant"


async def test_register_attorney_wrong_invite_code(client):
    resp = await client.post(f"{BASE}/auth/register", json={**_ATTY, "invite_code": "nope"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "forbidden"


async def test_register_attorney_missing_invite_code(client):
    resp = await client.post(f"{BASE}/auth/register", json={**_ATTY, "invite_code": None})
    assert resp.status_code == 403


async def test_register_duplicate_email(client):
    resp = await client.post(
        f"{BASE}/auth/register",
        json={**_APPLICANT, "email": settings.seed_attorney_email},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


async def test_register_weak_password(client):
    resp = await client.post(f"{BASE}/auth/register", json={**_APPLICANT, "password": "short"})
    assert resp.status_code == 422


async def test_register_attorney_signup_disabled(client, monkeypatch):
    monkeypatch.setattr(settings, "attorney_signup_enabled", False)
    resp = await client.post(f"{BASE}/auth/register", json=_ATTY)
    assert resp.status_code == 403
    # applicants can still register
    resp = await client.post(f"{BASE}/auth/register", json=_APPLICANT)
    assert resp.status_code == 201


async def test_register_rate_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_signup_per_hour", 1)
    from app.core.ratelimit import reset_rate_limiter

    reset_rate_limiter()
    await client.post(f"{BASE}/auth/register", json={**_APPLICANT, "email": "a@example.com"})
    resp = await client.post(f"{BASE}/auth/register", json={**_APPLICANT, "email": "b@example.com"})
    assert resp.status_code == 429
