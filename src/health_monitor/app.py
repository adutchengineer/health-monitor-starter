"""Health Monitor FastAPI application."""

from fastapi import FastAPI

app = FastAPI(title="Health Monitor")


@app.get("/health")
async def health():
    """Health check endpoint for the monitor itself."""
    return {"status": "ok"}
