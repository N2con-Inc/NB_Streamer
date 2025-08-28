# NB_Streamer

**Multi-tenant Event Streaming Service** - A lightweight FastAPI service for securely forwarding events to Graylog with tenant isolation.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://github.com/users/USERNAME/packages/container/nb-streamer)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

## 🚀 Quick Start

### Using Pre-built Images (Recommended)

```bash
# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Deploy with registry images
./scripts/deploy.sh
```

Your service will be available at `http://localhost:8080`

### Manual Docker Build

```bash
# Build and run locally
docker compose up -d --build
```

## 📋 Features

- **🏢 Multi-tenant Architecture** - Isolated endpoints per tenant
- **🔐 Multiple Authentication Methods** - Bearer, Basic, Header, or None
- **⚡ High Performance** - FastAPI-based async processing
- **🐳 Container Ready** - Optimized Docker images with health checks
- **📊 Observability** - Structured logging with tenant context
- **🔄 CI/CD Integration** - Automated builds and deployments
- **🛡️ Security Focused** - Tenant validation and request sanitization

## 🏗️ Architecture

```
Client Apps → [Reverse Proxy] → NB_Streamer → Graylog
    ↓              ↓                ↓           ↓
Per-tenant     Load balance    Multi-tenant   Centralized
endpoints      & SSL           validation     logging
```

### Multi-tenant Endpoints

- **New Format**: `POST /{tenant}/events` (e.g., `POST /n2con/events`)
- **Legacy Format**: `POST /events` (disabled in v0.3.1)

## 📖 Documentation

- **[📚 Complete Documentation](docs/)** - All guides in one place
- **[🚀 Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[🐳 Container Registry Setup](docs/CONTAINER_REGISTRY.md)** - Using pre-built images
- **[🔧 Development Guide](docs/DEVELOPMENT.md)** - Local development setup
- **[📊 API Documentation](docs/API.md)** - API reference and examples

## ⚙️ Configuration

### Environment Variables

```bash
# Required
NB_TENANTS=tenant1,tenant2,tenant3
NB_GRAYLOG_HOST=your-graylog-server
NB_AUTH_TOKEN=your-secure-token

# Optional
NB_PORT=8080
NB_LOG_LEVEL=INFO
NB_EXPOSE_TENANTS=false
```

See `.env.example` for complete configuration options.

## 🏃‍♂️ Usage Examples

### Send Event to Tenant-specific Endpoint

```bash
curl -X POST http://localhost:8080/n2con/events \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "user_login",
    "timestamp": "2025-08-28T12:00:00Z",
    "user": "john.doe",
    "message": "User logged in successfully"
  }'
```

### Health Check

```bash
curl http://localhost:8080/health
```

### Service Information

```bash
curl http://localhost:8080/info
```

## 🚢 Deployment Options

### 1. Registry-based Deployment (Recommended)

```bash
# Quick deploy with pre-built images
./scripts/deploy.sh

# Deploy specific version
IMAGE_TAG=0.3.1 ./scripts/deploy.sh
```

### 2. External Reverse Proxy

```bash
# For use behind nginx/traefik/cloudflare
docker compose -f docker-compose.external-proxy.yml up -d
```

### 3. Local Development

```bash
# Build and run locally
docker compose up -d --build
```

## 🔧 Development

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Setup

```bash
# Clone repository
git clone <repository-url>
cd NB_Streamer

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run locally
python -m src.main
```

See [Development Guide](docs/DEVELOPMENT.md) for detailed setup.

## 🎯 Migration from v0.2.x

**Breaking Changes in v0.3.1:**
- Legacy `/events` endpoint is **disabled**
- All clients must use tenant-specific endpoints: `/{tenant}/events`

### Migration Steps

1. **Update client URLs**:
   ```diff
   - POST /events
   + POST /n2con/events
   ```

2. **Remove NB_Tenant from payload**:
   ```diff
   {
     "type": "event",
   -  "NB_Tenant": "n2con",
     "message": "Event data"
   }
   ```

3. **Update configuration**:
   ```bash
   # Add to .env
   NB_TENANTS=n2con,othertenant
   ```

## 📊 Monitoring

### Health Checks

```bash
# Container health
docker compose ps

# Application health
curl http://localhost:8080/health
```

### Logs

```bash
# Follow application logs
docker compose logs -f nb-streamer

# View recent logs
docker compose logs --tail=100 nb-streamer
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration notes.

## 🔒 Security

- All endpoints require authentication (configurable)
- Tenant isolation prevents cross-tenant data access
- Request validation and sanitization
- Secure defaults for production deployment

Report security issues privately via GitHub Security Advisories.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions

---

**Current Version**: 0.3.1 | **Docker Images**: Available on GitHub Container Registry
