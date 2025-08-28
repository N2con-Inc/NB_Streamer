"""Main FastAPI application for NB_Streamer with multi-tenancy support."""

import logging
import re
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Response, status
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
    logger.info("Starting NB_Streamer v0.3.0")
    
    # Validate configuration at startup
    # config.validate_startup_configuration()  # TODO: Add this method if needed
    
    logger.info(
        f"Config: graylog_host={config.graylog_host}, "
        f"port={config.port}, auth_type={config.auth_type}"
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
    description="Multi-tenant Netbird Event Streaming Service to Graylog",
    version="0.3.0",
    lifespan=lifespan,
)


def get_request_metadata(request: Request) -> Dict[str, str]:
    """Extract request metadata for logging and processing."""
    metadata = {
        "method": request.method,
        "path": str(request.url.path),
        "query": str(request.url.query) if request.url.query else "",
    }
    
    # Add request ID if present
    request_id = request.headers.get("x-request-id") or request.headers.get("traceparent")
    if request_id:
        metadata["request_id"] = request_id
    
    # Add proxy headers if trusted
    if config.trust_proxy_headers:
        if forwarded_for := request.headers.get("x-forwarded-for"):
            metadata["client_ip"] = forwarded_for.split(",")[0].strip()
        if forwarded_proto := request.headers.get("x-forwarded-proto"):
            metadata["protocol"] = forwarded_proto
            
    return metadata


def extract_tenant_from_path(path: str) -> Optional[str]:
    """
    Extract tenant from path if it matches the tenant pattern.
    
    Args:
        path: Request path
        
    Returns:
        Tenant name if found and valid, None otherwise
    """
    if not config.require_tenant_path:
        return None
        
    # Match pattern: /tenant/events
    match = re.match(r"^/([^/]+)/events/?$", path)
    if not match:
        return None
        
    tenant = match.group(1).lower()
    
    # Validate tenant format
    if not config.validate_tenant_format(tenant):
        return None
        
    return tenant


def log_with_context(level: str, message: str, tenant: Optional[str] = None, 
                    metadata: Optional[Dict] = None):
    """Log with tenant and request context."""
    log_data = {"message": message}
    
    if tenant:
        log_data["tenant"] = tenant
        
    if metadata:
        log_data.update(metadata)
    
    log_method = getattr(logger, level.lower())
    log_method(f"{message} | Context: {log_data}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    tenant_list = config.get_tenant_list()
    return {
        "status": "healthy",
        "service": "nb_streamer",
        "version": "0.3.0",
        "multi_tenancy": config.require_tenant_path,
        "tenants_count": len(tenant_list),
        
    }


@app.get("/tenants")
async def list_tenants():
    """List allowed tenants (if enabled)."""
    if not config.expose_tenants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant listing not enabled"
        )
    
    tenant_list = config.get_tenant_list()
    return {"tenants": tenant_list}


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


@app.post("/{tenant}/events")
async def receive_tenant_events(tenant: str, request: Request, response: Response):
    """
    Receive Netbird events for a specific tenant via path-based routing.
    
    This is the new multi-tenant endpoint: POST /{tenant}/events
    """
    metadata = get_request_metadata(request)
    
    try:
        # Normalize tenant to lowercase
        tenant = tenant.lower()
        
        # Validate tenant format
        if not config.validate_tenant_format(tenant):
            error_detail = {
                "code": "INVALID_TENANT_FORMAT",
                "message": f"Tenant '{tenant}' has invalid format",
                "details": {
                    "provided_tenant": tenant,
                    "required_pattern": "^[a-z0-9-]{1,32}$"
                }
            }
            log_with_context("warning", f"Invalid tenant format: {tenant}", tenant, metadata)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        
        # Check if tenant is allowed
        if not config.is_tenant_allowed(tenant):
            error_detail = {
                "code": "INVALID_TENANT",
                "message": f"Tenant '{tenant}' is not allowed",
                "details": {
                    "allowed_tenants": config.get_tenant_list(),
                    "provided_tenant": tenant
                }
            }
            log_with_context("warning", f"Unknown tenant: {tenant}", tenant, metadata)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail
            )

        # Authenticate request
        await auth_service.authenticate(request)

        # Track received event
        event_stats.increment_received(tenant)

        # Parse JSON body
        try:
            event_data = await request.json()
        except Exception as e:
            log_with_context("error", f"Failed to parse JSON: {e}", tenant, metadata)
            event_stats.increment_failed(tenant)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_JSON",
                    "message": "Invalid JSON in request body",
                    "details": {"error": str(e)}
                }
            )

        # Validate tenant consistency if NB_Tenant is present
        if "NB_Tenant" in event_data:
            payload_tenant = event_data["NB_Tenant"].lower()
            if payload_tenant != tenant:
                error_detail = {
                    "code": "TENANT_MISMATCH",
                    "message": "Path tenant doesn't match payload NB_Tenant",
                    "details": {
                        "path_tenant": tenant,
                        "payload_tenant": payload_tenant
                    }
                }
                log_with_context("warning", f"Tenant mismatch: path={tenant}, payload={payload_tenant}", 
                                tenant, metadata)
                event_stats.increment_failed(tenant)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_detail
                )
        else:
            # Inject tenant into event data
            event_data["NB_Tenant"] = tenant

        # Validate basic event structure and log for discovery
        if not transformer_service.validate_event_structure(event_data):
            log_with_context("warning", "Event failed basic validation but will still process", 
                           tenant, metadata)

        # Transform event to GELF
        gelf_message = await transformer_service.transform_event(event_data, tenant)

        # Send to Graylog
        try:
            graylog_service.send_gelf_message(gelf_message)

            # Track successful forwarding
            level = str(getattr(gelf_message, "level", "unknown"))
            event_stats.increment_forwarded(tenant, level)

            log_with_context("info", f"Successfully forwarded event to Graylog", 
                           tenant, metadata)
        except Exception as e:
            log_with_context("error", f"Failed to send message to Graylog: {e}", 
                           tenant, metadata)
            event_stats.increment_failed(tenant)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GRAYLOG_UNREACHABLE",
                    "message": "Failed to forward event to Graylog",
                    "details": {"error": str(e)}
                }
            )

        # Add request ID to response if present
        if request_id := metadata.get("request_id"):
            response.headers["x-request-id"] = request_id

        # Return success response
        return {
            "status": "success",
            "message": "Event processed and forwarded to Graylog",
            "tenant_id": tenant,
        }

    except HTTPException:
        raise
    except Exception as e:
        log_with_context("error", f"Unexpected error processing event: {e}", 
                        tenant, metadata)
        event_stats.increment_failed(tenant)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Internal server error processing event",
                "details": {"error": str(e)}
            }
        )


@app.post("/events")
async def receive_events_legacy(request: Request, response: Response):
    """
    Legacy endpoint for backward compatibility.
    
    This endpoint accepts events with NB_Tenant in the payload.
    Deprecated in favor of path-based tenant routing.
    """
    metadata = get_request_metadata(request)
    
    # Check if legacy events are allowed
    if not config.allow_legacy_events:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "code": "LEGACY_ENDPOINT_DISABLED",
                "message": "Legacy endpoint disabled. Use POST /{tenant}/events",
                "details": {
                    "deprecated_endpoint": "/events",
                    "new_endpoint_pattern": "/{tenant}/events"
                }
            }
        )

    try:
        # Authenticate request
        await auth_service.authenticate(request)

        # Parse JSON body
        try:
            event_data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_JSON",
                    "message": "Invalid JSON in request body",
                    "details": {"error": str(e)}
                }
            )

        # Extract tenant from payload
        if "NB_Tenant" not in event_data:
            error_detail = {
                "code": "MISSING_TENANT",
                "message": "Legacy endpoint requires NB_Tenant in payload",
                "details": {
                    "missing_field": "NB_Tenant",
                    "migration_note": "Use POST /{tenant}/events for new implementations"
                }
            }
            logger.error(f"Legacy endpoint used without NB_Tenant field")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )

        tenant = event_data["NB_Tenant"].lower()
        
        # Validate tenant if enforcement is enabled
        if config.legacy_enforce_match:
            if not config.validate_tenant_format(tenant):
                error_detail = {
                    "code": "INVALID_TENANT_FORMAT",
                    "message": f"Tenant '{tenant}' has invalid format",
                    "details": {
                        "provided_tenant": tenant,
                        "required_pattern": "^[a-z0-9-]{1,32}$"
                    }
                }
                log_with_context("warning", f"Invalid tenant format in legacy call: {tenant}", 
                               tenant, metadata)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_detail
                )
                
            if not config.is_tenant_allowed(tenant):
                error_detail = {
                    "code": "INVALID_TENANT",
                    "message": f"Tenant '{tenant}' is not allowed",
                    "details": {
                        "allowed_tenants": config.get_tenant_list(),
                        "provided_tenant": tenant
                    }
                }
                log_with_context("warning", f"Unknown tenant in legacy call: {tenant}", 
                               tenant, metadata)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_detail
                )

        # Log deprecation warning
        log_with_context("warning", "LEGACY_ENDPOINT: Deprecated /events endpoint used", 
                        tenant, metadata)

        # Track received event
        event_stats.increment_received(tenant)

        # Validate basic event structure
        if not transformer_service.validate_event_structure(event_data):
            log_with_context("warning", "Event failed basic validation but will still process", 
                           tenant, metadata)

        # Transform event to GELF
        gelf_message = await transformer_service.transform_event(event_data, tenant)

        # Send to Graylog
        try:
            graylog_service.send_gelf_message(gelf_message)

            # Track successful forwarding
            level = str(getattr(gelf_message, "level", "unknown"))
            event_stats.increment_forwarded(tenant, level)

            log_with_context("info", f"Successfully forwarded legacy event to Graylog", 
                           tenant, metadata)
        except Exception as e:
            log_with_context("error", f"Failed to send legacy message to Graylog: {e}", 
                           tenant, metadata)
            event_stats.increment_failed(tenant)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GRAYLOG_UNREACHABLE", 
                    "message": "Failed to forward event to Graylog",
                    "details": {"error": str(e)}
                }
            )

        # Add deprecation warning to response
        response.headers["x-deprecation-warning"] = "Legacy endpoint. Use POST /{tenant}/events"
        
        # Add request ID to response if present
        if request_id := metadata.get("request_id"):
            response.headers["x-request-id"] = request_id

        # Return success response with deprecation notice
        return {
            "status": "success",
            "message": "Event processed and forwarded to Graylog",
            "tenant_id": tenant,
            "warning": "Legacy endpoint deprecated. Use POST /{tenant}/events"
        }

    except HTTPException:
        raise
    except Exception as e:
        log_with_context("error", f"Unexpected error processing legacy event: {e}", 
                        None, metadata)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Internal server error processing event",
                "details": {"error": str(e)}
            }
        )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with custom response."""
    tenant_list = config.get_tenant_list()
    
    available_endpoints = {
        "GET /health": "Health check",
        "GET /stats": "Get event processing statistics", 
        "POST /stats/reset": "Reset statistics (authenticated)"
    }
    
    if config.require_tenant_path and tenant_list:
        available_endpoints["POST /{tenant}/events"] = "Send events for specific tenant (authenticated)"
        available_endpoints["example"] = f"POST /{tenant_list[0]}/events"
        
    if config.allow_legacy_events:
        available_endpoints["POST /events"] = "Legacy event endpoint (deprecated, authenticated)"
        
    if config.expose_tenants:
        available_endpoints["GET /tenants"] = "List allowed tenants"
    
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "error": {
                "code": "ENDPOINT_NOT_FOUND",
                "message": "Endpoint not found",
                "details": {
                    "available_endpoints": available_endpoints,
                    "configured_tenants": tenant_list,
                    "multi_tenancy_enabled": config.require_tenant_path
                }
            }
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)
