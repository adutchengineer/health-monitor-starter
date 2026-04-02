# health-monitor

A service health monitoring tool you will build step by step through the [APIs & Async](https://dutchengineer.com/foundations/apis-async/) module. Each step applies concepts from the corresponding lesson — REST APIs, HTTP clients, concurrency, parallelism, and streaming.

## Getting started

```bash
uv sync --all-extras
uv run pytest tests/ -v
```

You can also run the API locally as you build it:

```bash
uv run uvicorn health_monitor.app:app --reload
```

The starter comes with a `/health` endpoint. Everything else is up to you.

## How it works

The [project page](https://dutchengineer.com/foundations/apis-async/project-health-monitor/) walks you through 6 steps. After each step, run the tests, commit, and push. CI validates your work automatically — green checks mean the step passes.

**Step 1 — Build the API** creates the CRUD endpoints for registering, listing, and removing services to monitor. Pydantic models handle request and response validation. Run `uv run pytest tests/test_step1_api.py`.

**Step 2 — Health Checks** implements the checker — making HTTP calls with timeouts, handling errors gracefully, and retrying with exponential backoff. Run `uv run pytest tests/test_step2_calls.py`.

**Step 3 — Sequential Cost** adds a `/sweep` endpoint that checks all registered services one by one and measures the total time. This is where you see the problem that concurrency solves. Run `uv run pytest tests/test_step3_sequential.py`.

**Step 4 — Concurrent Checking** makes the sweep fast with `ThreadPoolExecutor` and `asyncio.gather`. The `/sweep` endpoint now accepts a `?mode=sequential|threaded|async` parameter so you can compare. Run `uv run pytest tests/test_step4_concurrency.py`.

**Step 5 — CPU Validation** adds CPU-intensive payload validation using `ProcessPoolExecutor`, demonstrating when threads are not enough and processes are needed. Run `uv run pytest tests/test_step5_parallel.py`.

**Step 6 — Streaming Results** adds a `/stream` endpoint using Server-Sent Events, so check results appear one by one as they complete instead of all at the end. Run `uv run pytest tests/test_step6_streaming.py`.

## Project structure

As you work through the steps, you will create these files:

```
src/health_monitor/
├── __init__.py
├── app.py           # FastAPI application (Steps 1, 3-4, 6)
├── checker.py       # Health check logic (Step 2)
├── models.py        # Pydantic request/response models (Step 1)
└── validator.py     # CPU-intensive validation (Step 5)
locustfile.py        # Load testing (Step 6)
Dockerfile           # Container build (provided)
docker-compose.yml   # Multi-service setup (provided)
```
