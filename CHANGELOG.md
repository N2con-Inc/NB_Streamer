# Changelog

## [0.2.5] - 2025-08-01

### Changed
- **Version Consistency**: Standardized all version references across project to maintain consistency
- **Documentation Updates**: Updated all guides and documentation to reflect current version
- **Project Maintenance**: Comprehensive version audit and cleanup

### Fixed
- **Version References**: Fixed inconsistent version numbers across multiple files
- **Documentation Alignment**: Ensured all documentation reflects the correct current version


All notable changes to NB_Streamer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2025-07-31

### Fixed
- **Timestamp Column Display**: Fixed timestamp column display issues in Graylog interface
- **Enhanced Graylog Integration**: Improved event formatting and field mapping for better visibility

### Enhanced
- **Event Processing**: Optimized event transformation pipeline
- **Error Handling**: Improved error handling and logging throughout the application


## [0.2.0] - 2025-07-31

## [0.2.3] - 2025-07-31

### Fixed
- **Graylog Message Display**: Resolved "Netbird unknown" appearing in Graylog message column
  - Now uses actual Netbird `Message` field for `short_message` when available
  - Example: "User successfully connected to VPN gateway" instead of "Netbird unknown"
  - Improved readability and event identification in Graylog interface

### Enhanced
- **Message Generation Logic**:
  1. **Preferred**: Uses `Message` field directly if available and non-empty
  2. **Fallback**: Constructs from `event_type`, `action`, and `InitiatorID`
  3. **Minimal**: Falls back to "Netbird event by [user]" format
  - Always provides meaningful `short_message` for Graylog display

- **Timestamp Handling**: Enhanced to support both `timestamp` and `Timestamp` fields
  - Handles capitalization variations in Netbird event data
  - Ensures accurate event timing in Graylog

### Testing
- Added `test_short_message.py` for message generation validation
- Verified multiple scenarios: with Message, without Message, minimal fields
- All test cases now produce meaningful, readable messages

### User Experience
- **Better Log Analysis**: Clear, descriptive messages in Graylog
- **Improved Troubleshooting**: Actual event content displayed
- **Enhanced Monitoring**: Meaningful message summaries for dashboard widgets

## [0.2.2] - 2025-07-31

### Added
- **IP and Port Separation**: Automatic parsing of IP:port combinations into separate fields
  - Supports both IPv4 (`192.168.1.1:80`) and IPv6 (`[2001:db8::1]:443`) formats
  - Creates separate `_addr` and `_port` fields for better Graylog filtering
  - Example: `source_addr: "192.168.68.141:54615"` becomes:
    - `_NB_meta_source_addr: "192.168.68.141"`
    - `_NB_meta_source_port: "54615"`

- **Enhanced Network Analysis**:
  - Improved subnet-based filtering with pure IP fields
  - Port range queries for network security analysis
  - Better dashboard visualization capabilities
  - Separate indexing for IPs and ports improves query performance

- **Testing and Documentation**:
  - `test_ip_port_parsing.py` script for validation
  - `IP_PORT_PARSING_GUIDE.md` with comprehensive examples
  - Graylog search patterns for network analysis

### Enhanced
- **Field Processing**: Automatic detection of address fields with common patterns
- **Regex Parsing**: Robust parsing logic for various IP:port formats
- **Error Handling**: Graceful fallback for unparseable address formats

### Graylog Benefits
- Direct IP field searches: `_NB_meta_source_addr:"192.168.68.141"`
- Port-specific filtering: `_NB_meta_destination_port:"80"`
- Range queries: `_NB_meta_source_port:>49152`
- Combined filters: `_NB_meta_source_addr:"192.168.*" AND _NB_meta_destination_port:"443"`

## [0.2.1] - 2025-07-31

### Added
- **Advanced Field Flattening**: Recursive flattening of nested Netbird event structures
  - All nested objects become individual GELF fields with descriptive names
  - Example: `meta.source_addr` becomes `_NB_meta_source_addr`
  - Arrays handled with indexed flattening for object arrays
  - Simple arrays preserved as JSON strings

- **Enhanced Graylog Integration**:
  - Individual searchable fields instead of JSON strings
  - Better performance for complex queries
  - Improved field discoverability in Graylog interface
  - Auto-completion support for nested field searches

- **Field Testing and Documentation**:
  - `test_flattening.py` script for field discovery and validation
  - `FIELD_FLATTENING_GUIDE.md` with comprehensive field mapping examples
  - Graylog search pattern documentation
  - Dashboard widget configuration examples

### Changed
- **Breaking Change**: Nested objects now flattened to individual fields
  - Previous: `_NB_meta: "{\"source_addr\":\"10.0.1.100\"}"`
  - Current: `_NB_meta_source_addr: "10.0.1.100"`
- **Improved Field Naming**: Consistent underscore-separated naming convention
- **Enhanced Array Handling**: Better support for complex nested arrays

### Configuration Updates
- **Graylog Server**: Updated to `10.0.1.244` (wizard.n2con.int)
- **Tenant ID**: Changed to `n2con` for production deployment
- **Sample Configuration**: Updated with production-ready examples

### Technical Improvements
- Recursive flattening algorithm with configurable depth
- Thread-safe field processing for concurrent requests
- Memory-efficient flattening for large event structures
- Comprehensive error handling for malformed nested data

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
