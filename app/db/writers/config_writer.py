"""AI runtime configuration database reader and writer queries."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_ai_config(session: AsyncSession) -> dict[str, Any]:
    """Fetch current AI runtime settings from ai_config table."""
    query = text(
        """
        SELECT default_model, n_gpu_layers, n_threads, n_ctx, updated_at
        FROM ai_config
        WHERE id = 1
        LIMIT 1
        """
    )
    result = await session.execute(query)
    row = result.mappings().first()
    if not row:
        return {
            "default_model": "mistral-7b",
            "n_gpu_layers": 0,
            "n_threads": 4,
            "n_ctx": 4096,
            "updated_at": None,
        }
    return dict(row)


async def update_ai_config(
    session: AsyncSession,
    default_model: str | None = None,
    n_gpu_layers: int | None = None,
    n_threads: int | None = None,
    n_ctx: int | None = None,
) -> dict[str, Any]:
    """Update runtime settings in ai_config table."""
    current = await get_ai_config(session)

    new_default = default_model if default_model is not None else current["default_model"]
    new_gpu = n_gpu_layers if n_gpu_layers is not None else current["n_gpu_layers"]
    new_threads = n_threads if n_threads is not None else current["n_threads"]
    new_ctx = n_ctx if n_ctx is not None else current["n_ctx"]

    query = text(
        """
        INSERT INTO ai_config (id, default_model, n_gpu_layers, n_threads, n_ctx, updated_at)
        VALUES (1, :default_model, :n_gpu_layers, :n_threads, :n_ctx, NOW())
        ON DUPLICATE KEY UPDATE
            default_model = VALUES(default_model),
            n_gpu_layers = VALUES(n_gpu_layers),
            n_threads = VALUES(n_threads),
            n_ctx = VALUES(n_ctx),
            updated_at = NOW()
        """
    )
    await session.execute(
        query,
        {
            "default_model": new_default,
            "n_gpu_layers": new_gpu,
            "n_threads": new_threads,
            "n_ctx": new_ctx,
        },
    )
    await session.commit()

    return await get_ai_config(session)
