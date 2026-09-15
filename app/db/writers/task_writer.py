"""Task enhancement writer queries."""

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task_enhancement(
    session: AsyncSession,
    task_id: int,
    summary: str,
    acceptance_criteria: list[str],
    story_points: int | None,
    priority: str | None,
    model_used: str,
    tokens_used: int,
) -> int:
    """Insert newly generated enhancement into ai_task_enhancements."""
    query = text(
        """
        INSERT INTO ai_task_enhancements (
            task_id, summary, acceptance_criteria, story_points, priority, model_used, tokens_used, created_at
        ) VALUES (
            :task_id, :summary, :acceptance_criteria, :story_points, :priority, :model_used, :tokens_used, NOW()
        )
        """
    )
    result = await session.execute(
        query,
        {
            "task_id": task_id,
            "summary": summary,
            "acceptance_criteria": json.dumps(acceptance_criteria),
            "story_points": story_points,
            "priority": priority.lower() if priority else None,
            "model_used": model_used,
            "tokens_used": tokens_used,
        },
    )
    await session.commit()
    return int(result.lastrowid or 0)


async def get_task_enhancements(session: AsyncSession, task_id: int) -> list[dict[str, Any]]:
    """Fetch all enhancements created for a specific task."""
    query = text(
        """
        SELECT id, task_id, summary, acceptance_criteria, story_points, priority, model_used, tokens_used, created_at
        FROM ai_task_enhancements
        WHERE task_id = :task_id
        ORDER BY created_at DESC
        """
    )
    result = await session.execute(query, {"task_id": task_id})
    enhancements: list[dict[str, Any]] = []
    for r in result.mappings().all():
        d = dict(r)
        if isinstance(d.get("acceptance_criteria"), str):
            try:
                d["acceptance_criteria"] = json.loads(d["acceptance_criteria"])
            except Exception:
                d["acceptance_criteria"] = []
        enhancements.append(d)
    return enhancements
