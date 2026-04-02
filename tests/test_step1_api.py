"""Step 1: Build the API

Tests for FastAPI endpoints — health, CRUD for services, Pydantic validation.
"""

import pytest
import httpx
from httpx import ASGITransport

from health_monitor.app import app


@pytest.fixture
def client():
    """Return an httpx test client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
class TestHealthEndpoint:
    async def test_health_returns_ok(self, client):
        """GET /health should return 200 with status ok."""
        async with client as c:
            resp = await c.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.anyio
class TestServiceCRUD:
    async def test_register_service(self, client):
        """POST /services should register a service and return 201."""
        async with client as c:
            resp = await c.post(
                "/services",
                json={
                    "name": "payment-api",
                    "url": "https://api.example.com/health",
                    "expected_status": 200,
                },
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "payment-api"

    async def test_list_services(self, client):
        """GET /services should return all registered services."""
        async with client as c:
            # Register one first
            await c.post(
                "/services",
                json={
                    "name": "test-svc",
                    "url": "https://example.com/health",
                    "expected_status": 200,
                },
            )
            resp = await c.get("/services")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_service_by_name(self, client):
        """GET /services/{name} should return the specific service."""
        async with client as c:
            await c.post(
                "/services",
                json={
                    "name": "lookup-svc",
                    "url": "https://example.com/health",
                    "expected_status": 200,
                },
            )
            resp = await c.get("/services/lookup-svc")
        assert resp.status_code == 200
        assert resp.json()["name"] == "lookup-svc"

    async def test_get_missing_service_404(self, client):
        """GET /services/{name} should return 404 for unknown services."""
        async with client as c:
            resp = await c.get("/services/nonexistent")
        assert resp.status_code == 404

    async def test_delete_service(self, client):
        """DELETE /services/{name} should remove the service."""
        async with client as c:
            await c.post(
                "/services",
                json={
                    "name": "delete-me",
                    "url": "https://example.com/health",
                    "expected_status": 200,
                },
            )
            resp = await c.delete("/services/delete-me")
        assert resp.status_code == 200

    async def test_pydantic_validation(self, client):
        """POST /services with missing fields should return 422."""
        async with client as c:
            resp = await c.post("/services", json={"name": "bad"})
        assert resp.status_code == 422
