"""TimeLog database reader queries."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_time_logs(
    session: AsyncSession,
    user_id: int,
    project_id: int | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch filtered time logs for productivity analysis."""
    conditions = ["tl.user_id = :user_id"]
    params: dict[str, Any] = {"user_id": user_id}

    if project_id:
        conditions.append("tl.project_id = :project_id")
        params["project_id"] = project_id

    if from_date:
        conditions.append("DATE(tl.start_time) >= :from_date")
        params["from_date"] = from_date

    if to_date:
        conditions.append("DATE(tl.start_time) <= :to_date")
        params["to_date"] = to_date

    where_clause = " AND ".join(conditions)

    query = text(
        f"""
        SELECT 
            tl.id,
            tl.task_name,
            tl.start_time,
            tl.end_time,
            tl.duration,
            tl.is_billable,
            tl.notes,
            p.name AS project_name,
            u.username
        FROM time_logs tl
        LEFT JOIN projects p ON p.id = tl.project_id
        LEFT JOIN users u ON u.id = tl.user_id
        WHERE {where_clause}
        ORDER BY tl.start_time DESC
        LIMIT 100
        """
    )

    result = await session.execute(query, params)
    return [dict(r) for r in result.mappings().all()]
