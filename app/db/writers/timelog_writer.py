"""Time report database writer queries."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_time_report(
    session: AsyncSession,
    user_id: int,
    project_id: int | None,
    period_from: str | None,
    period_to: str | None,
    report_text: str,
    model_used: str,
) -> int:
    """Insert time analysis report into ai_time_reports."""
    query = text(
        """
        INSERT INTO ai_time_reports (
            user_id, project_id, period_from, period_to, report_text, model_used, created_at
        ) VALUES (
            :user_id, :project_id, :period_from, :period_to, :report_text, :model_used, NOW()
        )
        """
    )
    result = await session.execute(
        query,
        {
            "user_id": user_id,
            "project_id": project_id,
            "period_from": period_from,
            "period_to": period_to,
            "report_text": report_text,
            "model_used": model_used,
        },
    )
    await session.commit()
    return int(result.lastrowid or 0)
