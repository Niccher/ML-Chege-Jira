"""Project Wiki reader queries."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_wiki_page_by_id(session: AsyncSession, page_id: int) -> dict[str, Any] | None:
    """Fetch single wiki page row."""
    query = text(
        """
        SELECT id, project_id, parent_id, title, slug, content, version, created_at, updated_at
        FROM project_wiki_pages
        WHERE id = :page_id
        LIMIT 1
        """
    )
    result = await session.execute(query, {"page_id": page_id})
    row = result.mappings().first()
    return dict(row) if row else None
