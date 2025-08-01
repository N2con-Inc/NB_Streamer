# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **NB_Streamer** project - a production-ready HTTP service that receives streamed activity events from Netbird and forwards them to Graylog as GELF messages. The service uses a modular, service-oriented architecture and is designed for containerized deployment with comprehensive configuration management.

## Architecture

The project follows a modular service-oriented architecture:
- **HTTP Service**: FastAPI-based server with health checks and event processing endpoints
- **Configuration Management**: Pydantic-based configuration with `NB_` prefixed environment variables
- **Authentication Service**: Multi-method authentication (none, bearer, basic, header)
- **Event Processing Pipeline**: Flexible Netbird event parsing → GELF transformation → Graylog delivery
- **Development Environment**: Full Docker Compose stack with Graylog, MongoDB, and Elasticsearch

### Key Components

- `src/main.py` - Main FastAPI application with lifespan management
- `src/config.py` - Comprehensive Pydantic configuration management
- `src/services/auth.py` - Authentication service with timing-attack protection
- `src/services/transformer.py` - Event transformation service with field discovery
- `src/services/graylog.py` - Graylog communication service (UDP/TCP)
- `src/models/netbird.py` - Flexible Netbird event models for unknown structures
- `src/models/gelf.py` - GELF message models with automatic field prefixing
- `tests/` - Structured testing (unit, integration, e2e) using pytest
- `docker-compose.yml` - Development environment with full Graylog stack

### Data Flow

1. Netbird POSTs JSON events to `/events` endpoint
2. Service authenticates request using configured method
3. Parse JSON with flexible field discovery and validation
4. Transform to GELF format with automatic `_NB_` prefixed fields and tenant support
5. Compress and send via UDP/TCP to Graylog
6. Return success/error response to Netbird

## Configuration

All configuration is done via `NB_` prefixed environment variables:
- `NB_HOST`: Service bind address (default: 0.0.0.0)
- `NB_PORT`: Internal listen port (default: 8000)
- `NB_DEBUG`: Debug mode flag (default: false)
- `NB_GRAYLOG_HOST`: Graylog server hostname/IP (required)
- `NB_GRAYLOG_PORT`: Graylog port (default: 12201)
- `NB_GRAYLOG_PROTOCOL`: Transport protocol (udp|tcp, default: udp)
- `NB_TENANT_ID`: Unique tenant identifier (required)
- `NB_AUTH_TYPE`: Authentication method (none|bearer|basic|header, default: none)
- `NB_AUTH_TOKEN`: Bearer token for authentication
- `NB_AUTH_USERNAME`: Username for basic authentication
- `NB_AUTH_PASSWORD`: Password for basic authentication
- `NB_AUTH_HEADER_NAME`: Custom header name for header auth
- `NB_AUTH_HEADER_VALUE`: Custom header value for header auth
- `NB_COMPRESSION_ENABLED`: GELF message compression (default: true)
- `NB_MAX_MESSAGE_SIZE`: Maximum message size (default: 8192)
- `NB_LOG_LEVEL`: Logging level (DEBUG|INFO|WARNING|ERROR, default: INFO)

## Common Development Tasks

### Development Environment Setup
```bash
# Set up development environment with full Graylog stack
docker-compose up -d

# This starts:
# - NB_Streamer service on port 8080
# - JupyterLab on port 8888 
# - Graylog web interface on port 9000
# - Full logging infrastructure (MongoDB, Elasticsearch)
```

### Building and Running with Docker
```bash
# Production container build
docker build -t nb-streamer .

# Development environment (recommended)
docker-compose up -d

# Production deployment (requires configuration)
docker run -p 8080:8080 --env-file .env nb-streamer
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only

# Coverage reporting
pytest --cov=src --cov-report=html
```

### Development Server
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
python -m src.main

# Or with uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Performance Requirements

- Handle up to 100 events/second with low latency processing
- Process each event within 100ms end-to-end
- Stateless design supporting horizontal scaling
- Graceful error handling with fallback processing for malformed events
- TCP connection pooling for high-throughput scenarios

## Security Considerations

- Run as non-root user (appuser:1000) in Docker container
- Comprehensive authentication service with timing-attack protection
- All secrets via environment variables with Pydantic validation
- Input validation with flexible field discovery for unknown structures
- Optional compression to reduce network exposure

## GELF Transformation Details

The service uses sophisticated GELF transformation with these features:
- **Version**: "1.1" (GELF specification compliance)
- **Host**: Multi-tenant host identification (`nb_streamer_{tenant_id}`)
- **Messages**: Automatic short/full message generation from event data
- **Timestamps**: Flexible timestamp parsing (ISO, Unix, datetime objects)
- **Levels**: String-to-syslog level mapping with fallback
- **Custom Fields**: Automatic `_NB_` prefixed fields with tenant injection
- **Field Discovery**: Unknown JSON structures automatically processed
- **Fallback Processing**: Malformed events still forwarded with error metadata

### Multi-Tenant Support

Each service instance supports tenant isolation:
- `_NB_tenant` field automatically added to all GELF messages
- Host field includes tenant ID for source identification
- Configuration per tenant via environment variables

### Field Processing Examples

```json
# Input Netbird Event
{"type": "peer_login", "user": "john@example.com", "timestamp": "2025-07-31T10:00:00Z"}

# Output GELF Message
{
  "version": "1.1",
  "host": "nb_streamer_tenant_123",
  "short_message": "Netbird peer_login by john@example.com",
  "timestamp": 1756627200,
  "level": 6,
  "_NB_tenant": "tenant_123",
  "_NB_type": "peer_login",
  "_NB_user": "john@example.com",
  "_NB_timestamp": "2025-07-31T10:00:00Z"
}
```