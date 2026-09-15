"""Shared FastAPI route dependencies."""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_api_key
from app.db.session import get_db_session
from app.db.writers.config_writer import get_ai_config


async def get_session(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(verify_api_key),
) -> AsyncGenerator[AsyncSession, None]:
    """Yields verified database session protected by X-API-Key."""
    yield session


async def get_runtime_config(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Fetch cached runtime configuration from database."""
    return await get_ai_config(session)
