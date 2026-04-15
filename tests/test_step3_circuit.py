"""Step 3: Add Circuit Breaker

Tests for CircuitBreaker in src/health_monitor/circuit_breaker.py
and the /services/{name}/circuit endpoint.
"""

import pytest
import httpx
from httpx import ASGITransport

from health_monitor.app import app
from health_monitor.circuit_breaker import CircuitBreaker, CircuitOpenError


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


class TestCircuitBreakerUnit:
    def test_circuit_starts_closed(self):
        """CircuitBreaker should start in closed state."""
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=10)
        assert cb.state == "closed"

    def test_successful_call_passes_through(self):
        """call() should invoke the function and return its result when closed."""
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=10)
        result = cb.call(lambda: "ok")
        assert result == "ok"

    def test_failures_open_circuit(self):
        """Circuit should open after failure_threshold failures."""
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=60)

        def failing():
            raise ValueError("down")

        for _ in range(3):
            try:
                cb.call(failing)
            except ValueError:
                pass

        assert cb.state == "open"

    def test_open_circuit_raises_circuit_open_error(self):
        """CircuitOpenError should be raised immediately when circuit is open."""
        cb = CircuitBreaker(failure_threshold=1, cooldown_seconds=60)

        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        except RuntimeError:
            pass

        with pytest.raises(CircuitOpenError):
            cb.call(lambda: "should not run")

    def test_failure_count_resets_on_success(self):
        """A successful call should reset the failure count."""
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=60)

        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        except RuntimeError:
            pass

        cb.call(lambda: "ok")
        assert cb.failure_count == 0


@pytest.mark.anyio
class TestCircuitEndpoint:
    async def test_circuit_endpoint_exists(self, client):
        """GET /services/{name}/circuit should return circuit state."""
        async with client as c:
            await c.post(
                "/services",
                json={
                    "name": "circuit-svc",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.get("/services/circuit-svc/circuit")
        assert resp.status_code == 200
        data = resp.json()
        assert "state" in data
        assert data["state"] in ("closed", "open", "half-open")

    async def test_circuit_endpoint_includes_failure_count(self, client):
        """GET /services/{name}/circuit response should include failure_count."""
        async with client as c:
            await c.post(
                "/services",
                json={
                    "name": "count-svc",
                    "url": "https://httpbin.org/status/200",
                    "expected_status": 200,
                },
            )
            resp = await c.get("/services/count-svc/circuit")
        data = resp.json()
        assert "failure_count" in data
        assert isinstance(data["failure_count"], int)
