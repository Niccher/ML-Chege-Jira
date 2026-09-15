"""Sprint database reader queries."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_sprint_full_context(session: AsyncSession, sprint_id: int) -> dict[str, Any] | None:
    """Fetch sprint metadata, associated tasks, and team time logs."""
    # 1. Sprint Info
    sprint_query = text(
        """
        SELECT 
            s.id,
            s.project_id,
            s.name,
            s.goal,
            s.status,
            s.start_date,
            s.end_date,
            s.total_points,
            s.completed_points,
            p.name AS project_name
        FROM sprints s
        LEFT JOIN projects p ON p.id = s.project_id
        WHERE s.id = :sprint_id
        LIMIT 1
        """
    )
    sprint_res = await session.execute(sprint_query, {"sprint_id": sprint_id})
    sprint_row = sprint_res.mappings().first()
    if not sprint_row:
        return None

    sprint_data = dict(sprint_row)

    # 2. Tasks in this sprint
    tasks_query = text(
        """
        SELECT 
            t.id,
            t.title,
            t.description,
            t.status,
            t.priority,
            t.story_points,
            u.username AS assignee
        FROM tasks t
        LEFT JOIN users u ON u.id = t.assigned_to
        WHERE t.sprint_id = :sprint_id
        ORDER BY t.status, t.priority DESC
        """
    )
    tasks_res = await session.execute(tasks_query, {"sprint_id": sprint_id})
    sprint_data["tasks"] = [dict(r) for r in tasks_res.mappings().all()]

    return sprint_data
