"""Task database reader queries."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_task_with_project(session: AsyncSession, task_id: int) -> dict[str, Any] | None:
    """Fetch task row joined with project metadata."""
    query = text(
        """
        SELECT 
            t.id,
            t.user_id,
            t.project_id,
            t.sprint_id,
            t.title,
            t.description,
            t.status,
            t.priority,
            t.story_points,
            t.due_date,
            t.assigned_to,
            p.name AS project_name,
            p.description AS project_description,
            p.tech_stack AS project_tech_stack
        FROM tasks t
        LEFT JOIN projects p ON p.id = t.project_id
        WHERE t.id = :task_id
        LIMIT 1
        """
    )
    result = await session.execute(query, {"task_id": task_id})
    row = result.mappings().first()
    return dict(row) if row else None
