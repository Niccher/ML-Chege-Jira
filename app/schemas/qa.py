"""Q&A schemas."""

from typing import Any

from pydantic import BaseModel, Field


class QaRequest(BaseModel):
    """Request payload for project-grounded Q&A."""

    question: str = Field(min_length=3)
    context: dict[str, Any] | None = Field(default=None, description="Optional extra context")
    model: str | None = None


class QaData(BaseModel):
    id: int
    question: str
    answer: str
