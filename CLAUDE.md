# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Netbird Event Streaming Receiver** project - a lightweight HTTP service that receives streamed activity events from Netbird and forwards them to Graylog as GELF messages. The service is designed to be containerized and run behind a reverse proxy for TLS termination.

## Architecture

The project follows a simple architecture:
- **HTTP Service**: FastAPI-based server listening on port 8080 (internal)
- **Authentication Layer**: Configurable auth (None, Bearer Token, Basic Auth, Custom Header)
- **Event Processing**: Transform Netbird JSON events to GELF format with `NB_` prefixed fields
- **GELF Output**: Send compressed UDP datagrams to Graylog (default port 12201)
- **Setup Script**: Interactive Python script to generate `docker-compose.yml`

### Key Components

- `app/main.py` - Main FastAPI application with `/events` endpoint
- `app/gelf.py` - GELF transformation logic (Netbird → GELF with NB_ prefixes)
- `setup.py` - Interactive setup script for deployment configuration
- `tests/` - Unit and integration tests using pytest
- `Dockerfile` - Container definition using python:3.10-slim base

### Data Flow

1. Netbird POSTs JSON events to `/events` endpoint
2. Service authenticates request (if enabled)
3. Parse and validate JSON structure
4. Transform to GELF format with custom `NB_` prefixed fields:
   - `NB_ID`, `NB_TIMESTAMP`, `NB_MESSAGE`, `NB_INITIATOR_ID`, `NB_TARGET_ID`, `NB_META`, `NB_REFERENCE`
5. Compress and send via UDP to Graylog
6. Return HTTP response to Netbird

## Configuration

All configuration is done via environment variables:
- `PORT`: Internal listen port (default: 8080)
- `AUTH_TYPE`: Authentication method (none|bearer|basic|custom)
- `AUTH_SECRET`: Token/password for authentication
- `AUTH_CUSTOM_HEADER`: Custom header name for auth
- `GRAYLOG_HOST`: Graylog server hostname/IP
- `GRAYLOG_PORT`: Graylog port (default: 12201)
- `GRAYLOG_PROTOCOL`: Transport protocol (udp|tcp, default: udp)
- `DEFAULT_HOST`: Fallback GELF host field (default: netbird-streamer)

## Common Development Tasks

### Running the Setup Script
```bash
python setup.py
```
The setup script interactively prompts for configuration and generates a `docker-compose.yml` file.

### Building and Running with Docker
```bash
# Build the image
docker build -t netbird-receiver .

# Run with docker-compose (after setup script)
docker-compose up -d
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Integration tests with mock UDP
pytest tests/test_integration.py
```

### Development Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Performance Requirements

- Handle up to 100 events/second
- Process each event within 100ms
- Stateless design for horizontal scaling
- Graceful error handling (don't crash on invalid JSON or Graylog failures)

## Security Considerations

- Run as non-root user in Docker container
- Support multiple authentication methods for Netbird integration
- No hardcoded secrets (all via environment variables)
- Input validation for all received JSON events

## GELF Transformation Details

The service transforms Netbird events to GELF format with these mappings:
- `version`: "1.1" (fixed)
- `host`: Use `InitiatorID` or configured default
- `short_message`: Netbird's `Message` field
- `timestamp`: Convert Netbird's `Timestamp` to Unix timestamp
- `level`: Default to 6 (INFO)
- `full_message`: Concatenated message + Meta details
- Custom fields: All Netbird fields prefixed with `NB_` (e.g., `NB_ID`, `NB_INITIATOR_ID`)

Note: The `NB_` prefix format intentionally omits leading underscores to match project requirements, though GELF best practices recommend underscores for additional fields.