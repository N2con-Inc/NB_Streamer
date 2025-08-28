# Per-Tenant Authentication Specification
**Target Version:** v0.4.0  
**Type:** Major Feature Enhancement  
**Status:** Planning Phase

## Overview

This specification outlines the implementation of per-tenant authentication mechanisms for NB_Streamer v0.4.0. This feature will allow each tenant to have separate authentication credentials and potentially different authentication methods, providing better security isolation and tenant management.

## Current State Analysis

### Current Implementation (v0.3.1)
- **Global Authentication**: Single set of credentials for all tenants
- **Supported Methods**: Bearer token, Basic auth, Custom header, or None
- **Configuration**: Single auth configuration applied universally
- **Security**: All tenants share the same credentials

### Limitations
- No tenant isolation in authentication
- Security breach affects all tenants
- Difficult to manage tenant-specific access
- Cannot have different auth requirements per tenant

## Proposed Architecture

### 1. Configuration Structure

#### Option A: JSON Configuration (Recommended)
```bash
# Per-tenant authentication configuration
NB_TENANT_AUTH='{
  "tenant1": {
    "type": "bearer",
    "token": "tenant1-secret-token"
  },
  "tenant2": {
    "type": "basic", 
    "username": "tenant2user",
    "password": "tenant2pass"
  },
  "tenant3": {
    "type": "header",
    "header_name": "X-Tenant3-Key",
    "header_value": "tenant3-secret"
  },
  "tenant4": {
    "type": "none"
  }
}'

# Global fallback authentication (backward compatibility)
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=global-fallback-token
```

#### Option B: Environment Variable Pattern
```bash
# Per-tenant auth type
NB_AUTH_TENANT1_TYPE=bearer
NB_AUTH_TENANT2_TYPE=basic
NB_AUTH_TENANT3_TYPE=header

# Per-tenant credentials
NB_AUTH_TENANT1_TOKEN=tenant1-secret-token
NB_AUTH_TENANT2_USERNAME=tenant2user
NB_AUTH_TENANT2_PASSWORD=tenant2pass
NB_AUTH_TENANT3_HEADER_NAME=X-Tenant3-Key
NB_AUTH_TENANT3_HEADER_VALUE=tenant3-secret

# Global fallback
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=global-fallback-token
```

### 2. Authentication Flow

```mermaid
graph TD
    A[Request to /{tenant}/events] --> B[Extract tenant from path]
    B --> C{Tenant has specific auth?}
    C -->|Yes| D[Use tenant-specific auth]
    C -->|No| E[Use global/fallback auth]
    D --> F[Validate tenant credentials]
    E --> G[Validate global credentials]
    F --> H{Valid?}
    G --> H
    H -->|Yes| I[Process request]
    H -->|No| J[Return 401 Unauthorized]
```

### 3. Code Architecture Changes

#### Configuration Model Updates
```python
class TenantAuthConfig(BaseModel):
    type: Literal["none", "bearer", "basic", "header"]
    token: Optional[str] = None
    username: Optional[str] = None  
    password: Optional[str] = None
    header_name: Optional[str] = None
    header_value: Optional[str] = None

class Config(BaseSettings):
    # Existing global auth (backward compatibility)
    nb_auth_type: Literal["none", "bearer", "basic", "header"] = "none"
    nb_auth_token: Optional[str] = None
    # ... other global auth fields
    
    # New per-tenant auth
    nb_tenant_auth: Optional[Dict[str, TenantAuthConfig]] = None
    
    @field_validator("nb_tenant_auth", mode="before")
    @classmethod
    def parse_tenant_auth(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
```

#### Authentication Service Updates
```python
class AuthService:
    def __init__(self):
        self.global_auth = self._setup_global_auth()
        self.tenant_auth = self._setup_tenant_auth()
    
    async def authenticate(self, request: Request, tenant: str) -> bool:
        """Authenticate request for specific tenant."""
        # Try tenant-specific auth first
        if tenant in self.tenant_auth:
            return await self._authenticate_tenant(request, tenant)
        
        # Fallback to global auth
        return await self._authenticate_global(request)
    
    async def _authenticate_tenant(self, request: Request, tenant: str) -> bool:
        """Authenticate using tenant-specific configuration."""
        tenant_config = self.tenant_auth[tenant]
        # Implementation based on tenant_config.type
        pass
```

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
1. **Configuration Model Updates**
   - Extend Config class with tenant-specific auth fields
   - Add validation for tenant auth configurations
   - Implement JSON parsing and validation

2. **Authentication Service Refactor**
   - Update AuthService to support tenant-specific authentication
   - Maintain backward compatibility with global auth
   - Add tenant parameter to authenticate method

### Phase 2: Integration (Week 2)
3. **Endpoint Updates**
   - Update all authenticated endpoints to pass tenant information
   - Modify request handlers to use tenant-specific auth
   - Update error messages to be tenant-aware

4. **Testing Infrastructure**
   - Create test cases for per-tenant authentication
   - Test mixed authentication scenarios
   - Validate backward compatibility

### Phase 3: Documentation and Deployment (Week 3)
5. **Documentation Updates**
   - Update configuration documentation
   - Create migration guide from v0.3.x
   - Add security best practices guide

6. **Deployment Tools**
   - Update Docker Compose examples
   - Create configuration templates
   - Update CI/CD workflows if needed

## Configuration Examples

### Mixed Authentication Setup
```bash
# Global fallback for unspecified tenants
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=default-api-key

# Per-tenant configurations
NB_TENANT_AUTH='{
  "customer-a": {
    "type": "bearer",
    "token": "customer-a-secure-token-2024"
  },
  "customer-b": {
    "type": "basic",
    "username": "customer_b_user",
    "password": "customer_b_secure_pass"
  },
  "internal": {
    "type": "header",
    "header_name": "X-Internal-Key", 
    "header_value": "internal-system-key"
  },
  "public-demo": {
    "type": "none"
  }
}'
```

### Development Setup
```bash
# Simple development setup - all tenants use same token
NB_TENANT_AUTH='{
  "dev-tenant1": {"type": "bearer", "token": "dev-token-123"},
  "dev-tenant2": {"type": "bearer", "token": "dev-token-123"},
  "test-tenant": {"type": "none"}
}'
```

## Security Considerations

### Enhanced Security Features
1. **Credential Isolation**: Each tenant has separate credentials
2. **Flexible Auth Methods**: Different tenants can use different auth types
3. **Granular Access Control**: Compromise of one tenant doesn't affect others
4. **Audit Trail**: Authentication attempts are logged per tenant

### Security Best Practices
1. **Strong Tokens**: Use cryptographically secure tokens (min 32 chars)
2. **Regular Rotation**: Implement token rotation procedures
3. **Secure Storage**: Store credentials in secure environment variables
4. **Monitoring**: Log authentication failures per tenant
5. **Rate Limiting**: Consider per-tenant rate limiting (future enhancement)

## Backward Compatibility

### Migration Strategy
1. **Seamless Upgrade**: Existing global auth continues to work
2. **Gradual Migration**: Tenants can be migrated one by one
3. **Configuration Validation**: Clear error messages for invalid configs
4. **Documentation**: Comprehensive migration guide

### Deprecation Timeline
- **v0.4.0**: Introduce per-tenant auth, global auth still supported
- **v0.5.0**: Mark global-only auth as deprecated
- **v1.0.0**: Consider requiring per-tenant auth for multi-tenant deployments

## Performance Considerations

### Optimization Strategies
1. **Configuration Caching**: Cache parsed tenant auth configurations
2. **Authentication Caching**: Consider short-term auth result caching
3. **Efficient Lookup**: Use hash maps for O(1) tenant auth lookup
4. **Memory Usage**: Optimize configuration storage for many tenants

### Scalability
- **Many Tenants**: Efficient handling of 100+ tenants
- **Large Configurations**: Support for complex auth configurations
- **Hot Reloading**: Potential future feature for config updates

## Testing Strategy

### Unit Tests
- Configuration parsing and validation
- Authentication service tenant isolation
- Error handling and edge cases
- Backward compatibility scenarios

### Integration Tests  
- End-to-end authentication flows
- Mixed authentication scenarios
- Performance with multiple tenants
- Security isolation validation

### Load Testing
- Performance with many tenants
- Authentication throughput
- Memory usage patterns
- Concurrent access patterns

## Documentation Requirements

### User Documentation
1. **Configuration Guide**: Complete setup instructions
2. **Migration Guide**: Step-by-step upgrade from v0.3.x
3. **Security Guide**: Best practices and recommendations
4. **Troubleshooting**: Common issues and solutions

### Developer Documentation
1. **Architecture Overview**: Technical implementation details
2. **API Reference**: Updated endpoint documentation
3. **Extension Guide**: How to add new auth methods
4. **Testing Guide**: How to test per-tenant auth

## Success Metrics

### Technical Metrics
- **Backward Compatibility**: 100% of existing configurations work
- **Performance**: <5ms additional latency per auth check
- **Security**: Zero credential leakage between tenants
- **Reliability**: 99.9% auth success rate for valid credentials

### User Experience Metrics
- **Migration Time**: <30 minutes for typical deployment
- **Configuration Errors**: Clear, actionable error messages
- **Documentation Quality**: Users can configure without support
- **Feature Adoption**: >50% of multi-tenant deployments use feature

## Risk Assessment

### Technical Risks
1. **Breaking Changes**: Risk of breaking existing deployments
   - **Mitigation**: Extensive testing and backward compatibility
2. **Performance Impact**: Additional complexity in auth flow
   - **Mitigation**: Performance testing and optimization
3. **Security Vulnerabilities**: New attack vectors
   - **Mitigation**: Security review and penetration testing

### Operational Risks
1. **Configuration Complexity**: Users may misconfigure
   - **Mitigation**: Comprehensive documentation and validation
2. **Migration Issues**: Problems upgrading from v0.3.x
   - **Mitigation**: Migration guide and testing tools
3. **Support Burden**: Increased complexity in troubleshooting
   - **Mitigation**: Better logging and diagnostic tools

## Future Enhancements (v0.5.0+)

### Advanced Features
1. **JWT Token Support**: Support for JWT-based authentication
2. **OAuth Integration**: Integration with OAuth providers
3. **API Key Management**: Built-in key generation and rotation
4. **Rate Limiting**: Per-tenant rate limiting
5. **Audit Logging**: Enhanced security audit capabilities
6. **Dynamic Configuration**: Hot-reload of auth configurations

### Monitoring & Observability
1. **Authentication Metrics**: Per-tenant auth success/failure rates
2. **Security Dashboards**: Visual monitoring of auth events
3. **Alerting**: Notifications for auth failures or anomalies
4. **Compliance**: Features for regulatory compliance

## Conclusion

Per-tenant authentication represents a significant enhancement to NB_Streamer's multi-tenant capabilities. This feature will provide:

- **Enhanced Security**: Proper tenant isolation
- **Operational Flexibility**: Different auth methods per tenant
- **Enterprise Readiness**: Production-grade security features
- **Scalability**: Support for large multi-tenant deployments

The phased implementation approach ensures minimal disruption to existing deployments while providing a clear path to enhanced security and functionality.
