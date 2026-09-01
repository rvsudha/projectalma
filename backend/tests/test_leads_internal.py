from __future__ import annotations

from app.core.config import settings
from tests.conftest import SAMPLE_PDF, create_lead

BASE = settings.api_v1_prefix


async def test_list_requires_auth(client):
    assert (await client.get(f"{BASE}/leads")).status_code == 401


async def test_list_returns_paginated_leads(client, auth_headers):
    await create_lead(client, email="a@example.com")
    await create_lead(client, email="b@example.com")

    resp = await client.get(f"{BASE}/leads?limit=1", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"] == {"total": 2, "limit": 1, "offset": 0, "has_more": True}
    assert len(body["items"]) == 1
    assert set(body["items"][0]) >= {
        "first_name",
        "last_name",
        "email",
        "state",
        "resume_filename",
        "resume_size_bytes",
    }


async def test_list_search_filter(client, auth_headers):
    await create_lead(client, first_name="Ada", last_name="Lovelace", email="ada@example.com")
    await create_lead(client, first_name="Grace", last_name="Hopper", email="grace@example.com")

    resp = await client.get(f"{BASE}/leads?search=hopper", headers=auth_headers)
    assert resp.json()["meta"]["total"] == 1
    assert resp.json()["items"][0]["email"] == "grace@example.com"


async def test_state_filter(client, auth_headers):
    a = await create_lead(client, email="a@example.com")
    await create_lead(client, email="b@example.com")
    await client.patch(
        f"{BASE}/leads/{a['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )

    resp = await client.get(f"{BASE}/leads?state=PENDING", headers=auth_headers)
    assert resp.json()["meta"]["total"] == 1
    assert resp.json()["items"][0]["email"] == "b@example.com"


async def test_get_single_lead_includes_events(client, auth_headers):
    lead = await create_lead(client)
    resp = await client.get(f"{BASE}/leads/{lead['id']}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "PENDING"
    assert [e["type"] for e in body["events"]] == ["CREATED"]


async def test_get_missing_lead_404(client, auth_headers):
    resp = await client.get(
        f"{BASE}/leads/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


async def test_get_lead_bad_uuid_422(client, auth_headers):
    assert (await client.get(f"{BASE}/leads/not-a-uuid", headers=auth_headers)).status_code == 422


async def test_download_resume(client, auth_headers):
    lead = await create_lead(client)
    resp = await client.get(f"{BASE}/leads/{lead['id']}/resume", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.content == SAMPLE_PDF
    assert "attachment" in resp.headers["content-disposition"]


async def test_transition_pending_to_reached_out(client, auth_headers):
    lead = await create_lead(client)
    resp = await client.patch(
        f"{BASE}/leads/{lead['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "REACHED_OUT"
    assert body["reached_out_at"] is not None
    assert body["reached_out_by_id"] is not None

    events = await client.get(f"{BASE}/leads/{lead['id']}/events", headers=auth_headers)
    types = [e["type"] for e in events.json()]
    assert types == ["CREATED", "STATE_CHANGED"]
    assert events.json()[-1]["message"] == "PENDING -> REACHED_OUT"
    assert events.json()[-1]["actor_id"] is not None


async def test_reopen_reached_out_back_to_pending(client, auth_headers):
    lead = await create_lead(client)
    await client.patch(
        f"{BASE}/leads/{lead['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )
    resp = await client.patch(
        f"{BASE}/leads/{lead['id']}", json={"state": "PENDING"}, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "PENDING"
    # reopening clears the denormalised reached-out record
    assert body["reached_out_at"] is None
    assert body["reached_out_by_id"] is None

    events = await client.get(f"{BASE}/leads/{lead['id']}/events", headers=auth_headers)
    types = [e["type"] for e in events.json()]
    assert types == ["CREATED", "STATE_CHANGED", "STATE_CHANGED"]
    assert events.json()[-1]["message"] == "REACHED_OUT -> PENDING (reopened)"
    assert events.json()[-1]["actor_id"] is not None


async def test_noop_transition_is_ok(client, auth_headers):
    lead = await create_lead(client)
    resp = await client.patch(
        f"{BASE}/leads/{lead['id']}", json={"state": "PENDING"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "PENDING"


async def test_patch_requires_auth(client):
    resp = await client.patch(
        f"{BASE}/leads/00000000-0000-0000-0000-000000000000", json={"state": "REACHED_OUT"}
    )
    assert resp.status_code == 401


async def test_dashboard_stats(client, auth_headers):
    a = await create_lead(client, email="a@example.com")
    await create_lead(client, email="b@example.com")
    await create_lead(client, email="c@example.com")
    await client.patch(
        f"{BASE}/leads/{a['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )

    resp = await client.get(f"{BASE}/leads/stats", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"total": 3, "pending": 2, "reached_out": 1}


async def test_dashboard_stats_requires_auth(client):
    assert (await client.get(f"{BASE}/leads/stats")).status_code == 401


async def test_activity_feed_shows_recent_status_changes(client, auth_headers):
    a = await create_lead(client, email="a@example.com")
    b = await create_lead(client, email="b@example.com")
    await client.patch(
        f"{BASE}/leads/{a['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )
    await client.patch(
        f"{BASE}/leads/{b['id']}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )

    resp = await client.get(f"{BASE}/leads/activity?limit=10", headers=auth_headers)
    assert resp.status_code == 200
    feed = resp.json()
    # newest first: two STATE_CHANGED then two CREATED
    assert [e["type"] for e in feed] == [
        "STATE_CHANGED",
        "STATE_CHANGED",
        "CREATED",
        "CREATED",
    ]
    top = feed[0]
    assert top["message"] == "PENDING -> REACHED_OUT"
    assert top["lead_name"]  # "First Last"
    assert top["actor_name"]  # the attorney who made the change
    assert feed[-1]["actor_name"] is None  # CREATED events have no actor
