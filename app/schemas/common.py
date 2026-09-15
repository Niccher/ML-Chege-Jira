"""Standard API response envelopes and common types."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata about inference execution."""

    model_used: str | None = None
    tokens_used: int | None = None
    duration_ms: float | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Standard success envelope."""

    success: bool = True
    data: T
    meta: ResponseMeta | None = None


class ErrorDetail(BaseModel):
    """Error payload details."""

    code: str
    message: str
    details: Any | None = None


class ApiErrorResponse(BaseModel):
    """Standard error envelope."""

    success: bool = False
    error: ErrorDetail
