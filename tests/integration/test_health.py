"""Integration tests for health probe and models list."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    """GET /api/v1/health returns 200 OK and valid status envelope."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "status" in body["data"]


@pytest.mark.asyncio
async def test_models_endpoint_unauthorized(async_client: AsyncClient) -> None:
    """GET /api/v1/models without API key returns 403."""
    response = await async_client.get("/api/v1/models")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_models_endpoint_authorized(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /api/v1/models with valid API key returns 200 and list of models."""
    response = await async_client.get("/api/v1/models", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "models" in body["data"]
    assert "mistral-7b" in body["data"]["models"]
