"""Load testing for the Health Monitor API."""

from locust import HttpUser, between, task


class HealthMonitorUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def check_health(self):
        self.client.get("/health")

    @task(1)
    def list_services(self):
        self.client.get("/services")
