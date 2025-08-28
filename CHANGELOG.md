# Changelog

All notable changes to NB_Streamer will be documented in this file.

## [0.5.0] - 2025-08-28

### 🎉 Major Simplification Release

This version represents a complete architectural simplification, moving from complex multi-tenant URL routing to simple payload-based tenant identification.

### ✨ Added
- **Single endpoint architecture**: All NetBird instances use `/events`
- **Payload-based tenant identification**: Uses `NB_Tenant` field in JSON payload
- **Simplified configuration**: Single authentication token for all tenants
- **Enhanced error handling**: Clear error messages for missing or invalid tenant fields
- **Comprehensive documentation**: New NetBird setup guide with webhook body template examples

### 🔄 Changed
- **BREAKING**: Removed complex multi-tenant URL routing (`/tenant/events`)
- **BREAKING**: Removed per-tenant authentication tokens
- **BREAKING**: All NetBird instances must now include `NB_Tenant` field in webhook body template
- **Improved**: Simplified configuration management
- **Updated**: All documentation reflects new simplified approach

### ❌ Removed
- Multi-tenant configuration complexity (`NB_TENANTS`, `NB_REQUIRE_TENANT_PATH`, etc.)
- Per-tenant token management (`NB_AUTH_TOKEN_tenant`)
- Legacy endpoint complexity
- Complex tenant validation and routing logic

### 📚 Documentation
- Added comprehensive [NetBird Setup Guide](docs/netbird-setup.md)
- Updated README.md with simplified architecture explanation
- Updated .env.example with new configuration format
- Added webhook body template examples for different tenants

### 🔧 Configuration Changes
Required environment variables are now much simpler:
```env
NB_GRAYLOG_HOST=your-graylog-server.com
NB_AUTH_TYPE=bearer  
NB_AUTH_TOKEN=your-secure-token
```

### 🚀 Migration from 0.3.x
1. Update NetBird webhook body templates to include `NB_Tenant` field
2. Simplify NB_Streamer configuration (remove multi-tenant specific settings)
3. Update webhook URLs to use `/events` endpoint for all NetBird instances
4. Use single authentication token for all tenants

### 🎯 Benefits
- **Easier management**: One endpoint, one token for all NetBird instances
- **Simplified scaling**: Add new tenants by just updating webhook body templates
- **Reduced complexity**: No more complex tenant configuration management
- **Better maintainability**: Cleaner codebase with less complexity

---

## [0.3.x] - Previous Versions

See git history for detailed changelog of multi-tenant architecture versions.
