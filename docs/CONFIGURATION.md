# Configuration Guide

Complete configuration reference for NB_Streamer multi-tenant event streaming service.

## 🚀 Quick Setup

```bash
# Copy the example
cp .env.example .env

# Edit with your settings
nano .env
```

## 📋 Required Configuration

### Multi-tenancy
```bash
# Comma-separated list of allowed tenants
NB_TENANTS=tenant1,tenant2,tenant3
```

### Graylog Connection
```bash
# Graylog server details
NB_GRAYLOG_HOST=your-graylog-server.com
NB_GRAYLOG_PORT=12201
NB_GRAYLOG_PROTOCOL=udp
```

### Authentication
```bash
# Choose your authentication method
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=your-secure-token-here
```

## 🔧 Complete Configuration Reference

### Server Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NB_HOST` | `0.0.0.0` | Server bind address |
| `NB_PORT` | `8080` | Server port |
| `NB_DEBUG` | `false` | Enable debug mode |
| `NB_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Multi-tenancy Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NB_TENANTS` | `""` | **Required** - Comma-separated tenant list |
| `NB_TENANTS_FILE` | `null` | Optional file containing tenant list |
| `NB_EXPOSE_TENANTS` | `false` | Include tenant list in `/info` endpoint |

### Graylog Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NB_GRAYLOG_HOST` | `localhost` | **Required** - Graylog server hostname |
| `NB_GRAYLOG_PORT` | `12201` | Graylog GELF input port |
| `NB_GRAYLOG_PROTOCOL` | `udp` | Protocol (tcp, udp) |
| `NB_GRAYLOG_TIMEOUT` | `10` | Connection timeout in seconds |

### Authentication Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NB_AUTH_TYPE` | `none` | Authentication type (none, bearer, basic, header) |
| `NB_AUTH_TOKEN` | `null` | Bearer token (required if auth_type=bearer) |
| `NB_AUTH_USERNAME` | `null` | Basic auth username |
| `NB_AUTH_PASSWORD` | `null` | Basic auth password |
| `NB_AUTH_HEADER_NAME` | `null` | Custom header name |
| `NB_AUTH_HEADER_VALUE` | `null` | Custom header value |

### Message Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NB_COMPRESSION_ENABLED` | `true` | Enable GELF compression |
| `NB_MAX_MESSAGE_SIZE` | `8192` | Maximum message size in bytes |

### Network Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NB_TRUST_PROXY_HEADERS` | `true` | Trust X-Forwarded-* headers |

## 🔐 Authentication Methods

### 1. Bearer Token (Recommended)
```bash
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=your-secure-bearer-token-here
```

**Usage:**
```bash
curl -H "Authorization: Bearer your-secure-bearer-token-here" \
  http://localhost:8080/tenant/events
```

### 2. Basic Authentication
```bash
NB_AUTH_TYPE=basic
NB_AUTH_USERNAME=your-username
NB_AUTH_PASSWORD=your-secure-password
```

**Usage:**
```bash
curl -u your-username:your-secure-password \
  http://localhost:8080/tenant/events
```

### 3. Custom Header
```bash
NB_AUTH_TYPE=header
NB_AUTH_HEADER_NAME=X-API-Key
NB_AUTH_HEADER_VALUE=your-api-key-value
```

**Usage:**
```bash
curl -H "X-API-Key: your-api-key-value" \
  http://localhost:8080/tenant/events
```

### 4. No Authentication
```bash
NB_AUTH_TYPE=none
```

⚠️ **Warning:** Only use for development or when authentication is handled by a reverse proxy.

## 🏢 Multi-tenant Setup

### Single Tenant
```bash
NB_TENANTS=mycompany
```
- Endpoint: `POST /mycompany/events`

### Multiple Tenants
```bash
NB_TENANTS=company1,company2,department-a
```
- Endpoints: 
  - `POST /company1/events`
  - `POST /company2/events`  
  - `POST /department-a/events`

### Tenant File (Advanced)
```bash
NB_TENANTS_FILE=/path/to/tenants.txt
```

**tenants.txt format:**
```
# Comments start with #
tenant1
tenant2
# Another comment
tenant3
```

## 🌐 Network & Proxy Configuration

### Behind Reverse Proxy
```bash
# Enable proxy header support
NB_TRUST_PROXY_HEADERS=true
```

This enables logging of real client IPs from headers:
- `X-Forwarded-For`
- `X-Real-IP`
- `X-Forwarded-Proto`

### Direct Internet Access
```bash
# Disable proxy headers for security
NB_TRUST_PROXY_HEADERS=false
```

## 📊 Logging Configuration

### Log Levels
```bash
# Development
NB_LOG_LEVEL=DEBUG

# Production
NB_LOG_LEVEL=INFO

# Quiet
NB_LOG_LEVEL=WARNING
```

### Debug Mode
```bash
# Enable debug features
NB_DEBUG=true
```

**Debug mode enables:**
- Detailed error messages
- API documentation endpoints (`/docs`, `/redoc`)
- Additional logging

## 🔧 Graylog Integration

### UDP Configuration (Default)
```bash
NB_GRAYLOG_HOST=graylog.example.com
NB_GRAYLOG_PORT=12201
NB_GRAYLOG_PROTOCOL=udp
NB_GRAYLOG_TIMEOUT=10
```

### TCP Configuration
```bash
NB_GRAYLOG_HOST=graylog.example.com
NB_GRAYLOG_PORT=12201
NB_GRAYLOG_PROTOCOL=tcp
NB_GRAYLOG_TIMEOUT=30
```

### Message Limits
```bash
# Adjust based on your Graylog setup
NB_MAX_MESSAGE_SIZE=16384  # 16KB
NB_COMPRESSION_ENABLED=true
```

## 📁 Configuration Files

### Environment File (.env)
```bash
# Place in project root
/path/to/NB_Streamer/.env
```

### Docker Environment
```bash
# Override in docker-compose.yml
environment:
  - NB_GRAYLOG_HOST=production-graylog
  - NB_LOG_LEVEL=WARNING
```

### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nb-streamer-config
data:
  NB_TENANTS: "prod-tenant1,prod-tenant2"
  NB_GRAYLOG_HOST: "graylog.production.svc.cluster.local"
  NB_LOG_LEVEL: "INFO"
```

## ✅ Configuration Validation

### Startup Validation
The service validates configuration on startup:

```bash
# Valid configuration
2025-08-28 18:58:07 - src.config - INFO - === NB_Streamer Configuration Summary ===
2025-08-28 18:58:07 - src.config - INFO - Multi-tenancy enabled: True
2025-08-28 18:58:07 - src.config - INFO - Configured tenants: ['tenant1', 'tenant2']

# Invalid configuration  
2025-08-28 18:58:07 - src.config - ERROR - No tenants configured. Please set NB_TENANTS environment variable.
```

### Health Check Validation
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "nb-streamer", 
  "version": "0.3.1",
  "tenants_configured": 2,
  "multi_tenant_mode": true
}
```

## 🔍 Troubleshooting

### Common Issues

**No tenants configured**
```bash
# Error: ValueError: At least one tenant must be configured
# Solution: Set NB_TENANTS
NB_TENANTS=mytenant
```

**Authentication failures**
```bash
# Error: 401 Authentication required
# Solution: Check auth configuration
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=valid-token
```

**Graylog connection issues**  
```bash
# Error: Connection refused
# Solution: Verify Graylog settings
NB_GRAYLOG_HOST=correct-hostname
NB_GRAYLOG_PORT=12201  # Check Graylog GELF input
```

### Configuration Test
```bash
# Test configuration
docker run --env-file .env your-registry/nb-streamer:latest \
  python -c "from src.config import Config; Config().validate_configuration()"
```

## 📋 Example Configurations

### Development Setup
```bash
# .env for development
NB_TENANTS=dev-tenant
NB_GRAYLOG_HOST=localhost
NB_AUTH_TYPE=none
NB_DEBUG=true
NB_LOG_LEVEL=DEBUG
```

### Production Setup
```bash
# .env for production
NB_TENANTS=prod1,prod2,staging
NB_GRAYLOG_HOST=graylog.production.com
NB_GRAYLOG_PROTOCOL=tcp
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=prod-secret-token-here
NB_LOG_LEVEL=INFO
NB_TRUST_PROXY_HEADERS=true
```

### High-Security Setup
```bash
# .env for high-security
NB_TENANTS=secure-tenant
NB_GRAYLOG_HOST=secure-graylog.internal
NB_AUTH_TYPE=header
NB_AUTH_HEADER_NAME=X-Internal-API-Key
NB_AUTH_HEADER_VALUE=internal-secret-key
NB_EXPOSE_TENANTS=false
NB_TRUST_PROXY_HEADERS=false
```

---

**Need help?** Check the [troubleshooting section](../README.md#-support) or refer to the [deployment guide](DEPLOYMENT.md).
