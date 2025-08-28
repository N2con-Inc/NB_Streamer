# NB_Streamer API Documentation

## Overview

NB_Streamer provides HTTP endpoints for ingesting Netbird events and forwarding them to Graylog via GELF protocol. Version 0.3.0 introduces multi-tenancy support with path-based tenant identification.

## Endpoints

### Multi-tenant Event Ingestion

**Path-based tenant endpoints (v0.3.0+)**

```
POST /{tenant}/events
```

**Parameters:**
- `tenant` (path parameter): Tenant identifier matching `^[a-z0-9-]{1,32}$` pattern
- Must be in the configured allow-list (`NB_TENANTS`)

**Request Headers:**
- `Content-Type: application/json` (required)
- `Authorization: Bearer <token>` (if `NB_AUTH_TYPE=bearer`)
- `X-Request-ID` (optional): Request correlation ID

**Request Body:**
- JSON object containing Netbird event data
- `NB_Tenant` field (optional): If present, must match the path `{tenant}` parameter
- If `NB_Tenant` is missing, it will be automatically injected with the path tenant value

**Response:**
- `200 OK`: Event successfully processed and forwarded to Graylog
- `400 Bad Request`: Invalid JSON, tenant mismatch, or validation error
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Unknown tenant or invalid path format
- `422 Unprocessable Entity`: Event structure validation failed
- `502 Bad Gateway`: Failed to forward to Graylog

**Example:**

```bash
# Valid request
curl -X POST https://streamer.example.com/n2con/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "type": "peer_login",
    "user": "john@example.com",
    "timestamp": "2025-08-28T18:00:00Z",
    "peer_id": "abc123"
  }'

# Response
{
  "status": "success",
  "message": "Event processed and forwarded to Graylog",
  "tenant_id": "n2con"
}
```

### Legacy Event Ingestion (Backward Compatibility)

**Legacy endpoint (deprecated)**

```
POST /events
```

**Configuration:**
- Controlled by `NB_ALLOW_LEGACY_EVENTS` (default: `true`)
- Strict tenant validation controlled by `NB_LEGACY_ENFORCE_MATCH` (default: `true`)

**Request Body Requirements:**
- Must include `NB_Tenant` field in JSON payload
- If `NB_LEGACY_ENFORCE_MATCH=true`, tenant must be in the allow-list

**Deprecation Behavior:**
- Logs warning with code `LEGACY_ENDPOINT` 
- Includes deprecation notice in response headers
- Will be removed in a future version

**Example:**

```bash
# Legacy request (deprecated)
curl -X POST https://streamer.example.com/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "type": "peer_login",
    "user": "john@example.com",
    "NB_Tenant": "n2con"
  }'

# Response includes deprecation warning
{
  "status": "success",
  "message": "Event processed and forwarded to Graylog",
  "tenant_id": "n2con",
  "warning": "Legacy endpoint deprecated. Use POST /{tenant}/events"
}
```

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "nb_streamer",
  "version": "0.3.0",
  "tenant_id": "n2con"
}
```

### Statistics

```
GET /stats
```

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "events_received": 1250,
    "events_forwarded": 1248,
    "events_failed": 2,
    "tenants": {
      "n2con": {
        "received": 800,
        "forwarded": 799,
        "failed": 1
      },
      "acme": {
        "received": 450,
        "forwarded": 449,
        "failed": 1
      }
    }
  }
}
```

### Tenant Listing (Optional)

```
GET /tenants
```

**Configuration:**
- Only available if `NB_EXPOSE_TENANTS=true` (default: `false`)

**Response:**
```json
{
  "tenants": ["n2con", "acme", "demo"]
}
```

## Authentication

Multiple authentication methods are supported via `NB_AUTH_TYPE`:

### None (Development)
```bash
NB_AUTH_TYPE=none
```
No authentication required.

### Bearer Token
```bash
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=your-secure-token
```

**Request:**
```bash
Authorization: Bearer your-secure-token
```

### Basic Authentication
```bash
NB_AUTH_TYPE=basic
NB_AUTH_USERNAME=username
NB_AUTH_PASSWORD=password
```

**Request:**
```bash
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

### Custom Header
```bash
NB_AUTH_TYPE=header
NB_AUTH_HEADER_NAME=X-API-Key
NB_AUTH_HEADER_VALUE=secret-value
```

**Request:**
```bash
X-API-Key: secret-value
```

## Tenant Configuration

### Environment Variables

- `NB_TENANTS`: Comma-separated list of allowed tenants (required)
- `NB_TENANTS_FILE`: Optional path to JSON file containing tenant list
- `NB_REQUIRE_TENANT_PATH`: Enable path-based tenant requirement (default: `true`)
- `NB_ALLOW_LEGACY_EVENTS`: Enable legacy `/events` endpoint (default: `true`)
- `NB_LEGACY_ENFORCE_MATCH`: Enforce tenant validation on legacy endpoint (default: `true`)

### Tenant Validation

Tenants must match the pattern: `^[a-z0-9-]{1,32}$`

**Valid examples:**
- `n2con`
- `acme-corp`
- `client-123`
- `demo`

**Invalid examples:**
- `N2CON` (uppercase)
- `client_name` (underscore)
- `very-long-tenant-name-exceeding-32-chars`

### Configuration File (Optional)

If `NB_TENANTS_FILE` is set, the file should contain:

```json
{
  "tenants": ["n2con", "acme", "demo"]
}
```

When both environment and file are present, tenants are merged (union).

## Error Handling

### Standard Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_TENANT",
    "message": "Tenant 'unknown' is not allowed",
    "details": {
      "allowed_tenants": ["n2con", "acme"],
      "provided_tenant": "unknown"
    }
  }
}
```

### Error Codes

- `INVALID_TENANT`: Tenant not in allow-list or invalid format
- `TENANT_MISMATCH`: Path tenant doesn't match payload `NB_Tenant`
- `MISSING_TENANT`: Legacy endpoint used without `NB_Tenant` in payload
- `INVALID_JSON`: Request body is not valid JSON
- `AUTHENTICATION_FAILED`: Invalid or missing authentication
- `GRAYLOG_UNREACHABLE`: Cannot forward event to Graylog
- `VALIDATION_FAILED`: Event data failed validation

## Request/Response Headers

### Request Headers

- `Content-Type: application/json` (required for event endpoints)
- `Authorization: Bearer <token>` (if authentication enabled)
- `X-Request-ID: <correlation-id>` (optional, propagated to logs)
- `X-Forwarded-For: <client-ip>` (honored if `NB_TRUST_PROXY_HEADERS=true`)
- `X-Forwarded-Proto: <protocol>` (honored if `NB_TRUST_PROXY_HEADERS=true`)

### Response Headers

- `Content-Type: application/json`
- `X-Request-ID: <correlation-id>` (if provided in request)
- `X-Deprecation-Warning: Legacy endpoint` (for `/events` endpoint)

## Event Processing

### GELF Transformation

Events are transformed to GELF format with the following enhancements:

1. **Tenant Tagging**: `_NB_tenant` field added with tenant identifier
2. **Field Prefixing**: All Netbird fields prefixed with `_NB_`
3. **Host Identification**: GELF `host` field set to `nb_streamer_{tenant}`
4. **Timestamp Normalization**: Converts ISO timestamps to Unix epoch
5. **Level Mapping**: Maps Netbird levels to syslog levels

### Example Transformation

**Input (Netbird):**
```json
{
  "type": "peer_login",
  "user": "john@example.com",
  "timestamp": "2025-08-28T18:00:00Z"
}
```

**Output (GELF to Graylog):**
```json
{
  "version": "1.1",
  "host": "nb_streamer_n2con",
  "short_message": "Netbird peer_login by john@example.com",
  "timestamp": 1756665600.0,
  "level": 6,
  "_NB_tenant": "n2con",
  "_NB_type": "peer_login",
  "_NB_user": "john@example.com",
  "_NB_timestamp": "2025-08-28T18:00:00Z"
}
```

## Rate Limiting and Performance

- **Throughput**: Designed for 100+ events/second per tenant
- **Latency**: Target <100ms per event processing
- **Resource Usage**: ~100MB RAM baseline + per-tenant overhead
- **Scaling**: Stateless design supports horizontal scaling

No built-in rate limiting is provided. Use external reverse proxy (nginx, Traefik) for rate limiting if needed.

## Migration Guide

See [MIGRATION-0.3.0.md](MIGRATION-0.3.0.md) for detailed upgrade instructions from single-tenant to multi-tenant architecture.

---

**Version**: 0.3.0  
**Last Updated**: 2025-08-28
