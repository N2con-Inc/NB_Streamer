# Changelog

All notable changes to NB_Streamer will be documented in this file.

## [0.5.1] - 2025-08-28

### Fixed
- **NetBird Webhook Bug Workaround**: Fixed parsing of NetBird webhook payloads when using custom webhook body templates
  - Added Go map syntax parser for `meta` field that NetBird incorrectly sends as string instead of JSON object
  - Added HTML entity decoding (`&#43;` → `+`) for timestamps and other fields 
  - Added Go timestamp to ISO 8601 conversion (`2025-08-28 23:31:16.312662603 +0000 UTC` → `2025-08-28T23:31:16.312Z`)
  - Fixed OpenSearch/Elasticsearch date parsing errors in Graylog
  - Fixed JSON parsing exceptions caused by compressed GELF messages by disabling compression

### Added
- Comprehensive NetBird bug workaround documentation (`NETBIRD_BUG_WORKAROUND.md`)
- Code comments marking workaround functions for removal when upstream bug is fixed

### Technical Details
- **Root Cause**: NetBird's `{{.Event.Meta}}` template outputs Go map string instead of JSON object
- **Trigger**: Occurs when customizing webhook body template (e.g., adding `NB_Tenant` field)
- **Impact**: Events failed to index in Graylog due to malformed timestamp fields
- **Solution**: Automatic detection and parsing of Go map syntax with proper field extraction

### Notes
- This workaround will be **removed** when NetBird fixes the upstream bug
- Bug report filed with NetBird project
- All event processing now works correctly with proper field separation and timestamp formatting

## [0.5.0] - 2025-08-28

### Changed
- Simplified architecture from multi-tenant to single-tenant with `NB_Tenant` field-based routing
- Consolidated authentication to single API key
- Streamlined configuration and deployment

### Fixed
- Initial timestamp parsing improvements
- Code cleanup and simplification

## Previous Versions

See git history for earlier version details.
