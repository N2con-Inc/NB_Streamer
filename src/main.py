"""Main FastAPI application for NB_Streamer.

This is a placeholder file for the development environment setup.
The actual implementation will be added in Phase 1 of development.
"""

from fastapi import FastAPI

# Create FastAPI application instance
app = FastAPI(
    title="NB_Streamer",
    description="Netbird Event Streaming Receiver - Development Environment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - development placeholder."""
    return {
        "message": "NB_Streamer Development Environment",
        "status": "Development setup complete",
        "next_steps": "Begin Phase 1 implementation",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "nb-streamer-dev"}


@app.post("/events")
async def receive_events() -> dict[str, str]:
    """Events endpoint placeholder - to be implemented."""
    return {
        "message": "Events endpoint placeholder",
        "status": "To be implemented in Phase 1",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
