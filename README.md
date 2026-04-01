# health-monitor

Starter repo for the APIs & Async module. Fork this repo and follow the lessons.

## Setup

```bash
uv sync --all-extras
uv run pytest tests/ -v
```

## Run locally

```bash
uv run uvicorn health_monitor.app:app --reload
```

## Run with Docker

```bash
docker compose up --build
```

The API runs on port 8000. The Locust load testing UI runs on port 8089.
