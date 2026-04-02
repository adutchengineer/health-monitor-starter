"""Step 3: Measure Sequential Cost

Tests for the /sweep endpoint in sequential mode.
"""

import pytest
import httpx
from httpx import ASGITransport

from health_monitor.app import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
class TestSequentialSweep:
    async def test_sweep_returns_results(self, client):
        """POST /sweep should return a list of check results."""
        async with client as c:
            # Register a couple of services
            await c.post(
                "/services",
                json={
                    "name": "svc-a",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            await c.post(
                "/services",
                json={
                    "name": "svc-b",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.post("/sweep")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    async def test_sweep_includes_total_time(self, client):
        """POST /sweep response should include total_time_seconds."""
        async with client as c:
            await c.post(
                "/services",
                json={
                    "name": "timed-svc",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.post("/sweep")
        data = resp.json()
        assert "total_time_seconds" in data
        assert isinstance(data["total_time_seconds"], (int, float))
        assert data["total_time_seconds"] >= 0
