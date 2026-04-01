import pytest


class TestHealthEndpoint:
    def test_health_endpoint(self):
        """GET /health should return 200 with {"status": "ok"}.

        Use httpx.AsyncClient with the FastAPI app as transport:
            async with httpx.AsyncClient(transport=ASGITransport(app=app)) as client:
                response = await client.get("http://test/health")
        """
        pytest.skip("Implement in Lesson 1")


class TestServiceRegistration:
    def test_register_service(self):
        """POST /services should register a new service to monitor.

        Request body: {"name": "api", "url": "https://api.example.com/health"}
        Response: 201 with the registered service including an id.
        """
        pytest.skip("Implement in Lesson 2")

    def test_register_duplicate_service(self):
        """Registering a service with a duplicate name should return 409."""
        pytest.skip("Implement in Lesson 2")


class TestServiceChecks:
    def test_check_services(self):
        """GET /services/check should trigger health checks on all registered services.

        Response: list of check results with url, status_code, response_time_ms, healthy.
        """
        pytest.skip("Implement in Lesson 3")
