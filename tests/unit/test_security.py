"""Tests for security and API key authentication."""

import pytest
from fastapi import HTTPException

from app.config import settings
from app.core.security import verify_api_key


@pytest.mark.asyncio
async def test_verify_api_key_valid() -> None:
    """Valid API key passes verification."""
    result = await verify_api_key(settings.API_KEY)
    assert result == settings.API_KEY


@pytest.mark.asyncio
async def test_verify_api_key_invalid() -> None:
    """Invalid API key raises 403 Forbidden."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key("wrong_secret_key")
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_verify_api_key_missing() -> None:
    """Missing API key raises 403 Forbidden."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(None)
    assert exc_info.value.status_code == 403
