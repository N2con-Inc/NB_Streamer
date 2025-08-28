# Running Configuration Checkpoint - 2025-08-28

## Overview
This document captures the current running configuration of NB_Streamer before implementing multi-tenancy features (v0.3.0).

## Version Information
- **Current Version**: 0.2.6
- **Commit SHA**: f405e35eebb7ecb5db53994b78a0c090a51fc168
- **Git Tags**: 
  - `pre-mt-20250828-112424` (checkpoint)
  - `v0.2.6-running-config` (versioned checkpoint)
- **Date**: 2025-08-28T18:24:24Z

## Environment Configuration
Current `.env` configuration highlights (secrets redacted):

```bash
# Server Configuration
NB_HOST=0.0.0.0
NB_PORT=8000
NB_DEBUG=false

# Graylog Configuration
NB_GRAYLOG_HOST=10.0.1.244
NB_GRAYLOG_PORT=12201
NB_GRAYLOG_PROTOCOL=udp

# Tenant Configuration - Single tenant mode
NB_TENANT_ID=n2con

# Authentication
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=[REDACTED]

# Message Configuration
NB_COMPRESSION_ENABLED=true
NB_MAX_MESSAGE_SIZE=8192
NB_LOG_LEVEL=DEBUG
```

## Current Endpoints
- **Event Ingestion**: `POST /events`
  - Requires bearer token authentication
  - Accepts Netbird event JSON payload
  - Tags events with `_NB_tenant: "n2con"`
  - Forwards to Graylog via GELF UDP

- **Health Check**: `GET /health`
  - Returns service status and version info

- **Statistics**: `GET /stats` and `POST /stats/reset`
  - Event processing metrics

## Deployment Configuration
- **Compose File**: `docker-compose.yml`
- **Exposed Ports**: 8000 (mapped from container port 8000)
- **Container Name**: `nb-streamer`
- **Base Image**: Python 3.10+ FastAPI application

## Current Architecture
- **Single Tenant Mode**: All events tagged with `n2con`
- **Authentication**: Bearer token required
- **Event Flow**: Netbird → NB_Streamer → Graylog
- **Protocol**: HTTP POST → GELF UDP

## Known Clients
- Events currently tagged with `NB_Tenant: "n2con"`
- Clients using endpoint: `POST /events`
- All events forwarded to Graylog at `10.0.1.244:12201`

## Notes
This configuration represents a stable, production-ready single-tenant deployment. The upcoming multi-tenancy implementation (v0.3.0) will maintain backward compatibility through configurable legacy endpoint support.

---
*Checkpoint created before multi-tenancy implementation - Phase 0 complete*
