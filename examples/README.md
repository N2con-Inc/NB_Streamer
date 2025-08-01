# NB_Streamer Examples

This directory contains example files and scripts to help you test and understand NB_Streamer.

## Files

### `test-event.json`
Sample Netbird event in JSON format. This represents the type of data that Netbird would typically send to the `/events` endpoint.

### `curl-test.sh`
Bash script to test your NB_Streamer deployment:
- Performs a health check
- Sends the sample event
- Shows the expected response

## Usage

### Basic Testing

```bash
# Make sure NB_Streamer is running
cd examples/

# Test without authentication
./curl-test.sh

# Test with authentication (edit script to set AUTH_TOKEN)
AUTH_TOKEN="your-token" ./curl-test.sh
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Send test event
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d @test-event.json
```

### Expected GELF Output

The test event will be transformed to GELF format and sent to Graylog:

```json
{
  "version": "1.1",
  "host": "nb_streamer_your-tenant-id",
  "short_message": "Netbird peer_login: connected by john@example.com",
  "timestamp": 1706626800.0,
  "level": 6,
  "facility": "nb_streamer",
  "_NB_tenant": "your-tenant-id",
  "_NB_type": "peer_login",
  "_NB_user": "john@example.com",
  "_NB_peer": "peer-abc-123",
  "_NB_network": "corporate-vpn",
  "_NB_action": "connected",
  "_NB_ip_address": "10.0.0.15",
  "_NB_location": "New York, NY",
  "_NB_device": "laptop-corporate-001",
  "_NB_metadata": "{\"connection_duration\": 0, \"bandwidth_usage\": 0, \"authentication_method\": \"sso\"}"
}
```

## Integration with Netbird

Configure Netbird to send events to your NB_Streamer instance:

```bash
# Netbird webhook configuration
URL: http://your-server:8000/events
Method: POST
Content-Type: application/json
Authorization: Bearer your-token  # if authentication enabled
```