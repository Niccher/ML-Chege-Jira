"""Pytest fixtures for unit and integration testing."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_session
from app.config import settings
from app.main import app


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Mock database session for fast unit tests without live MySQL."""
    mock = MagicMock()
    return mock


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client for invoking FastAPI routes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Default headers containing valid X-API-Key."""
    return {"X-API-Key": settings.API_KEY, "Content-Type": "application/json"}
