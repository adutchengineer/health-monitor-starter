"""Circuit breaker pattern for service health checks.

Implement CircuitBreaker with three states: closed, open, half-open.
"""

from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitOpenError(Exception):
    """Raised when a call is attempted while the circuit is open."""


class CircuitBreaker:
    def __init__(self, failure_threshold: int, cooldown_seconds: float) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count: int = 0
        self.state: str = "closed"
        self._opened_at: float | None = None

    def call(self, fn: Callable[[], T]) -> T:
        raise NotImplementedError("Implement CircuitBreaker.call()")
