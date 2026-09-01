"""Applicant self-service portal — a prospect's read-only view of their own cases.

Ownership is by email: a signed-in user sees every lead submitted with their
email address (so submit-then-sign-up works retroactively).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Response

from app.api.deps import CurrentUser, DbSession
from app.core.errors import NotFoundError
from app.schemas.lead import LeadDetail, LeadEventRead, LeadRead
from app.services import leads as lead_service
from app.services.storage import get_storage

router = APIRouter(prefix="/my", tags=["portal"])


@router.get("/leads", response_model=list[LeadDetail], summary="My submitted cases")
async def my_leads(db: DbSession, user: CurrentUser) -> list[LeadDetail]:
    leads = await lead_service.list_leads_for_email(db, user.email)
    out: list[LeadDetail] = []
    for lead in leads:
        events = await lead_service.list_lead_events(db, lead.id)
        out.append(
            LeadDetail(
                **LeadRead.model_validate(lead).model_dump(),
                events=[LeadEventRead.model_validate(e) for e in events],
            )
        )
    return out


@router.get("/leads/{lead_id}/resume", summary="Download my own resume")
async def my_resume(lead_id: uuid.UUID, db: DbSession, user: CurrentUser) -> Response:
    lead = await lead_service.get_lead(db, lead_id)
    if lead.email != user.email.lower():
        raise NotFoundError("Lead not found")
    data = await get_storage().load(lead.resume_key)
    return Response(
        content=data,
        media_type=lead.resume_content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{lead.resume_filename}"',
            "Cache-Control": "private, no-store",
        },
    )
