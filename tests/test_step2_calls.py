"""Step 2: Add Health Checks

Tests for the checker module — HTTP calls, timeouts, retries,
and the /services/{name}/check endpoint.
"""

import time

import pytest
import httpx
from httpx import ASGITransport

from health_monitor.app import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


class TestCheckService:
    def test_check_returns_result_dict(self):
        """check_service should return a dict with name, status, response_time_ms, timestamp."""
        from health_monitor.checker import check_service

        # Use the app's own health endpoint as target
        result = check_service("self", "http://localhost:8000/health", 200)
        # The function may fail if the server isn't running, but it should
        # still return a result dict (status = "error" is fine)
        assert "name" in result
        assert "status" in result
        assert result["status"] in ("healthy", "unhealthy", "error")

    def test_check_timeout_handling(self):
        """check_service should handle timeouts gracefully."""
        from health_monitor.checker import check_service

        # Use a non-routable IP to trigger timeout
        result = check_service("slow", "http://192.0.2.1/health", 200)
        assert result["status"] == "error"

    def test_check_connect_error_handling(self):
        """check_service should handle connection errors gracefully."""
        from health_monitor.checker import check_service

        result = check_service("down", "http://localhost:1/health", 200)
        assert result["status"] == "error"


@pytest.mark.anyio
class TestCheckEndpoint:
    async def test_check_endpoint_returns_result(self, client):
        """POST /services/{name}/check should trigger a check and return results."""
        async with client as c:
            # Register a service first
            await c.post(
                "/services",
                json={
                    "name": "check-target",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.post("/services/check-target/check")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    async def test_check_unknown_service_404(self, client):
        """POST /services/{name}/check should 404 for unknown services."""
        async with client as c:
            resp = await c.post("/services/ghost/check")
        assert resp.status_code == 404


class TestRetryLogic:
    def test_retry_on_failure(self):
        """check_service should retry up to 2 times on failure."""
        from health_monitor.checker import check_service

        start = time.monotonic()
        result = check_service("retry-test", "http://localhost:1/health", 200)
        elapsed = time.monotonic() - start
        # With retries and exponential backoff (sleep 1 + sleep 2 = 3s min),
        # the call should take at least 1 second if retries are happening
        assert result["status"] == "error"
        assert elapsed >= 1.0, "Retries do not appear to be happening"
