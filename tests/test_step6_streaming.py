"""Step 6: Streaming Results

Tests for the SSE /stream endpoint.
"""

import json

import pytest
import httpx
from httpx import ASGITransport

from health_monitor.app import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
class TestStreamEndpoint:
    async def test_stream_returns_sse(self, client):
        """GET /stream should return text/event-stream content type."""
        async with client as c:
            # Register a service to stream
            await c.post(
                "/services",
                json={
                    "name": "stream-svc",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.get("/stream")
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

    async def test_stream_yields_json_events(self, client):
        """Each SSE event should contain valid JSON with name and status."""
        async with client as c:
            await c.post(
                "/services",
                json={
                    "name": "event-svc",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.get("/stream")

        # Parse SSE events from the response body
        body = resp.text
        events = []
        for line in body.strip().split("\n"):
            line = line.strip()
            if line.startswith("data:"):
                data_str = line[len("data:"):].strip()
                if data_str:
                    events.append(json.loads(data_str))

        assert len(events) > 0, "No SSE events found in response"
        for event in events:
            assert "name" in event
            assert "status" in event
