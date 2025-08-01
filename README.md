# NB_Streamer

**🚀 Lightweight Netbird-to-Graylog Event Streaming Service**

Stream Netbird VPN events directly to your existing Graylog infrastructure with multi-tenant support, flexible authentication, and automatic GELF transformation.

[![Production Ready](https://img.shields.io/badge/status-production%20ready-green)](docs/PHASE1_COMPLETE.md)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](Dockerfile)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)

## ⚡ Quick Start

### 1️⃣ Clone and Configure
```bash
git clone https://github.com/yourusername/NB_Streamer.git
cd NB_Streamer

# Copy configuration template
cp .env.example .env

# Edit configuration (set your Graylog host and tenant ID)
nano .env
```

### 2️⃣ Deploy with Docker
```bash
# Simple deployment (connects to your existing Graylog)
docker-compose up -d
```

### 3️⃣ Test Your Deployment
```bash
# Health check
curl http://localhost:8000/health

# Send test event
cd examples/
./curl-test.sh
```

### 4️⃣ Configure Netbird
Point Netbird webhook to: `http://your-server:8000/events`

**That's it!** Your Netbird events are now flowing to Graylog with multi-tenant support. 🎉

---

## 📋 What It Does

- **Receives**: Netbird activity events via HTTP POST
- **Transforms**: JSON events → GELF format with `_NB_` prefixes  
- **Forwards**: Events to your existing Graylog infrastructure via UDP/TCP
- **Supports**: Multi-tenancy, multiple auth methods, field discovery

**Prerequisites**: Requires an existing Graylog server with GELF input configured (typically UDP port 12201)

## 🏗️ Architecture

```
Netbird → NB_Streamer → Graylog
   │           │           │
   │           ├─ Authentication
   │           ├─ GELF Transformation
   │           ├─ Multi-tenant Support
   │           └─ Field Discovery
   │
   └── HTTP POST /events
```

### Event Transformation Example

**Input (Netbird):**
```json
{
  "type": "peer_login",
  "user": "john@example.com",
  "timestamp": "2025-01-30T12:00:00Z"
}
```

**Output (GELF to Graylog):**
```json
{
  "version": "0.2.5",
  "host": "nb_streamer_tenant_123",
  "short_message": "Netbird peer_login by john@example.com",
  "_NB_tenant": "tenant_123",
  "_NB_type": "peer_login",
  "_NB_user": "john@example.com"
}
```

## ⚙️ Configuration

### Required Settings
```bash
# .env file
NB_GRAYLOG_HOST=your-graylog-server.com  # Your Graylog server
NB_TENANT_ID=your-unique-tenant-id       # Multi-tenant identifier
```

### Optional Settings
```bash
# Authentication (default: none)
NB_AUTH_TYPE=bearer                    # none|bearer|basic|header
NB_AUTH_TOKEN=your-secure-token       # For bearer/basic auth

# Service Configuration
NB_HOST=0.0.0.0                       # Bind address
NB_PORT=8000                          # Service port
NB_GRAYLOG_PORT=12201                 # GELF port
NB_GRAYLOG_PROTOCOL=udp               # udp|tcp
NB_LOG_LEVEL=INFO                     # DEBUG|INFO|WARNING|ERROR
```

See [.env.example](.env.example) for complete configuration options.

## 🐳 Deployment Options

### Docker (Recommended)
```bash
# Simple deployment - connects to your existing Graylog
cp .env.example .env  # Configure your Graylog server first
docker-compose up -d
```

### Development Environment  
```bash
# Development with auto-reload
cd dev/
docker-compose -f docker-compose.dev.yml up -d

# Access NB_Streamer: http://localhost:8000
```

### Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run service
python -m src.main
```

## 🧪 Testing

### Automated Testing
```bash
# Run test suite
pytest

# With coverage
pytest --cov=src --cov-report=html

# Development stack testing
python scripts/test_nb_streamer.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Send test event (see examples/)
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d @examples/test-event.json
```

## 📊 Monitoring

### Health Endpoint
```bash
GET /health
{
  "status": "healthy",
  "service": "nb_streamer",
  "version": "0.2.5",
  "tenant_id": "your-tenant-id"
}
```

### Logs
```bash
# Docker logs
docker logs nb-streamer-prod

# Look for field discovery
grep "Event contains known fields" logs/
```

### Graylog Integration
- Events appear with `_NB_tenant` field for filtering
- All Netbird fields prefixed with `_NB_`
- Automatic field discovery logs unknown structures

## 🔐 Authentication

Supports all Netbird authentication methods:

```bash
# No authentication (development)
NB_AUTH_TYPE=none

# Bearer token
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=your-secure-token

# Basic authentication  
NB_AUTH_TYPE=basic
NB_AUTH_USERNAME=username
NB_AUTH_PASSWORD=password

# Custom header
NB_AUTH_TYPE=header
NB_AUTH_HEADER_NAME=X-API-Key
NB_AUTH_HEADER_VALUE=secret-value
```

## 📚 Documentation

- **[Quick Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Development Setup](docs/DEVELOPMENT.md)** - Local development environment
- **[Architecture](ARCHITECTURE.md)** - System design and data flow
- **[Contributing](CONTRIBUTING.md)** - Development workflow and standards
- **[Examples](examples/)** - Test scripts and sample events

## 🔄 Multi-Tenant Support

Each NB_Streamer instance supports a single tenant but multiple tenants can be deployed:

```bash
# Tenant A
NB_TENANT_ID=company_a
NB_PORT=8000

# Tenant B  
NB_TENANT_ID=company_b
NB_PORT=8001
```

Graylog messages include `_NB_tenant` field for filtering and dashboards.

## 🚀 Performance

- **Throughput**: 100+ events/second
- **Latency**: <100ms per event
- **Resource Usage**: ~100MB RAM
- **Scaling**: Stateless design supports horizontal scaling

## 🛟 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check configuration
docker logs nb-streamer-prod

# Test configuration
python -c "from src.config import config; print('Config OK')"
```

**Events not reaching Graylog:**
```bash
# Test connectivity to your Graylog server
nc -u your-graylog-host 12201

# Verify Graylog GELF input is configured and running
# Check network connectivity and firewall rules
# Ensure Graylog server accepts GELF UDP on port 12201
```

**Field discovery:**
```bash
# Enable debug logging
NB_LOG_LEVEL=DEBUG

# Check logs for field discovery
grep "All event fields" logs/nb_streamer.log
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📞 Support

- **Documentation**: [docs/](docs/) directory
- **Examples**: [examples/](examples/) directory  
- **Issues**: [GitHub Issues](https://github.com/yourusername/NB_Streamer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/NB_Streamer/discussions)

---

**Built for production** • **Multi-tenant ready** • **Easy deployment** • **Comprehensive monitoring**