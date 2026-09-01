"""Applicant portal — a prospect's read-only view of their own cases."""

from __future__ import annotations

from app.core.config import settings
from tests.conftest import create_lead

BASE = settings.api_v1_prefix


async def _applicant_headers(client, email="sam@example.com", password="a-strong-passphrase"):
    await client.post(
        f"{BASE}/auth/register",
        json={"full_name": "Sam Rivera", "email": email, "password": password, "role": "applicant"},
    )
    resp = await client.post(f"{BASE}/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}, email


async def test_my_leads_shows_only_own_submissions(client):
    await create_lead(client, first_name="Sam", last_name="Rivera", email="sam@example.com")
    await create_lead(client, first_name="Other", last_name="Person", email="other@example.com")

    headers, _ = await _applicant_headers(client)
    resp = await client.get(f"{BASE}/my/leads", headers=headers)
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) == 1
    assert cases[0]["email"] == "sam@example.com"
    assert cases[0]["state"] == "PENDING"
    assert cases[0]["milestone"] == "Awaiting attorney review"
    assert [e["type"] for e in cases[0]["events"]] == ["CREATED"]


async def test_my_leads_reflects_attorney_status_change(client, auth_headers):
    lead = await create_lead(client, email="sam@example.com")
    await client.patch(
        f"{BASE}/leads/{lead['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )

    headers, _ = await _applicant_headers(client)
    resp = await client.get(f"{BASE}/my/leads", headers=headers)
    case = resp.json()[0]
    assert case["state"] == "REACHED_OUT"
    assert case["milestone"] == "Attorney has reached out"
    assert [e["type"] for e in case["events"]] == ["CREATED", "STATE_CHANGED"]


async def test_my_leads_requires_auth(client):
    assert (await client.get(f"{BASE}/my/leads")).status_code == 401


async def test_applicant_cannot_access_internal_dashboard(client):
    headers, _ = await _applicant_headers(client)
    assert (await client.get(f"{BASE}/leads", headers=headers)).status_code == 403
    assert (await client.get(f"{BASE}/leads/stats", headers=headers)).status_code == 403


async def test_applicant_downloads_own_resume_only(client):
    mine = await create_lead(client, email="sam@example.com")
    theirs = await create_lead(client, email="other@example.com")
    headers, _ = await _applicant_headers(client)

    ok = await client.get(f"{BASE}/my/leads/{mine['id']}/resume", headers=headers)
    assert ok.status_code == 200

    denied = await client.get(f"{BASE}/my/leads/{theirs['id']}/resume", headers=headers)
    assert denied.status_code == 404
