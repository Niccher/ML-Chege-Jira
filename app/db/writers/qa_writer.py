"""Q&A log writer queries."""

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_qa_log(
    session: AsyncSession,
    question: str,
    context_json: dict[str, Any] | None,
    answer: str,
    model_used: str,
) -> int:
    """Insert Q&A interaction into ai_qa_log."""
    query = text(
        """
        INSERT INTO ai_qa_log (
            question, context_json, answer, model_used, created_at
        ) VALUES (
            :question, :context_json, :answer, :model_used, NOW()
        )
        """
    )
    result = await session.execute(
        query,
        {
            "question": question,
            "context_json": json.dumps(context_json) if context_json else None,
            "answer": answer,
            "model_used": model_used,
        },
    )
    await session.commit()
    return int(result.lastrowid or 0)
