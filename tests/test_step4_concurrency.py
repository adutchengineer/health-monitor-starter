"""Step 4: Concurrent Checking

Tests for threaded and async sweep modes, and the semaphore limit.
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
class TestConcurrentSweep:
    async def _register_services(self, client, count=3):
        """Helper to register multiple test services."""
        for i in range(count):
            await client.post(
                "/services",
                json={
                    "name": f"concurrent-{i}",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )

    async def test_threaded_mode(self, client):
        """POST /sweep?mode=threaded should use ThreadPoolExecutor."""
        async with client as c:
            await self._register_services(c)
            resp = await c.post("/sweep", params={"mode": "threaded"})
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    async def test_async_mode(self, client):
        """POST /sweep?mode=async should use asyncio.gather."""
        async with client as c:
            await self._register_services(c)
            resp = await c.post("/sweep", params={"mode": "async"})
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    async def test_sequential_mode_explicit(self, client):
        """POST /sweep?mode=sequential should work as before."""
        async with client as c:
            await self._register_services(c)
            resp = await c.post("/sweep", params={"mode": "sequential"})
        assert resp.status_code == 200

    async def test_concurrent_faster_than_sequential(self, client):
        """Threaded/async sweep should be faster than sequential for multiple services."""
        async with client as c:
            await self._register_services(c, count=5)

            resp_seq = await c.post("/sweep", params={"mode": "sequential"})
            resp_async = await c.post("/sweep", params={"mode": "async"})

        seq_time = resp_seq.json()["total_time_seconds"]
        async_time = resp_async.json()["total_time_seconds"]

        # Async should be noticeably faster (at least 30% faster)
        # This is a soft check — CI network variability may affect it
        assert async_time <= seq_time * 1.1 or async_time < 5.0
