"""Project database reader queries."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_project_with_tasks_and_wiki(
    session: AsyncSession, project_id: int
) -> dict[str, Any] | None:
    """Fetch project details, recent tasks, and existing wiki page titles."""
    # 1. Project details
    proj_query = text(
        """
        SELECT 
            id, name, slug, description, tech_stack, status, priority, repository_url
        FROM projects
        WHERE id = :project_id AND deleted_at IS NULL
        LIMIT 1
        """
    )
    proj_res = await session.execute(proj_query, {"project_id": project_id})
    proj_row = proj_res.mappings().first()
    if not proj_row:
        return None

    data = dict(proj_row)

    # 2. Associated tasks
    tasks_query = text(
        """
        SELECT id, title, description, status, priority, story_points
        FROM tasks
        WHERE project_id = :project_id
        ORDER BY created_at DESC
        LIMIT 25
        """
    )
    tasks_res = await session.execute(tasks_query, {"project_id": project_id})
    data["tasks"] = [dict(r) for r in tasks_res.mappings().all()]

    # 3. Existing wiki pages
    wiki_query = text(
        """
        SELECT id, title, slug
        FROM project_wiki_pages
        WHERE project_id = :project_id
        ORDER BY order_index ASC, title ASC
        """
    )
    wiki_res = await session.execute(wiki_query, {"project_id": project_id})
    data["existing_wiki_pages"] = [dict(r) for r in wiki_res.mappings().all()]

    return data
