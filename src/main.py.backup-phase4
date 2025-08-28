"""Main FastAPI application for NB_Streamer."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from .config import config
from .services.auth import AuthService
from .services.graylog import GraylogService
from .services.stats import event_stats
from .services.transformer import TransformerService

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Global service instances
auth_service = AuthService()
transformer_service = TransformerService()
graylog_service = GraylogService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting NB_Streamer")
    logger.info(
        f"Config: tenant_id={config.tenant_id}, graylog_host={config.graylog_host}"
    )

    if config.graylog_protocol == "tcp":
        try:
            graylog_service.connect()
            logger.info("Connected to Graylog via TCP")
        except Exception as e:
            logger.error(f"Failed to connect to Graylog: {e}")
            raise

    yield

    # Shutdown
    logger.info("Shutting down NB_Streamer")
    graylog_service.close()


# Create FastAPI app
app = FastAPI(
    title="NB_Streamer",
    description="Netbird Event Streaming Service to Graylog",
    version="0.2.6",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nb_streamer",
        "version": "0.2.6",
        "tenant_id": config.tenant_id,
    }


@app.get("/stats")
async def get_statistics():
    """Get event processing statistics."""
    try:
        stats = event_stats.get_stats()
        return {"status": "success", "statistics": stats}
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )


@app.post("/stats/reset")
async def reset_statistics(request: Request):
    """Reset event processing statistics (requires authentication)."""
    try:
        # Authenticate request
        await auth_service.authenticate(request)

        # Reset statistics
        event_stats.reset_stats()

        return {"status": "success", "message": "Statistics reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset statistics",
        )


@app.post("/events")
async def receive_events(request: Request):
    """
    Receive Netbird events and forward them to Graylog.

    This endpoint:
    1. Authenticates the request
    2. Parses the JSON event data
    3. Transforms it to GELF format
    4. Sends it to Graylog
    """
    tenant_id = config.tenant_id

    try:
        # Authenticate request
        await auth_service.authenticate(request)

        # Track received event
        event_stats.increment_received(tenant_id)

        # Parse JSON body
        try:
            event_data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            event_stats.increment_failed(tenant_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON in request body",
            )

        # Validate basic event structure and log for discovery
        if not transformer_service.validate_event_structure(event_data):
            logger.warning("Event failed basic validation but will still process")

        # Transform event to GELF
        gelf_message = await transformer_service.transform_event(event_data)

        # Send to Graylog
        try:
            graylog_service.send_gelf_message(gelf_message)

            # Track successful forwarding
            level = str(getattr(gelf_message, "level", "unknown"))
            event_stats.increment_forwarded(tenant_id, level)

            logger.info(
                f"Successfully forwarded event to Graylog for tenant {tenant_id}"
            )
        except Exception as e:
            logger.error(f"Failed to send message to Graylog: {e}")
            event_stats.increment_failed(tenant_id)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to forward event to Graylog",
            )

        # Return success response
        return {
            "status": "success",
            "message": "Event processed and forwarded to Graylog",
            "tenant_id": tenant_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing event: {e}")
        event_stats.increment_failed(tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing event",
        )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with custom response."""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found. Available endpoints listed below.",
            "available_endpoints": {
                "POST /events": "Send Netbird events (authenticated)",
                "GET /health": "Health check",
                "GET /stats": "Get event processing statistics",
                "POST /stats/reset": "Reset statistics (authenticated)",
            },
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)
