"""Sprint-related request and response schemas."""

from pydantic import BaseModel, Field


class SprintSummaryRequest(BaseModel):
    """Request payload for generating a sprint summary."""

    model: str | None = Field(default=None, description="Optional override of model key")
    max_tokens: int = Field(default=1500, ge=256, le=4096)
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)


class SprintSummaryData(BaseModel):
    id: int
    sprint_id: int
    summary_text: str
    health_score: int = Field(ge=0, le=100)
    risk_flags: list[str] = Field(default_factory=list)
