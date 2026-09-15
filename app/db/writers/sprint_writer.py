"""Sprint summary database writer queries."""

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_sprint_summary(
    session: AsyncSession,
    sprint_id: int,
    summary_text: str,
    health_score: int,
    risk_flags: list[str],
    model_used: str,
) -> int:
    """Insert newly generated summary into ai_sprint_summaries."""
    query = text(
        """
        INSERT INTO ai_sprint_summaries (
            sprint_id, summary_text, health_score, risk_flags, model_used, created_at
        ) VALUES (
            :sprint_id, :summary_text, :health_score, :risk_flags, :model_used, NOW()
        )
        """
    )
    result = await session.execute(
        query,
        {
            "sprint_id": sprint_id,
            "summary_text": summary_text,
            "health_score": health_score,
            "risk_flags": json.dumps(risk_flags),
            "model_used": model_used,
        },
    )
    await session.commit()
    return int(result.lastrowid or 0)


async def get_sprint_summaries(session: AsyncSession, sprint_id: int) -> list[dict[str, Any]]:
    """Fetch all AI summaries generated for a specific sprint."""
    query = text(
        """
        SELECT id, sprint_id, summary_text, health_score, risk_flags, model_used, created_at
        FROM ai_sprint_summaries
        WHERE sprint_id = :sprint_id
        ORDER BY created_at DESC
        """
    )
    result = await session.execute(query, {"sprint_id": sprint_id})
    summaries: list[dict[str, Any]] = []
    for r in result.mappings().all():
        d = dict(r)
        if isinstance(d.get("risk_flags"), str):
            try:
                d["risk_flags"] = json.loads(d["risk_flags"])
            except Exception:
                d["risk_flags"] = []
        summaries.append(d)
    return summaries
