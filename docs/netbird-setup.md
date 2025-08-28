# NetBird Webhook Configuration for NB_Streamer

This guide explains how to configure NetBird to send events to NB_Streamer with proper tenant identification.

## Overview

NB_Streamer uses a simplified architecture where all NetBird instances send events to the same endpoint (`/events`) but include tenant identification directly in the JSON payload.

## Configuration Steps

### 1. Access NetBird Console
1. Log into your NetBird Management Console
2. Navigate to **Settings** → **Integrations** → **Webhooks**
3. Add or edit your webhook configuration

### 2. Configure Webhook URL
Set the webhook URL to your NB_Streamer endpoint:
```
https://your-nb-streamer-host.com/events
```

### 3. Configure Authentication
Set the authentication header:
```
Authorization: Bearer your-authentication-token
```

### 4. Customize Body Template
**This is the key step for tenant identification.**

In the NetBird webhook configuration, look for "Customize the body template" option. Replace the default template with the following, customizing the `NB_Tenant` field for each NetBird instance:

#### For Tenant "n2con":
```json
{
  "id": "{{.ID}}",
  "timestamp": "{{.Timestamp.Format "2006-01-02T15:04:05.999Z07:00"}}",
  "message": "{{.Message}}",
  "initiator_id": "{{.InitiatorID}}",
  "target_id": "{{.TargetID}}",
  "meta": "{{.Meta}}",
  "NB_Tenant": "n2con"
}
```

#### For Tenant "hassard":
```json
{
  "id": "{{.ID}}",
  "timestamp": "{{.Timestamp.Format "2006-01-02T15:04:05.999Z07:00"}}",
  "message": "{{.Message}}",
  "initiator_id": "{{.InitiatorID}}",
  "target_id": "{{.TargetID}}",
  "meta": "{{.Meta}}",
  "NB_Tenant": "hassard"
}
```

#### For Other Tenants:
Simply replace `"NB_Tenant": "your-tenant-name"` with your specific tenant identifier.

### 5. Test Configuration
After saving the configuration, use NetBird's "Test" feature to verify the webhook works correctly.

## Important Notes

- **All NetBird instances use the same webhook URL and authentication token**
- **Tenant identification is done via the `NB_Tenant` field in the JSON payload**
- **The `NB_Tenant` field must contain only alphanumeric characters, hyphens, and underscores**
- **Tenant names are case-insensitive but will be processed in lowercase**

## Troubleshooting

### Common Issues:
1. **401 Unauthorized**: Check that the Bearer token is correctly configured
2. **400 Bad Request**: Verify the JSON template is valid
3. **Events not appearing**: Ensure `NB_Tenant` field is included and not empty

### Testing:
You can test your configuration with curl:
```bash
curl -X POST -H "Authorization: Bearer your-token" \
     -H "Content-Type: application/json" \
     -d '{"message":"Test event","NB_Tenant":"your-tenant"}' \
     https://your-nb-streamer-host.com/events
```

## Multiple NetBird Instances

If you have multiple NetBird deployments (e.g., for different customers, environments, or organizations):

1. Configure each NetBird instance with the **same webhook URL and token**
2. Use **different `NB_Tenant` values** in each body template
3. Events will be automatically routed to the appropriate tenant in your logging system

This approach simplifies management while maintaining proper tenant separation in your logs.
