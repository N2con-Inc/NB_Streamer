# Changelog

All notable changes to NB_Streamer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2024-08-28

### Critical Bugfix
- **CRITICAL**: Fixed Graylog host configuration from localhost to 10.0.1.244
- **CRITICAL**: Updated all default configurations to use correct production Graylog server
- Fixed version number display in health endpoint (now shows 0.3.2 correctly)

### Documentation Updates
- Updated all documentation to reference correct Graylog host (10.0.1.244:12201)
- Fixed production deployment examples with correct server configuration
- Updated .env examples and configuration templates
- Corrected configuration documentation defaults

### Configuration Changes
- Default graylog_host changed from "localhost" to "10.0.1.244"
- Production environment files updated with correct host
- All example configurations now use production values

**Migration**: If upgrading from 0.3.2, update NB_GRAYLOG_HOST=10.0.1.244 in your .env file

---

## [0.3.2] - 2024-08-28

### Fixed
- **CRITICAL**: Fixed Pydantic configuration not reading environment variables
- **CRITICAL**: Added missing `validate_startup_configuration()` method
- Fixed default port from 8000 to 8080 for consistency
- Improved Pydantic v2 compatibility with proper SettingsConfigDict
- Fixed Docker container startup issues

### Changed
- Updated version to 0.3.2 across all files
- Enhanced configuration validation with proper error messages
- Improved environment variable handling in containers

### Technical Improvements
- Proper Pydantic v2 BaseSettings configuration
- Fixed model_config formatting for environment variable loading
- Enhanced startup configuration validation
- Better error handling for missing configuration

---

## [Planned] - v0.4.0 (Q1 2025)

### Planned Features
- **🔐 Per-Tenant Authentication**: Separate authentication mechanisms for each tenant
  - JSON-based tenant authentication configuration
  - Support for mixed authentication methods (Bearer, Basic, Header, None)
  - Backward compatibility with global authentication
  - Enhanced security through tenant credential isolation
- **📊 Enhanced Monitoring**: Per-tenant metrics and authentication tracking
- **🔧 Configuration Management**: Improved configuration validation and templates
- **🚦 Rate Limiting**: Optional per-tenant rate limiting (if time permits)

### Technical Improvements
- Performance optimizations for high-tenant-count deployments
- Enhanced error handling and user feedback
- Comprehensive test coverage for per-tenant features
- Security testing and penetration testing

### Documentation Updates
- Migration guide from v0.3.x to v0.4.0
- Security best practices guide
- Troubleshooting and debugging guide
- Architecture documentation updates

### Breaking Changes
- **None planned** - v0.4.0 will maintain full backward compatibility
- New features will be opt-in and additive
- Existing configurations will continue to work unchanged

---

## [0.3.1] - 2024-08-28

### Added
- **Container Registry Support**: Automated Docker builds and deployment
  - GitHub Actions CI/CD pipeline for image builds
  - Pre-built images on GitHub Container Registry (ghcr.io)
  - Production deployment scripts (`scripts/deploy.sh`, `scripts/build-and-push.sh`)
  - Docker Compose configurations for production deployments
- **Documentation Overhaul**: Comprehensive guides and references
  - Container registry setup guides
  - Deployment documentation with multiple scenarios
  - Configuration reference with all environment variables
  - External proxy integration guides (Traefik, Nginx)
- **Build and Deployment Tools**:
  - Release preparation script (`scripts/prepare-release.sh`)
  - Automated build and push workflows
  - Environment variable templates and examples

### Removed
- **BREAKING**: Legacy `/events` endpoint has been permanently disabled
- Removed legacy environment variables and configuration options
- Cleaned up legacy-related code and comments
- Moved outdated documentation to `docs/archive/`

### Changed
- Simplified codebase by removing backward compatibility layer
- Updated documentation structure with organized guides
- Legacy `/events` endpoint now returns clear error message directing users to tenant-specific endpoints
- Updated Docker configurations removing deprecated `version` fields
- Enhanced `.gitignore` and project file organization

### Fixed
- Improved configuration validation and error messages
- Streamlined multi-tenant configuration handling
- Fixed Pydantic configuration issues and environment handling
- Updated requirements.txt with proper dependencies

### Migration Notes
- **Required**: All clients must now use tenant-specific endpoints: `POST /{tenant}/events`
- **Required**: Remove any legacy environment variables from your `.env` file
- The legacy `/events` endpoint will return HTTP 400 with migration instructions
- Update deployment workflows to use container registry images

## [0.3.0] - 2024-08-28

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

---

## Release Notes

### v0.3.1 Release Notes
Comprehensive release notes available in [RELEASE_NOTES_v0.3.1.md](RELEASE_NOTES_v0.3.1.md)

### Future Releases
See [ROADMAP.md](ROADMAP.md) for detailed information about upcoming features and release timeline.
