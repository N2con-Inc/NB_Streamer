# Current NB_Streamer Deployment Documentation
**Generated:** 2024-08-28  
**Location:** `/mass/application/NB_Streamer`  
**Status:** Development/Testing Environment

## Current Running Configuration

### Container Status
- **Container Name:** `nb-streamer-mt`
- **Image:** `nb-streamer:0.3.0`
- **Status:** Restarting (due to config import issue)
- **Issue:** ImportError: cannot import name 'config' from 'src.config'

### Environment Configuration (.env)
```bash
# NB_Streamer Configuration - PRODUCTION DEPLOYMENT v0.3.1
# Multi-tenant only (legacy support removed)

# Server Configuration
NB_HOST=0.0.0.0
NB_PORT=8000
NB_DEBUG=false

# Graylog Configuration
NB_GRAYLOG_HOST=10.0.1.244
NB_GRAYLOG_PORT=12201
NB_GRAYLOG_PROTOCOL=udp

# MULTI-TENANCY CONFIGURATION
# Comma-separated list of allowed tenants
NB_TENANTS=n2con

# Legacy Support: DISABLED in v0.3.1
NB_ALLOW_LEGACY_EVENTS=false

# Authentication Configuration
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=NB_STREAMER_FEqa6rCRAMQoEzunR_B9l9APd2S3wRuJylSXyA8r7DI

# Message Configuration
NB_COMPRESSION_ENABLED=true
NB_MAX_MESSAGE_SIZE=8192

# Logging Configuration
NB_LOG_LEVEL=INFO

# Reverse Proxy Configuration
NB_TRUST_PROXY_HEADERS=true

# Optional features
NB_EXPOSE_TENANTS=false

# Current Production Endpoints:
# POST /n2con/events - Active tenant-specific endpoint
# POST /events - DISABLED (legacy removed)
```

### Configuration Analysis
- **Tenant:** n2con (single tenant setup)
- **Authentication:** Bearer token authentication enabled
- **Graylog Integration:** Configured for 10.0.1.244:12201
- **Port Configuration:** 8001 (external) -> 8080 (internal)

### Historical Environment Files
- `.env.0-3-0`: Configuration snapshot from v0.3.0 upgrade
- `.env.pre-multitenancy-backup`: Pre-multi-tenancy configuration
- `.env.sample`: Sample configuration file

### Issues Identified
1. **Config Import Error**: Current container fails to start due to missing config instance
2. **Old Image Version**: Using 0.3.0 instead of latest 0.3.1
3. **Port Inconsistency**: Some references to 8000 instead of 8080

### Docker Compose Setup
The current deployment appears to use a custom docker-compose or docker run command, as there's no active docker-compose.yml deployment visible.

## Recommended Actions
1. Stop current failing deployment
2. Set up production deployment in separate directory
3. Use latest pre-built images from GitHub Container Registry
4. Apply fixed configuration with proper multi-tenancy setup

---
*This documentation captures the state before migrating to production deployment setup*
