# NB_Streamer

A FastAPI-based service that receives Netbird events, transforms them into GELF (Graylog Extended Log Format), and forwards them to Graylog for centralized logging and monitoring.

## Features

- **Event Processing**: Receives Netbird events via HTTP POST
- **GELF Transformation**: Converts events to Graylog Extended Log Format
- **Multi-tenant Support**: Tags events with tenant identifiers
- **Flexible Authentication**: Supports Bearer token, Basic auth, and custom headers
- **Real-time Statistics**: Tracks event processing metrics with detailed breakdowns
- **Health Monitoring**: Built-in health checks and monitoring tools
- **Docker Support**: Containerized deployment for easy scaling
- **Comprehensive Logging**: Debug-level logging for troubleshooting

## Architecture

```
Netbird Events → NB_Streamer → GELF Format → Graylog Server
                     ↓
               Statistics & Monitoring
```

## API Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/health` | Health check endpoint | None |
| GET | `/stats` | View event processing statistics | None |
| POST | `/events` | Receive Netbird events | Required |
| POST | `/stats/reset` | Reset statistics counters | Required |

## Statistics Features

The service provides comprehensive event processing statistics:

- **Total Counters**: Received, forwarded, and failed events
- **Success Rate**: Percentage of successfully processed events
- **Per-tenant Breakdown**: Statistics grouped by tenant ID
- **Per-level Breakdown**: Events categorized by log level
- **Uptime Tracking**: Service uptime and last event timestamp
- **Real-time Updates**: Statistics update with each processed event

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/NB_Streamer.git
cd NB_Streamer
```

### 2. Configuration
Copy the sample environment file and customize:
```bash
cp .env.sample .env
# Edit .env with your specific configuration
```

Required configuration:
- `NB_TENANT_ID`: Your tenant identifier (e.g., "n2con")
- `NB_GRAYLOG_HOST`: Graylog server IP (e.g., "10.0.1.244")
- `NB_AUTH_TOKEN`: Authentication token for securing the API

### 3. Docker Deployment (Recommended)
```bash
# Build the image
docker build -t nb_streamer .

# Run the container
docker run -d --name nb_streamer --env-file .env -p 8001:8000 nb_streamer
```

### 4. Verify Installation
```bash
# Check health
curl http://localhost:8001/health

# View statistics
curl http://localhost:8001/stats

# Monitor with included script
./monitor_nb_streamer.sh
```

## Monitoring

### Built-in Monitoring Script
Use the included monitoring script for real-time statistics:

```bash
# Single check
./monitor_nb_streamer.sh

# Continuous monitoring
./monitor_nb_streamer.sh --watch
```

### Docker Logs
Monitor service logs:
```bash
# Follow logs
docker logs -f nb_streamer

# View recent logs
docker logs nb_streamer --tail 50
```

### Statistics API
Access detailed statistics via HTTP:
```bash
# Get current statistics
curl http://localhost:8001/stats | jq

# Reset statistics (requires authentication)
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/stats/reset
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NB_HOST` | Server bind address | `0.0.0.0` | No |
| `NB_PORT` | Server port | `8000` | No |
| `NB_TENANT_ID` | Tenant identifier | - | **Yes** |
| `NB_GRAYLOG_HOST` | Graylog server IP | `localhost` | **Yes** |
| `NB_GRAYLOG_PORT` | Graylog GELF port | `12201` | No |
| `NB_GRAYLOG_PROTOCOL` | Protocol (udp/tcp) | `udp` | No |
| `NB_AUTH_TYPE` | Authentication type | `bearer` | No |
| `NB_AUTH_TOKEN` | Bearer token | - | **Yes** |
| `NB_LOG_LEVEL` | Logging level | `INFO` | No |

### Authentication Types

1. **Bearer Token** (Recommended)
   ```bash
   NB_AUTH_TYPE=bearer
   NB_AUTH_TOKEN=your_secure_token
   ```

2. **Basic Authentication**
   ```bash
   NB_AUTH_TYPE=basic
   NB_AUTH_USERNAME=username
   NB_AUTH_PASSWORD=password
   ```

3. **Custom Header**
   ```bash
   NB_AUTH_TYPE=header
   NB_AUTH_HEADER_NAME=X-Custom-Auth
   NB_AUTH_HEADER_VALUE=custom_value
   ```

## GELF Message Format

Events are transformed into GELF format with:

- **Standard Fields**: version, host, short_message, timestamp, level
- **Tenant Tagging**: `_NB_tenant` field for multi-tenant filtering
- **Netbird Fields**: All original fields prefixed with `_NB_`
- **JSON Serialization**: Complex objects converted to JSON strings

Example GELF message:
```json
{
  "version": "1.1",
  "host": "nb_streamer",
  "short_message": "Netbird user_login",
  "timestamp": 1643723400.0,
  "level": 6,
  "_NB_tenant": "n2con",
  "_NB_ID": "event-123",
  "_NB_InitiatorID": "user@example.com",
  "_NB_Message": "User login successful"
}
```

## Development

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run locally
python -m src.main
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Test specific event
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"ID":"test","Message":"Test event"}' \
     http://localhost:8001/events
```

## Production Deployment

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  nb_streamer:
    build: .
    ports:
      - "8001:8000"
    environment:
      - NB_TENANT_ID=your_tenant
      - NB_GRAYLOG_HOST=your_graylog_ip
      - NB_AUTH_TOKEN=your_secure_token
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment
See `k8s/` directory for Kubernetes manifests.

### Security Considerations
- Use strong, unique authentication tokens
- Enable HTTPS in production (reverse proxy recommended)
- Monitor failed authentication attempts
- Regularly rotate authentication credentials
- Network-level access controls to Graylog server

## Troubleshooting

### Common Issues

1. **Connection to Graylog Failed**
   - Verify `NB_GRAYLOG_HOST` and `NB_GRAYLOG_PORT`
   - Test network connectivity: `nc -u -v graylog_host 12201`
   - Check Graylog server logs

2. **Authentication Errors**
   - Verify `NB_AUTH_TOKEN` matches client configuration
   - Check authentication type is correctly set
   - Review service logs for auth failures

3. **Events Not Appearing in Graylog**
   - Check Graylog inputs are configured for GELF UDP
   - Verify tenant filtering: search for `_NB_tenant:your_tenant`
   - Review Graylog processing pipeline

### Log Analysis
```bash
# Service errors
docker logs nb_streamer 2>&1 | grep ERROR

# Authentication failures
docker logs nb_streamer 2>&1 | grep "authentication"

# Event processing
docker logs nb_streamer 2>&1 | grep "Successfully forwarded"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

## Changelog

### v0.2.0 (2025-07-31)
- Added comprehensive event statistics tracking
- Implemented `/stats` and `/stats/reset` endpoints
- Added monitoring script (`monitor_nb_streamer.sh`)
- Enhanced error handling and failure tracking
- Improved documentation and deployment guides
- Added per-tenant and per-level event breakdowns
- Integrated real-time success rate calculation

### v0.1.0 (Initial Release)
- Basic Netbird event reception and GELF transformation
- Multi-tenant support with tenant tagging
- Flexible authentication (Bearer, Basic, Custom header)
- Docker containerization
- Health check endpoint
- Comprehensive logging and debugging
