"""Project wiki page writer queries."""

import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _generate_slug(title: str) -> str:
    """Generate clean URL slug from title."""
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s or "page"


async def create_wiki_page(
    session: AsyncSession,
    project_id: int,
    title: str,
    content: str,
    parent_id: int | None = None,
    created_by: int | None = None,
) -> dict[str, Any]:
    """Insert newly AI-generated page into project_wiki_pages."""
    base_slug = _generate_slug(title)
    slug = base_slug

    # Find unique slug
    check_query = text(
        "SELECT COUNT(*) AS c FROM project_wiki_pages WHERE project_id = :project_id AND slug = :slug"
    )
    counter = 1
    while True:
        res = await session.execute(check_query, {"project_id": project_id, "slug": slug})
        count = res.scalar() or 0
        if count == 0:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Insert page
    insert_query = text(
        """
        INSERT INTO project_wiki_pages (
            project_id, parent_id, title, slug, content, order_index, version, created_by, updated_by, created_at, updated_at
        ) VALUES (
            :project_id, :parent_id, :title, :slug, :content, 0, 1, :created_by, :created_by, NOW(), NOW()
        )
        """
    )
    result = await session.execute(
        insert_query,
        {
            "project_id": project_id,
            "parent_id": parent_id,
            "title": title,
            "slug": slug,
            "content": content,
            "created_by": created_by,
        },
    )
    await session.commit()
    new_id = int(result.lastrowid or 0)

    return {
        "id": new_id,
        "project_id": project_id,
        "parent_id": parent_id,
        "title": title,
        "slug": slug,
        "content": content,
        "version": 1,
    }
