# NB_Streamer v0.2.0 Deployment Guide

This guide covers deployment of NB_Streamer v0.2.0 with the new statistics and monitoring features.

## What's New in v0.2.0

- **Event Statistics**: Real-time tracking of event processing metrics
- **Monitoring Endpoints**: New `/stats` and `/stats/reset` API endpoints
- **Monitoring Script**: User-friendly `monitor_nb_streamer.sh` script
- **Enhanced Error Tracking**: Automatic failure categorization and counting
- **Per-tenant Analytics**: Statistics breakdown by tenant ID

## Quick Deployment

### 1. Update Your Repository
```bash
git pull origin main
```

### 2. Update Configuration
```bash
# Copy new sample configuration
cp .env.sample .env

# Edit with your specific settings
nano .env
```

Key configuration updates:
- `NB_TENANT_ID`: Set to your organization identifier (e.g., "n2con")
- `NB_GRAYLOG_HOST`: Your Graylog server IP (e.g., "10.0.1.244")
- `NB_AUTH_TOKEN`: Generate a new secure token

### 3. Deploy with Docker
```bash
# Stop existing container (if running)
docker stop nb_streamer && docker rm nb_streamer

# Rebuild with new features
docker build -t nb_streamer .

# Run with updated configuration
docker run -d --name nb_streamer --env-file .env -p 8001:8000 nb_streamer
```

### 4. Verify New Features
```bash
# Check health
curl http://localhost:8001/health

# View statistics
curl http://localhost:8001/stats | jq

# Use monitoring script
./monitor_nb_streamer.sh
```

## New API Endpoints

### GET /stats
Returns comprehensive event processing statistics:

```bash
curl http://localhost:8001/stats
```

Response example:
```json
{
  "status": "success",
  "statistics": {
    "total_events_received": 83,
    "total_events_forwarded": 83,
    "total_events_failed": 0,
    "success_rate": 1.0,
    "uptime_seconds": 43.2,
    "events_by_tenant": {
      "n2con": {
        "received": 83,
        "forwarded": 83,
        "failed": 0
      }
    },
    "events_by_level": {
      "6": 83
    },
    "last_event_time": "2025-07-31T22:39:38.982695+00:00",
    "current_time": "2025-07-31T22:40:00.123456+00:00"
  }
}
```

### POST /stats/reset
Resets all statistics counters (requires authentication):

```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8001/stats/reset
```

## Monitoring Script Usage

The new `monitor_nb_streamer.sh` script provides user-friendly monitoring:

### Single Check
```bash
./monitor_nb_streamer.sh
```

### Continuous Monitoring
```bash
./monitor_nb_streamer.sh --watch
```

### Script Output Example
```
==================================
      NB_Streamer Monitor         
==================================

✅ Service is healthy

📊 Event Processing Statistics:
   Total Received:  83
   Total Forwarded: 83
   Total Failed:    0

✅ Success Rate:    100%
⏱️  Uptime:          43s
🕐 Last Event:      2025-07-31T22:39:38.982695+00:00

👥 Events by Tenant:
   n2con: 83 received, 83 forwarded, 0 failed

📈 Events by Level:
   Level 6: 83 events

==================================
```

## Production Monitoring Setup

### 1. Automated Health Checks
Set up periodic health checks:

```bash
# Create systemd timer for health checks
sudo systemctl edit --force --full nb-streamer-health.service
```

Service content:
```ini
[Unit]
Description=NB_Streamer Health Check
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/curl -f http://localhost:8001/health
User=monitoring
StandardOutput=journal
```

### 2. Log Monitoring
Monitor Docker logs:

```bash
# Follow real-time logs
docker logs -f nb_streamer

# Check for errors
docker logs nb_streamer 2>&1 | grep ERROR

# Monitor successful forwards
docker logs nb_streamer 2>&1 | grep "Successfully forwarded"
```

### 3. Statistics Collection
Collect statistics for external monitoring:

```bash
#!/bin/bash
# collect_stats.sh - Collect statistics for external monitoring

STATS=$(curl -s http://localhost:8001/stats)
RECEIVED=$(echo "$STATS" | jq -r '.statistics.total_events_received')
FORWARDED=$(echo "$STATS" | jq -r '.statistics.total_events_forwarded')
FAILED=$(echo "$STATS" | jq -r '.statistics.total_events_failed')
SUCCESS_RATE=$(echo "$STATS" | jq -r '.statistics.success_rate')

echo "nb_streamer_events_received $RECEIVED"
echo "nb_streamer_events_forwarded $FORWARDED"
echo "nb_streamer_events_failed $FAILED"
echo "nb_streamer_success_rate $SUCCESS_RATE"
```

## Troubleshooting v0.2.0

### Statistics Not Updating
- Check service logs: `docker logs nb_streamer`
- Verify events are being received: `curl -s http://localhost:8001/stats | jq '.statistics.total_events_received'`
- Test event sending manually

### Monitoring Script Issues
- Ensure script is executable: `chmod +x monitor_nb_streamer.sh`
- Check `jq` is installed: `apt-get install jq`
- Verify service URL in script matches your deployment

### Performance Considerations
- Statistics are stored in memory and reset on service restart
- Thread-safe operations may have minimal performance impact under high load
- Consider statistics reset frequency based on your monitoring needs

## Migration from v0.1.0

If upgrading from v0.1.0:

1. **No Breaking Changes**: All existing functionality remains the same
2. **New Dependencies**: No additional dependencies required
3. **Configuration**: Existing `.env` files work without changes
4. **API Compatibility**: All existing endpoints remain unchanged

### Optional Upgrades
- Add monitoring script to your deployment automation
- Update monitoring systems to use new `/stats` endpoint
- Configure alerts based on success rate thresholds

## Docker Compose Update

Updated `docker-compose.yml` for v0.2.0:

```yaml
version: '3.8'
services:
  nb_streamer:
    build: .
    ports:
      - "8001:8000"
    environment:
      - NB_TENANT_ID=n2con
      - NB_GRAYLOG_HOST=10.0.1.244
      - NB_AUTH_TOKEN=${NB_AUTH_TOKEN}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./monitor_nb_streamer.sh:/app/monitor_nb_streamer.sh:ro
```

## Security Notes

- Statistics endpoints are publicly accessible (no sensitive data exposed)
- Statistics reset requires authentication
- Consider rate limiting for statistics endpoints in high-traffic environments
- Monitor authentication failures via statistics

## Support

For v0.2.0 specific issues:
- Check the new statistics for error patterns
- Use the monitoring script for real-time diagnostics
- Review the CHANGELOG.md for detailed changes
- Create GitHub issues with statistics output for better troubleshooting
