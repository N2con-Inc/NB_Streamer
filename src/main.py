"""Main application module for NB_Streamer."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from .config import config
from .services.auth import AuthService
from .services.graylog import GraylogService as GraylogForwarder
from .services.transformer import TransformerService as EventTransformer

# Version information
__version__ = "0.5.0"

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Initialize services
auth_service = AuthService()
graylog_forwarder = GraylogForwarder()
transformer = EventTransformer()

# Statistics tracking
stats = {
    "total_events_received": 0,
    "total_events_forwarded": 0,
    "total_events_failed": 0,
    "events_by_tenant": {},
    "events_by_level": {},
    "last_event_time": None,
    "service_start_time": None,
    "success_rate": 0.0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting NB_Streamer v{__version__}")
    
    # Validate configuration
    try:
        config.validate_startup_configuration()
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(1)
    
    logger.info(f"Config: graylog_host={config.graylog_host}, port={config.port}, auth_type={config.auth_type}")
    
    # Initialize statistics
    from datetime import datetime, timezone
    stats["service_start_time"] = datetime.now(timezone.utc).isoformat()
    
    yield


app = FastAPI(
    title="NB_Streamer",
    description="Stream NetBird events to Graylog with tenant identification via event payload",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def update_statistics(tenant: str, level: str, success: bool) -> None:
    """Update application statistics."""
    from datetime import datetime, timezone
    
    stats["total_events_received"] += 1
    stats["last_event_time"] = datetime.now(timezone.utc).isoformat()
    
    if success:
        stats["total_events_forwarded"] += 1
    else:
        stats["total_events_failed"] += 1
    
    # Track by tenant
    if tenant not in stats["events_by_tenant"]:
        stats["events_by_tenant"][tenant] = {"received": 0, "forwarded": 0, "failed": 0}
    
    stats["events_by_tenant"][tenant]["received"] += 1
    if success:
        stats["events_by_tenant"][tenant]["forwarded"] += 1
    else:
        stats["events_by_tenant"][tenant]["failed"] += 1
    
    # Track by level
    if level not in stats["events_by_level"]:
        stats["events_by_level"][level] = 0
    stats["events_by_level"][level] += 1
    
    # Calculate success rate
    total = stats["total_events_received"]
    if total > 0:
        stats["success_rate"] = stats["total_events_forwarded"] / total
    else:
        stats["success_rate"] = 0.0


def extract_request_context(request: Request) -> Dict[str, Any]:
    """Extract context information from request."""
    # Get client IP (handle proxy headers)
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    
    # Detect protocol
    protocol = "https" if request.headers.get("x-forwarded-proto") == "https" else "http"
    
    return {
        "method": request.method,
        "path": str(request.url.path),
        "query": str(request.url.query),
        "client_ip": client_ip,
        "protocol": protocol,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nb_streamer",
        "version": __version__,
        "message": "Simplified single-endpoint architecture"
    }


@app.get("/stats")
async def get_statistics():
    """Get application statistics."""
    from datetime import datetime, timezone
    current_stats = stats.copy()
    current_stats["current_time"] = datetime.now(timezone.utc).isoformat()
    
    # Calculate uptime if service_start_time exists
    if current_stats["service_start_time"]:
        start_time = datetime.fromisoformat(current_stats["service_start_time"].replace("Z", "+00:00"))
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - start_time).total_seconds()
        current_stats["uptime_seconds"] = uptime
    
    return {"status": "success", "statistics": current_stats}


@app.post("/events")
async def process_events(request: Request):
    """Process NetBird events with tenant identification via NB_Tenant field."""
    try:
        # Authenticate request
        await auth_service.authenticate(request)
        
        # Parse request body
        try:
            raw_body = await request.body()
            event_data = json.loads(raw_body)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading request body: {str(e)}"
            )
        
        # Validate NB_Tenant field
        if "NB_Tenant" not in event_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "MISSING_TENANT",
                    "message": "NB_Tenant field is required in event payload",
                    "details": {
                        "missing_field": "NB_Tenant",
                        "note": "Add 'NB_Tenant': 'your-tenant-name' to your NetBird webhook body template"
                    }
                }
            )

        tenant = event_data["NB_Tenant"].lower()
        
        # Validate tenant format
        if not config.validate_tenant_format(tenant):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_TENANT_FORMAT",
                    "message": f"Tenant '{tenant}' has invalid format",
                    "details": {
                        "tenant": tenant,
                        "allowed_characters": "alphanumeric, hyphens, underscores",
                        "regex_pattern": "^[a-zA-Z0-9_-]+$"
                    }
                }
            )

        # Transform event
        transformed_event = await transformer.transform_event(event_data, tenant)
        
        # Forward to Graylog
        success = await graylog_forwarder.forward_event(transformed_event)
        
        # Extract request context for logging
        context = extract_request_context(request)
        
        if success:
            # Update statistics
            level = str(getattr(transformed_event, "level", 6))  # Default to INFO level
            update_statistics(tenant, level, True)
            
            # Log success
            context["message"] = "Successfully forwarded event to Graylog"
            context["tenant"] = tenant
            logger.info(f"Successfully forwarded event to Graylog | Context: {context}")
            
            return {
                "status": "success",
                "message": "Event processed and forwarded to Graylog",
                "tenant_id": tenant
            }
        else:
            # Update statistics
            level = str(getattr(transformed_event, "level", 6))  # Default to INFO level
            update_statistics(tenant, level, False)
            
            # Log failure
            context["message"] = "Failed to forward event to Graylog"
            context["tenant"] = tenant
            logger.error(f"Failed to forward event to Graylog | Context: {context}")
            
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to forward event to Graylog"
            )

    except HTTPException:
        raise
    except Exception as e:
        context = extract_request_context(request)
        context["message"] = f"Unexpected error processing event: {str(e)}"
        logger.error(f"Unexpected error processing event: {str(e)} | Context: {context}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Internal server error processing event",
                "details": {"error": str(e)}
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host=config.host, port=config.port)
