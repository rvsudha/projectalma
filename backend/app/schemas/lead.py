from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, field_validator

from app.models.lead import LEAD_MILESTONE, LeadState
from app.models.lead_event import LeadEventType


class LeadCreate(BaseModel):
    """Fields the public prospect submits (multipart form; resume handled separately)."""

    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    email: EmailStr

    @field_validator("first_name", "last_name")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v


class LeadUpdate(BaseModel):
    """Internal update. Moves the lead between PENDING and REACHED_OUT (either way)."""

    state: LeadState


class LeadEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: LeadEventType
    message: str
    actor_id: uuid.UUID | None
    created_at: datetime


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    state: LeadState
    resume_filename: str
    resume_content_type: str
    resume_size_bytes: int
    reached_out_at: datetime | None
    reached_out_by_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def milestone(self) -> str:
        """Current-milestone label shown on both dashboards, derived from state."""
        return LEAD_MILESTONE[self.state]


class LeadDetail(LeadRead):
    events: list[LeadEventRead] = Field(default_factory=list)


class LeadCreateResponse(BaseModel):
    id: uuid.UUID
    state: LeadState
    message: str = "Thanks — we received your submission and will be in touch."


class LeadStats(BaseModel):
    total: int
    pending: int
    reached_out: int


class ActivityItem(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    lead_name: str
    type: LeadEventType
    message: str
    actor_name: str | None
    created_at: datetime
