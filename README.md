# NB_Streamer

A lightweight, simplified service that streams NetBird webhook events to Graylog with automatic tenant identification via event payload.

## Overview

NB_Streamer v0.5.0 uses a simplified single-endpoint architecture where all NetBird instances send events to the same `/events` endpoint, with tenant identification handled via the `NB_Tenant` field in the event payload.

## Key Features

- **Single endpoint architecture**: All NetBird instances use `/events`
- **Payload-based tenant identification**: Uses `NB_Tenant` field in JSON payload
- **Flexible authentication**: Bearer token, basic auth, header auth, or none
- **Real-time event streaming**: Events forwarded to Graylog via GELF
- **Statistics tracking**: Per-tenant event statistics and success rates
- **Health monitoring**: Built-in health checks and metrics
- **Docker support**: Easy containerized deployment

## Quick Start

### 1. Configuration

Copy and customize the environment configuration:

```bash
cp .env.example .env
# Edit .env with your settings
```

Required settings:
```env
NB_GRAYLOG_HOST=your-graylog-server.com
NB_AUTH_TYPE=bearer
NB_AUTH_TOKEN=your-secure-token
```

### 2. NetBird Webhook Configuration

**This is the key difference in v0.5.0**: You must customize NetBird's webhook body template.

In your NetBird Management Console:

1. Go to **Settings** → **Integrations** → **Webhooks**
2. Set webhook URL: `https://your-nb-streamer.com/events`
3. Set authentication: `Authorization: Bearer your-token`
4. **Customize body template** (replace `TENANT-NAME` with your identifier):

```json
{
  "id": "{{.ID}}",
  "timestamp": "{{.Timestamp.Format "2006-01-02T15:04:05.999Z07:00"}}",
  "message": "{{.Message}}",
  "initiator_id": "{{.InitiatorID}}",
  "target_id": "{{.TargetID}}",
  "meta": "{{.Meta}}",
  "NB_Tenant": "TENANT-NAME"
}
```

### 3. Deployment

#### Docker (Recommended)
```bash
docker run -d \
  --name nb-streamer \
  -p 8080:8080 \
  --env-file .env \
  nb-streamer:0.5.0
```

#### From Source
```bash
pip install -r requirements.txt
python -m src.main
```

## API Endpoints

- `POST /events` - Process NetBird webhook events (requires `NB_Tenant` in payload)
- `GET /health` - Health check
- `GET /stats` - Event statistics

## Multiple NetBird Instances

For multiple NetBird deployments (different customers, environments, etc.):

1. **Same webhook URL and token** for all instances
2. **Different `NB_Tenant` values** in each body template:
   - Customer A: `"NB_Tenant": "customer-a"`
   - Customer B: `"NB_Tenant": "customer-b"`  
   - Staging: `"NB_Tenant": "staging"`

Events will be automatically routed to the appropriate tenant in Graylog.

## Architecture Benefits

- **Simplified management**: One endpoint, one token for all NetBird instances
- **Easy scaling**: Add new NetBird instances by just changing the body template
- **Flexible tenant identification**: Tenant names in JSON payload, not URL structure
- **Backward compatible**: Works with any NetBird version that supports custom templates

## Configuration Reference

See [.env.example](./.env.example) for all available configuration options.

### Authentication Types

- `bearer` - Bearer token authentication (recommended)
- `basic` - HTTP Basic authentication
- `header` - Custom header authentication  
- `none` - No authentication (development only)

## Monitoring

- Health check: `GET /health`
- Statistics: `GET /stats` (includes per-tenant metrics)
- Logs: Structured JSON logging to stdout

## Documentation

- [NetBird Setup Guide](docs/netbird-setup.md) - Detailed NetBird webhook configuration
- [.env.example](.env.example) - Complete configuration reference

## Version 0.5.0 Changes

This version represents a major simplification from the multi-tenant complexity of 0.3.x:

- **Removed**: Complex multi-tenant URL routing (`/tenant/events`)
- **Removed**: Per-tenant authentication tokens
- **Removed**: Tenant configuration management
- **Added**: Simple payload-based tenant identification
- **Added**: Single-endpoint architecture
- **Improved**: Easier NetBird configuration management

For multiple NetBird instances, simply customize the webhook body template instead of managing different URLs and tokens.

## License

MIT License - see LICENSE file for details.

## Known Issues & Workarounds

### NetBird Webhook Bug (v0.5.1)

**Issue**: NetBird sends the `meta` field as Go map syntax string instead of JSON object when using custom webhook templates.

**Workaround**: Version 0.5.1 includes automatic parsing of Go map format with HTML entity decoding and timestamp conversion.

**Documentation**: See [NETBIRD_BUG_WORKAROUND.md](./NETBIRD_BUG_WORKAROUND.md) for full details.

**Status**: This workaround will be removed when NetBird fixes the upstream bug.

