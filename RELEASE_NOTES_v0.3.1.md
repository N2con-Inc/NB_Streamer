# NB_Streamer v0.3.1 Release Notes

## 🎯 Overview

Version 0.3.1 is a **cleanup release** that removes legacy backward compatibility and completes the transition to a pure multi-tenant architecture. This version focuses on simplification, improved documentation, and production-ready container registry workflows.

## 🚨 Breaking Changes

### Legacy Endpoint Permanently Disabled
- **BREAKING**: The legacy `/events` endpoint is now **permanently disabled**
- All clients must use tenant-specific endpoints: `POST /{tenant}/events`
- Legacy configuration variables have been removed

### Migration Required
If you haven't migrated from v0.2.x yet:

1. **Update client URLs**:
   ```diff
   - POST http://your-server/events
   + POST http://your-server/{tenant}/events
   ```

2. **Remove tenant from payload**:
   ```diff
   {
     "type": "user_login",
   - "NB_Tenant": "n2con",
     "message": "User logged in"
   }
   ```

3. **Update configuration**:
   ```bash
   # Required in .env
   NB_TENANTS=tenant1,tenant2,tenant3
   ```

## ✨ New Features

### 🐳 Container Registry Support
- **Pre-built Docker images** available on GitHub Container Registry
- **Automated builds** via GitHub Actions on code changes
- **One-command deployment** with `./scripts/deploy.sh`
- **Version-specific tags** for stable deployments

### 📊 Enhanced Documentation  
- **Comprehensive guides** for all deployment scenarios
- **Container registry setup** with step-by-step instructions
- **Configuration reference** with all environment variables documented
- **Migration guides** for smooth upgrades

### 🔧 Production Improvements
- **Simplified codebase** with legacy code removed
- **Cleaner configuration** with consistent environment variables
- **Better error messages** for misconfiguration issues
- **Standardized Docker Compose** files without deprecated options

## 🛠️ What's New

### Container Registry Workflow
```bash
# Deploy latest version
./scripts/deploy.sh

# Deploy specific version
IMAGE_TAG=0.3.1 ./scripts/deploy.sh

# Build and push custom images
./scripts/build-and-push.sh
```

### Automated Builds
- GitHub Actions automatically builds images on push
- Multiple tags created: `latest`, `main`, version-specific
- Security attestations for all built images

### Simplified Deployment
- `docker-compose.production.yml` pulls pre-built images
- No more local building required
- Faster deployment times
- Consistent environments across deployments

## 📋 Complete Changes

### Removed
- Legacy `/events` endpoint functionality
- Legacy environment variables (`NB_ALLOW_LEGACY_EVENTS`, etc.)
- Backward compatibility layer
- Unused legacy code and comments
- Deprecated documentation

### Added
- Container registry build and deployment scripts
- GitHub Actions CI/CD workflow
- Production Docker Compose configuration
- Comprehensive deployment documentation
- Container registry setup guides
- Configuration reference documentation

### Changed
- Cleaner, simplified codebase
- Updated documentation structure
- Improved error messages
- Standardized configuration format
- Enhanced logging and observability

### Fixed
- Removed deprecated Docker Compose version fields
- Cleaned up environment file examples
- Improved configuration validation
- Streamlined multi-tenant setup

## 🚀 Getting Started

### New Deployment (Recommended)
```bash
# Set up registry access (one-time setup)
export IMAGE_REGISTRY="ghcr.io"
export IMAGE_NAMESPACE="your-github-username"

# Deploy with pre-built images
./scripts/deploy.sh
```

### Traditional Deployment
```bash
# Build and run locally
docker compose up -d --build
```

## 📊 Migration Guide

### From v0.3.0
1. Update any legacy endpoint references
2. Remove legacy environment variables from `.env`
3. Test with new deployment methods

### From v0.2.x
1. Follow the breaking changes section above
2. Update client applications to use tenant-specific endpoints
3. Update configuration files
4. Test thoroughly in staging environment

## 🔍 Technical Details

### Container Registry
- **Registry**: GitHub Container Registry (ghcr.io)
- **Alternative**: Docker Hub support included
- **Tags**: `latest`, version-specific, branch-based
- **Size**: ~50MB optimized production image

### Architecture
- **Multi-tenant only**: No single-tenant fallback
- **FastAPI**: Async event processing
- **Docker**: Production-ready containerization
- **Logging**: Structured logging with tenant context

## 🆘 Support

- **Documentation**: [Complete guides in docs/](docs/)
- **Migration help**: See [Migration Guide](README.md#-migration-from-v02x)
- **Issues**: Use GitHub Issues for bug reports
- **Questions**: Use GitHub Discussions

## 🎉 What's Next

- **v0.4.x**: Planned features include enhanced monitoring, metrics, and scaling improvements
- **Feedback welcome**: Let us know how the new deployment workflow works for you!

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)  
**Container Images**: Available on [GitHub Container Registry](https://github.com/users/USERNAME/packages/container/nb-streamer)
