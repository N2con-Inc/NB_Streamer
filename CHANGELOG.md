# Changelog

All notable changes to NB_Streamer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-31

### Added
- **Event Statistics System**: Comprehensive tracking of event processing metrics
  - Total counters for received, forwarded, and failed events
  - Per-tenant statistics breakdown
  - Per-log-level event categorization
  - Real-time success rate calculation
  - Service uptime tracking
  - Last event timestamp tracking

- **New API Endpoints**:
  - `GET /stats` - View current event processing statistics
  - `POST /stats/reset` - Reset statistics counters (authenticated)

- **Monitoring Tools**:
  - `monitor_nb_streamer.sh` - User-friendly monitoring script
  - Watch mode for continuous monitoring (`--watch` flag)
  - Visual indicators for service health and success rates

- **Enhanced Error Handling**:
  - Automatic failure tracking for authentication errors
  - Processing error categorization and counting
  - Thread-safe statistics updates

### Changed
- **Updated API Documentation**: Enhanced 404 error responses to include new endpoints
- **Improved Logging**: More detailed event processing logs with tenant information
- **Enhanced Health Checks**: Better service status reporting

### Fixed
- **Pydantic Model Access**: Fixed statistics tracking to properly access GELFMessage attributes
- **Thread Safety**: Implemented proper locking for concurrent statistics updates

### Technical Details
- Added `src/services/stats.py` for statistics management
- Enhanced `src/main.py` with statistics integration
- Statistics are reset on service restart
- All statistics operations are thread-safe using Python threading.Lock

## [0.1.0] - 2025-07-30

### Added
- **Initial Release**: Complete Netbird event streaming service
- **Core Features**:
  - FastAPI-based HTTP API for receiving Netbird events
  - GELF (Graylog Extended Log Format) transformation
  - Multi-tenant support with configurable tenant IDs
  - Flexible authentication system (Bearer, Basic, Custom header)

- **Event Processing**:
  - JSON event validation and parsing
  - Automatic timestamp handling (ISO strings, Unix timestamps, datetime objects)
  - Custom field prefixing with `_NB_` for Netbird fields
  - Tenant tagging with `_NB_tenant` field

- **Deployment Support**:
  - Docker containerization with Python 3.11-slim base
  - Environment-based configuration with Pydantic v2
  - Health check endpoint (`/health`)
  - Comprehensive logging with configurable levels

- **Documentation**:
  - Complete README with setup instructions
  - Environment configuration guide
  - API endpoint documentation
  - Troubleshooting section

- **Testing**:
  - Comprehensive test suite with pytest
  - Authentication testing
  - Event processing validation
  - Mock Graylog server testing

### Configuration
- **Environment Variables**: Complete configuration via environment variables
- **Authentication Types**: Support for Bearer token, Basic auth, and custom headers
- **Graylog Integration**: UDP/TCP support for GELF message transmission
- **Logging**: Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### API Endpoints
- `GET /health` - Service health check
- `POST /events` - Netbird event reception (authenticated)
- Custom 404 handler with endpoint information

### Infrastructure
- **Docker**: Multi-stage build with security best practices
- **Dependencies**: Pinned versions for stability
- **Security**: Non-root user execution in container
- **Networking**: Configurable host/port binding

---

## Development History

### Configuration Updates (2025-07-31)
- **Graylog Server**: Updated to `10.0.1.244` (wizard.n2con.int)
- **Tenant ID**: Changed to `n2con` for production deployment
- **Network Verification**: Confirmed connectivity to new Graylog infrastructure

### Deployment Testing (2025-07-31)
- Successfully deployed on Debian Linux host
- Verified event processing with 83+ events
- 100% success rate achieved
- Real Graylog server integration confirmed

### Future Roadmap
- [ ] Kubernetes deployment manifests
- [ ] Prometheus metrics integration
- [ ] Event batching for high-volume scenarios
- [ ] Advanced filtering and transformation rules
- [ ] Web-based dashboard for statistics
- [ ] SSL/TLS support for secure communications
