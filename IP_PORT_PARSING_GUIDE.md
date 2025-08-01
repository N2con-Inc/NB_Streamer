# IP and Port Separation Guide

NB_Streamer v0.2.6 introduces IP and port separation for fields with IP:port combinations.

## Overview

Netbird events often have fields with combined IP and port values (e.g., `source_addr`, `destination_addr`). Version v0.2.6 parses these fields and splits them into separate IP and port fields with `_NB_` prefixing for better searchability and analysis in Graylog.

## Key Enhancements

- **IPv4 and IPv6 Support**: Automatically parse IP:port combinations for both IPv4 (`192.168.1.1:80`) and IPv6 (`[2001:db8::1]:443`) addresses.
- **Separate Fields**: Create `_NB_` prefixed fields for IPs and ports (e.g., `_NB_meta_source_addr`, `_NB_meta_source_port`).
- **Dynamic Parsing**: Handles various naming patterns like `source_addr`, `remote_host`, `peer_address`, etc.

## Field Patterns

### Common Address Patterns
| Combined Field | IP Field | Port Field |
|----------------|----------|------------|
| `source_addr`  | `_NB_meta_source_addr` | `_NB_meta_source_port` |
| `destination_addr` | `_NB_meta_destination_addr` | `_NB_meta_destination_port` |
| `remote_addr` | `_NB_network_data_remote_addr` | `_NB_network_data_remote_port` |
| `local_addr` | `_NB_network_data_local_addr` | `_NB_network_data_local_port` |
| `peer_addr` | `_NB_network_data_peer_addr` | `_NB_network_data_peer_port` |
| `client_addr` | `_NB_additional_info_client_addr` | `_NB_additional_info_client_port` |

## Graylog Search Examples

### IP-based Filtering
- Find all events from a specific source IP
  ```
  _NB_meta_source_addr:"192.168.68.141"
  ```

- Filter events within a subnet
  ```
  _NB_meta_source_addr:"192.168.68.*"
  ```

- Search for events with specific destination IP
  ```
  _NB_meta_destination_addr:"10.0.1.244"
  ```

### Port-based Filtering
- Find all events connecting to port 80
  ```
  _NB_meta_destination_port:"80"
  ```  

- Identify SSH connections (port 22)
  ```
  _NB_network_data_peer_port:"22"
  ```

- Select high port numbers (ephemeral ports)
  ```
  _NB_meta_source_port:>49152
  ```

### Combined Filtering
- Combine IP and port filters
  ```
  _NB_meta_source_addr:"192.168.68.*" AND _NB_meta_destination_port:"80"
  ```

- Locate HTTPS traffic (commonly on port 443)
  ```
  _NB_network_data_remote_port:"443"
  ```

## Benefits of IP and Port Parsing

1. **Improved Query Performance**
   - Direct field searches enhance performance compared to parsing JSON strings.

2. **Enhanced Visibility**
   - Clear separation between IP and port fields aids in monitoring and dashboard creation.

3. **Network Security Analysis**
   - Simplifies the audit process and anomaly detection with range queries.
 
4. **Scalable Analysis**
   - Efficient analysis across large volumes of events due to direct indexing of individual fields.

5. **Flexible Dashboard Configuration**
   - Ready-to-use field structure for creating insights and alerting rules based on network activity.

## How it Works

### Example Transformation

#### Input Netbird Event
```json
{
  "meta": {
    "source_addr": "192.168.68.141:54615",
    "destination_addr": "10.0.1.244:80"
  },
  "network_data": {
    "remote_addr": "203.0.113.45:443"
  }
}
```

#### Transformed GELF Fields
- `_NB_meta_source_addr`: "192.168.68.141"
- `_NB_meta_source_port`: "54615"
- `_NB_meta_destination_addr`: "10.0.1.244"
- `_NB_meta_destination_port`: "80"
- `_NB_network_data_remote_addr`: "203.0.113.45"
- `_NB_network_data_remote_port`: "443"

## Troubleshooting

### Missing Fields
- Ensure IP:port format is valid (e.g., `[IPv6]:port` or `IPv4:port`).
- Review logs for parsing errors or unsupported formats.

### Potential Edge Cases
- Addresses without ports remain unchanged.
- Non-standard address fields require manual parsing logic additions.

## Future Enhancements
- [ ] Customizable field mapping for organization-specific naming conventions.
- [ ] Support for additional network protocols and formats.
- [ ] Automatic update of field names based on evolving network standards.

