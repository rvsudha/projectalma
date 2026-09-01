from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta

    @classmethod
    def build(cls, items: list[T], *, total: int, limit: int, offset: int) -> Page[T]:
        return cls(
            items=items,
            meta=PageMeta(
                total=total,
                limit=limit,
                offset=offset,
                has_more=offset + len(items) < total,
            ),
        )


class ErrorDetail(BaseModel):
    code: str = Field(examples=["not_found"])
    message: str
    details: list = Field(default_factory=list)
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """The envelope every non-2xx response uses."""

    error: ErrorDetail
