"""Task-related request and response schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class TaskEnhanceRequest(BaseModel):
    """Request payload for enhancing a task description."""

    model: str | None = Field(default=None, description="Optional override of model key")
    max_tokens: int = Field(default=1024, ge=128, le=4096)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)


class TaskEnhanceData(BaseModel):
    id: int
    task_id: int
    summary: str
    acceptance_criteria: list[str]
    story_points: int | None
    priority: Literal["low", "medium", "high", "critical"] | None


class PrioritySuggestRequest(BaseModel):
    """Request payload for priority and story point estimation."""

    model: str | None = Field(default=None, description="Optional override of model key")


class PrioritySuggestData(BaseModel):
    task_id: int
    priority: Literal["low", "medium", "high", "critical"]
    story_points: int
    reasoning: str | None = None
