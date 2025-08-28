# Changelog

All notable changes to NB_Streamer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-08-28

### Removed
- **BREAKING**: Legacy `/events` endpoint has been permanently disabled
- Removed legacy environment variables and configuration options
- Cleaned up legacy-related code and comments

### Changed
- Simplified codebase by removing backward compatibility layer
- Updated documentation to reflect multi-tenant only architecture
- Legacy `/events` endpoint now returns clear error message directing users to tenant-specific endpoints

### Fixed
- Improved configuration validation and error messages
- Streamlined multi-tenant configuration handling

### Migration Notes
- **Required**: All clients must now use tenant-specific endpoints: `POST /{tenant}/events`
- **Required**: Remove any legacy environment variables from your `.env` file
- The legacy `/events` endpoint will return HTTP 400 with migration instructions

## [0.3.0] - 2025-08-28

### Added
- **Multi-tenancy support** with tenant-specific endpoints (`/{tenant}/events`)
- Tenant isolation and validation
- Enhanced logging with tenant context
- Support for external reverse proxy deployments
- Docker health checks and container optimization
- Comprehensive API documentation for multi-tenant endpoints

### Changed
- **BREAKING**: Primary endpoint moved from `/events` to `/{tenant}/events`
- Container now runs on port 8080 by default
- Enhanced error handling and validation
- Improved configuration management
- Updated Docker Compose configurations for production deployment

### Added - Configuration
- `NB_TENANTS`: Comma-separated list of allowed tenants
- `NB_ALLOW_LEGACY_EVENTS`: Toggle for legacy endpoint support
- `NB_TRUST_PROXY_HEADERS`: Support for proxy headers
- `NB_EXPOSE_TENANTS`: Control tenant information exposure

### Deprecated
- Legacy `/events` endpoint (maintained for backward compatibility in 0.3.0)
- Single-tenant configuration approach

### Migration Guide
- Update client code to use `/{tenant}/events` endpoints
- Configure `NB_TENANTS` environment variable
- Test with both legacy and new endpoints during transition
- Plan to disable legacy support in future versions

## [0.2.0] - Previous Release

### Added
- FastAPI-based HTTP server
- Graylog integration
- Authentication support (Bearer, Basic, Header)
- Docker containerization
- Basic logging and monitoring

### Features
- Event forwarding to Graylog
- Configurable authentication
- Environment-based configuration
- Health check endpoints
- Container deployment support
