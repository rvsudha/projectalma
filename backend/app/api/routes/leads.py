from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, Response, UploadFile
from fastapi import status as http_status
from pydantic import ValidationError

from app.api.deps import CurrentAttorney, DbSession, rate_limit
from app.core.config import settings
from app.core.errors import PayloadTooLargeError, UnsupportedMediaTypeError, ValidationAppError
from app.models.lead import LeadState
from app.schemas.common import Page
from app.schemas.lead import (
    ActivityItem,
    LeadCreate,
    LeadCreateResponse,
    LeadDetail,
    LeadEventRead,
    LeadRead,
    LeadStats,
    LeadUpdate,
)
from app.services import leads as lead_service
from app.services.email import Recipient, send_new_lead_emails
from app.services.storage import get_storage

router = APIRouter(prefix="/leads", tags=["leads"])

_create_rate_limit = rate_limit(
    "lead_create",
    limit=lambda: settings.rate_limit_lead_create_per_hour,
    window_seconds=3600,
)


@router.post(
    "",
    response_model=LeadCreateResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Submit a lead (public)",
    dependencies=[Depends(_create_rate_limit)],
)
async def create_lead(
    db: DbSession,
    background_tasks: BackgroundTasks,
    first_name: Annotated[str, Form(max_length=120)],
    last_name: Annotated[str, Form(max_length=120)],
    email: Annotated[str, Form(max_length=320)],
    resume: Annotated[UploadFile, File(description="Resume / CV (PDF, DOC or DOCX)")],
) -> LeadCreateResponse:
    try:
        payload = LeadCreate(first_name=first_name, last_name=last_name, email=email)
    except ValidationError as exc:
        raise ValidationAppError(
            "Invalid lead details",
            details=exc.errors(include_url=False, include_context=False),
        ) from exc

    content_type = (resume.content_type or "").split(";")[0].strip().lower()
    if content_type not in settings.allowed_resume_content_types:
        raise UnsupportedMediaTypeError(
            f"Unsupported resume type '{content_type or 'unknown'}'. Accepted: PDF, DOC, DOCX."
        )

    # Read with a hard cap: stop at limit + 1 byte so a huge upload can't OOM us.
    data = await resume.read(settings.max_resume_bytes + 1)
    if not data:
        raise ValidationAppError("Resume file is empty.")
    if len(data) > settings.max_resume_bytes:
        raise PayloadTooLargeError(
            f"Resume exceeds the {settings.max_resume_bytes // (1024 * 1024)} MiB limit."
        )

    lead = await lead_service.create_lead(
        db,
        payload=payload,
        resume_bytes=data,
        resume_filename=resume.filename or "resume",
        resume_content_type=content_type,
    )
    await db.commit()

    background_tasks.add_task(
        send_new_lead_emails,
        prospect=Recipient(email=lead.email, first_name=lead.first_name, last_name=lead.last_name),
        lead_id=str(lead.id),
    )
    return LeadCreateResponse(id=lead.id, state=lead.state)


@router.get(
    "",
    response_model=Page[LeadRead],
    summary="List leads (internal)",
)
async def list_leads(
    db: DbSession,
    _: CurrentAttorney,
    state: Annotated[LeadState | None, Query()] = None,
    search: Annotated[str | None, Query(max_length=200, description="name or email")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[LeadRead]:
    items, total = await lead_service.list_leads(
        db, state=state, search=search, limit=limit, offset=offset
    )
    return Page.build(
        [LeadRead.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=LeadStats, summary="Dashboard summary counts (internal)")
async def lead_stats(db: DbSession, _: CurrentAttorney) -> LeadStats:
    return LeadStats(**await lead_service.stats(db))


@router.get(
    "/activity",
    response_model=list[ActivityItem],
    summary="Recent status changes across all leads (internal)",
)
async def lead_activity(
    db: DbSession,
    _: CurrentAttorney,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ActivityItem]:
    return [
        ActivityItem.model_validate(r) for r in await lead_service.list_activity(db, limit=limit)
    ]


@router.get("/{lead_id}", response_model=LeadDetail, summary="Get one lead (internal)")
async def get_lead(lead_id: uuid.UUID, db: DbSession, _: CurrentAttorney) -> LeadDetail:
    lead = await lead_service.get_lead(db, lead_id)
    events = await lead_service.list_lead_events(db, lead_id)
    return LeadDetail(
        **LeadRead.model_validate(lead).model_dump(),
        events=[LeadEventRead.model_validate(e) for e in events],
    )


@router.get(
    "/{lead_id}/events",
    response_model=list[LeadEventRead],
    summary="Lead audit trail (internal)",
)
async def list_events(lead_id: uuid.UUID, db: DbSession, _: CurrentAttorney) -> list[LeadEventRead]:
    await lead_service.get_lead(db, lead_id)  # 404 if missing
    events = await lead_service.list_lead_events(db, lead_id)
    return [LeadEventRead.model_validate(e) for e in events]


@router.get("/{lead_id}/resume", summary="Download a lead's resume (internal)")
async def download_resume(lead_id: uuid.UUID, db: DbSession, _: CurrentAttorney) -> Response:
    lead = await lead_service.get_lead(db, lead_id)
    data = await get_storage().load(lead.resume_key)
    return Response(
        content=data,
        media_type=lead.resume_content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{lead.resume_filename}"',
            "Cache-Control": "private, no-store",
        },
    )


@router.patch("/{lead_id}", response_model=LeadRead, summary="Update lead state (internal)")
async def update_lead(
    lead_id: uuid.UUID, payload: LeadUpdate, db: DbSession, current_user: CurrentAttorney
) -> LeadRead:
    lead = await lead_service.update_lead_state(
        db, lead_id=lead_id, new_state=payload.state, actor=current_user
    )
    await db.commit()
    await db.refresh(lead)  # reload server-side onupdate columns after commit
    return LeadRead.model_validate(lead)
