"""Time log report schemas."""

from pydantic import BaseModel, Field


class TimeReportRequest(BaseModel):
    """Request payload for generating productivity analysis from time logs."""

    user_id: int
    project_id: int | None = None
    period_from: str | None = Field(default=None, description="YYYY-MM-DD")
    period_to: str | None = Field(default=None, description="YYYY-MM-DD")
    model: str | None = None


class TimeReportData(BaseModel):
    id: int
    user_id: int
    project_id: int | None
    period_from: str | None
    period_to: str | None
    report_text: str
