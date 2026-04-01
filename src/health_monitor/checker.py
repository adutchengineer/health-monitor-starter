"""Service health checker."""


async def check_service(url: str) -> dict:
    """Check the health of a service at the given URL.

    Implement in Lesson 2: Send an HTTP GET request to the URL and return
    a dict with keys: url, status_code, response_time_ms, healthy.

    Args:
        url: The URL to check.

    Returns:
        A dict describing the health check result.
    """
    pass
