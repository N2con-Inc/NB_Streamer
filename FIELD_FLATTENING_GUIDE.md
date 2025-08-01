# Netbird Event Field Flattening Guide

NB_Streamer v0.2.1 introduces advanced field flattening for Netbird events, making nested data structures easily searchable in Graylog.

## Overview

Instead of storing nested objects as JSON strings, NB_Streamer now flattens all nested structures into individual GELF fields with descriptive names prefixed with `_NB_`.

## Field Naming Convention

All Netbird event fields are prefixed with `_NB_` and nested structures are flattened using underscore separators:

```
Original Nested Structure:
{
  "meta": {
    "connection_info": {
      "encrypted": true,
      "cipher": "AES-256-GCM"
    }
  }
}

Flattened GELF Fields:
_NB_meta_connection_info_encrypted: "true"
_NB_meta_connection_info_cipher: "AES-256-GCM"
```

## Common Netbird Field Mappings

### Connection Information
| Original Path | GELF Field | Example Value |
|---------------|------------|---------------|
| `meta.source_addr` | `_NB_meta_source_addr` | "192.168.1.100" |
| `meta.destination_addr` | `_NB_meta_destination_addr` | "10.0.1.200" |
| `meta.port` | `_NB_meta_port` | "22" |
| `meta.protocol` | `_NB_meta_protocol` | "TCP" |
| `meta.bytes_sent` | `_NB_meta_bytes_sent` | "1024" |
| `meta.bytes_received` | `_NB_meta_bytes_received` | "2048" |

### User Information
| Original Path | GELF Field | Example Value |
|---------------|------------|---------------|
| `user.id` | `_NB_user_id` | "user-123" |
| `user.email` | `_NB_user_email` | "john@example.com" |
| `user.groups` | `_NB_user_groups` | ["admin", "users"] |
| `meta.user_info.username` | `_NB_meta_user_info_username` | "admin" |
| `meta.user_info.role` | `_NB_meta_user_info_role` | "administrator" |

### Geographic and Device Data
| Original Path | GELF Field | Example Value |
|---------------|------------|---------------|
| `additional_data.geo_location.country` | `_NB_additional_data_geo_location_country` | "US" |
| `additional_data.geo_location.region` | `_NB_additional_data_geo_location_region` | "CA" |
| `additional_data.device_info.os` | `_NB_additional_data_device_info_os` | "Linux" |
| `additional_data.device_info.version` | `_NB_additional_data_device_info_version` | "Ubuntu 22.04" |

### Event Metadata
| Original Path | GELF Field | Example Value |
|---------------|------------|---------------|
| `ID` | `_NB_ID` | "event-123" |
| `InitiatorID` | `_NB_InitiatorID` | "user@example.com" |
| `target_id` | `_NB_target_id` | "peer-001" |
| `event_type` | `_NB_event_type` | "connection" |
| `action` | `_NB_action` | "connect" |
| `reference` | `_NB_reference` | "conn-12345" |

## Array Handling

Arrays are handled in two ways:

### Simple Arrays
Simple arrays (strings, numbers) are converted to JSON:
```json
"permissions": ["read", "write", "admin"]
```
Becomes:
```
_NB_meta_user_info_permissions: ["read", "write", "admin"]
```

### Object Arrays
Arrays containing objects are flattened with numeric indices:
```json
"connections": [
  {"id": "conn1", "status": "active"},
  {"id": "conn2", "status": "inactive"}
]
```
Becomes:
```
_NB_connections_0_id: "conn1"
_NB_connections_0_status: "active"
_NB_connections_1_id: "conn2"
_NB_connections_1_status: "inactive"
```

## Graylog Search Examples

### Basic Searches
```
# All events for n2con tenant
_NB_tenant:"n2con"

# All connection events
_NB_event_type:"connection"

# Events by specific user
_NB_InitiatorID:"john.doe@n2con.com"
```

### Network-based Searches
```
# TCP connections only
_NB_meta_protocol:"TCP"

# Connections from specific source
_NB_meta_source_addr:"192.168.1.*"

# SSH connections (port 22)
_NB_meta_port:"22"

# Encrypted connections
_NB_meta_connection_info_encrypted:"true"
```

### User and Geographic Searches
```
# Admin user actions
_NB_meta_user_info_username:"admin" OR _NB_meta_user_info_role:"administrator"

# US-based connections
_NB_additional_data_geo_location_country:"US"

# Linux systems
_NB_additional_data_device_info_os:"Linux"

# Specific user groups
_NB_user_groups:*"vpn-users"*
```

### Advanced Filtering
```
# High-bandwidth connections (>1MB transferred)
_NB_meta_bytes_sent:>1048576 OR _NB_meta_bytes_received:>1048576

# Connection duration over 5 minutes
_NB_meta_duration_seconds:>300

# WireGuard connections
_NB_meta_protocol:"WireGuard"
```

### Time-based Analysis
```
# Events in last hour with specific source
_NB_meta_source_addr:"10.0.1.100" AND timestamp:[now-1h TO now]

# Daily connection patterns for user
_NB_InitiatorID:"user@example.com" AND timestamp:[now-24h TO now]
```

## Graylog Dashboard Widgets

### Connection Volume by Protocol
```
# Aggregation: Terms
# Field: _NB_meta_protocol
# Size: 10
```

### Geographic Distribution
```
# Aggregation: Terms  
# Field: _NB_additional_data_geo_location_country
# Size: 20
```

### Top Users by Event Count
```
# Aggregation: Terms
# Field: _NB_InitiatorID
# Size: 15
```

### Encryption Usage
```
# Aggregation: Terms
# Field: _NB_meta_connection_info_encrypted
# Size: 2
```

## Field Discovery

Use the test script to see what fields are generated from your events:

```bash
# Run the field flattening test
./test_flattening.py

# Or send a test event and check logs
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d @sample_event.json \
     http://localhost:8001/events

# Check what fields were created
docker logs nb_streamer | grep "All event fields"
```

## Benefits

### 1. Enhanced Searchability
- Each nested field becomes individually searchable
- No need to parse JSON strings in search queries
- Better performance for complex queries

### 2. Improved Analytics
- Easy aggregation on specific fields
- Better dashboard visualizations
- Simplified alert creation

### 3. Better Field Discovery
- All fields visible in Graylog field list
- Auto-completion in search interface
- Clear field naming convention

### 4. Flexible Querying
- Range queries on numeric fields
- Wildcard searches on text fields
- Combination queries across multiple dimensions

## Migration from JSON Fields

If you were previously using the JSON string format:

### Before (v0.1.0)
```
_NB_meta: "{\"source_addr\":\"10.0.1.100\",\"port\":22}"
```

### After (v0.2.1)
```
_NB_meta_source_addr: "10.0.1.100"
_NB_meta_port: "22"
```

### Search Migration
```
# Old way (searching within JSON)
_NB_meta:*"source_addr":"10.0.1.100"*

# New way (direct field search)
_NB_meta_source_addr:"10.0.1.100"
```

## Performance Considerations

1. **Field Count**: More fields per message (typically 15-30 vs 5-10)
2. **Index Size**: Slightly larger due to individual field indexing
3. **Query Speed**: Faster for specific field queries
4. **Memory Usage**: Minimal increase in processing memory

## Troubleshooting

### Missing Fields
- Check event structure in `full_message` field
- Verify field names match expected patterns
- Look for null or empty values (automatically filtered)

### Unexpected Field Names
- Review flattening logic for complex nested structures
- Check for special characters in original field names
- Arrays may create indexed field names

### Field Value Issues
- All values converted to strings for GELF compatibility
- Boolean values become "true"/"false" strings
- Numeric values remain as string representations

## Custom Field Processing

The flattening function can be customized by modifying `src/models/gelf.py`:

```python
# Skip certain fields from flattening
SKIP_FLATTEN = ['internal_metadata', 'debug_info']

# Custom field name transformations
FIELD_MAPPINGS = {
    'source_addr': 'src_ip',
    'destination_addr': 'dst_ip'
}
```

This enables organization-specific field naming conventions while maintaining the benefits of field flattening.
