# NB_Streamer Deployment Guide

**For testing on another host with real Netbird and Graylog integration**

## 🎯 Quick Deployment Steps

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/NB_Streamer.git
cd NB_Streamer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy and edit configuration
cp .env.sample .env
nano .env  # or your preferred editor
```

**Required configuration for testing:**
```bash
# Graylog Configuration - CHANGE THESE
NB_GRAYLOG_HOST=your-graylog-server.com    # Your actual Graylog server
NB_TENANT_ID=test_environment_tenant       # Unique identifier for this test

# Optional - enable authentication if needed
# NB_AUTH_TYPE=bearer
# NB_AUTH_TOKEN=your-secure-test-token

# Logging for development
NB_LOG_LEVEL=DEBUG    # Shows field discovery information
```

### 3. Test the Service
```bash
# Start the service
python -m src.main

# In another terminal, run tests
python test_nb_streamer.py

# Manual test
curl http://localhost:8000/health
```

### 4. Configure Netbird Integration
Point your Netbird instance to send events to:
```
POST http://your-host:8000/events
Content-Type: application/json
```

If authentication is enabled:
```bash
# Bearer token
Authorization: Bearer your-secure-test-token

# Or basic auth
Authorization: Basic base64(username:password)

# Or custom header
X-Custom-Auth: your-custom-value
```

## 🔧 Production-Like Setup

### Docker Deployment (Recommended)
```bash
# Build Docker image
docker build -t nb_streamer:latest .

# Run with environment file
docker run -d \
  --name nb_streamer \
  --env-file .env \
  -p 8000:8000 \
  nb_streamer:latest
```

### Systemd Service (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/nb_streamer.service
```

```ini
[Unit]
Description=NB_Streamer Netbird Event Service
After=network.target

[Service]
Type=simple
User=nb_streamer
WorkingDirectory=/opt/nb_streamer
Environment=PATH=/opt/nb_streamer/venv/bin
ExecStart=/opt/nb_streamer/venv/bin/python -m src.main
EnvironmentFile=/opt/nb_streamer/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nb_streamer
sudo systemctl start nb_streamer
sudo systemctl status nb_streamer
```

### Nginx Reverse Proxy (Optional)
```nginx
server {
    listen 80;
    server_name nb-streamer.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring and Debugging

### Real-time Logs
```bash
# View service logs
tail -f /var/log/nb_streamer.log

# Or with systemd
journalctl -f -u nb_streamer

# Or with Docker
docker logs -f nb_streamer
```

### Field Discovery
With `NB_LOG_LEVEL=DEBUG`, you'll see field discovery information:
```
INFO - Event contains known fields: ['type', 'timestamp', 'user', 'peer']
DEBUG - All event fields: ['type', 'timestamp', 'user', 'peer', 'ip_address', 'location']
```

This helps you understand what Netbird is actually sending.

### Health Monitoring
```bash
# Check service health
curl http://your-host:8000/health

# Expected response:
{
  "status": "healthy",
  "service": "nb_streamer",
  "version": "0.1.0", 
  "tenant_id": "your-tenant-id"
}
```

### Test Event Injection
```bash
# Send a test event to verify the pipeline
curl -X POST http://your-host:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "type": "test_event",
    "timestamp": "2024-01-31T14:30:00Z",
    "user": "test@example.com",
    "message": "Test event from deployment",
    "test_deployment": true
  }'
```

Then check Graylog for a message with:
- `_NB_tenant`: your configured tenant ID
- `_NB_type`: "test_event"
- `_NB_test_deployment`: true

## 🐛 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check configuration
python -c "from src.config import config; print('Config loaded successfully')"

# Check required environment variables
echo $NB_GRAYLOG_HOST
echo $NB_TENANT_ID
```

**Events not reaching Graylog:**
```bash
# Test Graylog connectivity
nc -u your-graylog-host 12201
# Type a test message and press Enter

# Check Graylog inputs
# Verify GELF UDP input is active on port 12201
```

**Authentication issues:**
```bash
# Test with curl including auth
curl -X POST http://your-host:8000/events \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"test": "auth"}'
```

**Field discovery not working:**
```bash
# Ensure debug logging is enabled
export NB_LOG_LEVEL=DEBUG
python -m src.main
```

### Log Analysis
Key log patterns to watch for:
```bash
# Successful event processing
grep "Successfully forwarded event to Graylog" /var/log/nb_streamer.log

# Field discovery
grep "Event contains known fields" /var/log/nb_streamer.log

# Authentication issues  
grep "Authentication" /var/log/nb_streamer.log

# Transformation errors
grep "Error transforming event" /var/log/nb_streamer.log
```

## 🔐 Security Considerations

### Production Security
1. **Enable authentication:**
   ```bash
   NB_AUTH_TYPE=bearer
   NB_AUTH_TOKEN=generate-strong-random-token
   ```

2. **Use HTTPS proxy:**
   - Deploy behind nginx/traefik with TLS termination
   - Never expose service directly to internet

3. **Network security:**
   - Firewall rules to restrict access
   - VPN or private network access only

4. **Logging security:**
   - Avoid logging sensitive data
   - Rotate logs regularly
   - Monitor for suspicious activity

### Netbird Configuration
Configure Netbird to send events securely:
```json
{
  "webhook_url": "https://nb-streamer.yourdomain.com/events",
  "auth_type": "bearer",
  "auth_token": "your-secure-token",
  "retry_attempts": 3,
  "timeout_seconds": 30
}
```

## 📈 Performance Tuning

### High Volume Deployments
```bash
# Increase worker processes
export NB_WORKERS=4
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Tune message buffer size
export NB_MAX_MESSAGE_SIZE=16384

# Use TCP for reliable delivery
export NB_GRAYLOG_PROTOCOL=tcp
```

### Monitoring Metrics
Key metrics to monitor:
- Request rate to `/events` endpoint
- Response time for event processing
- Error rate in logs
- Graylog message ingestion rate
- Memory and CPU usage

## 🎉 Success Indicators

You'll know the integration is working when:

1. **Service health check passes**
2. **Netbird events appear in NB_Streamer logs** with field discovery info
3. **GELF messages arrive in Graylog** with `_NB_tenant` field
4. **All Netbird fields are prefixed** with `_NB_` in Graylog
5. **Unknown fields are discovered** and logged for future processing

---

**Next Steps After Successful Deployment:**
1. Monitor field discovery logs to understand Netbird's event schema
2. Create Graylog dashboards filtering by `_NB_tenant`  
3. Set up alerting based on specific event types
4. Fine-tune field mappings based on discovered structures
