# External Reverse Proxy Configuration

This guide covers deploying NB_Streamer v0.3.0 behind an external reverse proxy for production use.

## Overview

NB_Streamer is designed to operate behind a reverse proxy that:
- Terminates TLS/SSL encryption
- Routes requests to the appropriate tenant endpoints
- Provides load balancing and high availability
- Handles request forwarding with proper headers

## Supported Reverse Proxies

- **nginx** (recommended for simplicity)
- **Traefik** (with automatic Let's Encrypt)
- **HAProxy**
- **Cloudflare**
- **AWS Application Load Balancer (ALB)**
- **Azure Application Gateway**
- **Google Cloud Load Balancer**

## Quick Start

### 1. Deploy NB_Streamer

```bash
# Use the external proxy compose file
docker compose -f docker-compose.external-proxy.yml --env-file .env up -d
```

### 2. Configure Your Reverse Proxy

The reverse proxy should forward requests to `http://127.0.0.1:8080` (or your configured bind address).

## Required Headers

NB_Streamer expects these headers from the reverse proxy when `NB_TRUST_PROXY_HEADERS=true`:

| Header | Purpose | Example |
|--------|---------|---------|
| `Host` | Original hostname | `streamer.example.com` |
| `X-Forwarded-For` | Client IP address | `203.0.113.12` |
| `X-Forwarded-Proto` | Original protocol | `https` |
| `X-Request-ID` | Request correlation (optional) | `req-123abc` |

## Endpoint Routing

### Multi-tenant Endpoints (v0.3.0+)

- `POST /{tenant}/events` - Event ingestion for specific tenant
- `GET /health` - Health check endpoint
- `GET /stats` - Statistics endpoint
- `POST /stats/reset` - Reset statistics (authenticated)
- `GET /tenants` - List tenants (if enabled)

### Legacy Endpoints (backward compatibility)

- `POST /events` - Legacy event ingestion (deprecated)

## Configuration Examples

### nginx Configuration

```nginx
# /etc/nginx/sites-available/nb-streamer
upstream nb_streamer {
    server 127.0.0.1:8080;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name streamer.example.com;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy configuration
    location / {
        proxy_pass http://nb_streamer;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings for large requests
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Health check endpoint (for load balancer probes)
    location /health {
        access_log off;
        proxy_pass http://nb_streamer;
        proxy_set_header Host $host;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name streamer.example.com;
    return 301 https://$server_name$request_uri;
}
```

### HAProxy Configuration

```haproxy
# /etc/haproxy/haproxy.cfg
global
    daemon
    log stdout local0
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy

defaults
    mode http
    log global
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client 50000
    timeout server 50000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

frontend nb_streamer_frontend
    bind *:443 ssl crt /path/to/cert.pem
    redirect scheme https if !{ ssl_fc }
    
    # Security headers
    http-response set-header X-Frame-Options DENY
    http-response set-header X-Content-Type-Options nosniff
    
    # Forward to backend
    default_backend nb_streamer_backend

backend nb_streamer_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    # Forward headers
    http-request set-header X-Forwarded-Proto https
    http-request add-header X-Forwarded-For %[src]
    
    server nb-streamer-1 127.0.0.1:8080 check inter 10s
```

### Traefik Configuration (Docker Labels)

If you prefer Traefik with automatic service discovery:

```yaml
# docker-compose.traefik.yml (see Phase 8 for full implementation)
services:
  nb-streamer:
    image: nb-streamer:0.3.0
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nb.rule=Host(`streamer.example.com`)"
      - "traefik.http.routers.nb.entrypoints=websecure"
      - "traefik.http.routers.nb.tls.certresolver=letsencrypt"
      - "traefik.http.services.nb.loadbalancer.server.port=8080"
      - "traefik.http.routers.nb.middlewares=secure-headers"
      
      # Health check
      - "traefik.http.services.nb.loadbalancer.healthcheck.path=/health"
      - "traefik.http.services.nb.loadbalancer.healthcheck.interval=10s"
```

## Cloud Load Balancer Examples

### AWS Application Load Balancer

```yaml
# ALB Configuration (CloudFormation/Terraform)
TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Port: 8080
    Protocol: HTTP
    HealthCheckPath: /health
    HealthCheckIntervalSeconds: 10
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 3

LoadBalancer:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Type: application
    Scheme: internet-facing
    SecurityGroups: [!Ref ALBSecurityGroup]
    Subnets: [!Ref PublicSubnet1, !Ref PublicSubnet2]

Listener:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    DefaultActions:
      - Type: forward
        TargetGroupArn: !Ref TargetGroup
    LoadBalancerArn: !Ref LoadBalancer
    Port: 443
    Protocol: HTTPS
    Certificates:
      - CertificateArn: !Ref SSLCertificate
```

### Google Cloud Load Balancer

```yaml
# gcloud configuration
# Create backend service
gcloud compute backend-services create nb-streamer-backend \
    --protocol=HTTP \
    --port-name=http \
    --health-checks=nb-streamer-health \
    --global

# Create URL map
gcloud compute url-maps create nb-streamer-map \
    --default-backend-service=nb-streamer-backend

# Create HTTPS proxy
gcloud compute target-https-proxies create nb-streamer-proxy \
    --url-map=nb-streamer-map \
    --ssl-certificates=nb-streamer-ssl

# Create forwarding rule
gcloud compute forwarding-rules create nb-streamer-rule \
    --address=nb-streamer-ip \
    --global \
    --target-https-proxy=nb-streamer-proxy \
    --ports=443
```

## Health Checks

Configure your load balancer to perform health checks:

- **Path**: `/health`
- **Method**: `GET`
- **Expected Status**: `200`
- **Timeout**: `5s`
- **Interval**: `10s`
- **Healthy Threshold**: `2`
- **Unhealthy Threshold**: `3`

### Example Health Response

```json
{
  "status": "healthy",
  "service": "nb_streamer", 
  "version": "0.3.0",
  "multi_tenancy": true,
  "tenants_count": 2,
  "legacy_events_enabled": true
}
```

## Security Considerations

### Network Security

```bash
# Only allow reverse proxy access to NB_Streamer
# Bind to localhost only
NB_BIND_HOST=127.0.0.1
NB_BIND_PORT=8080
```

### Firewall Rules

```bash
# Example iptables rules
# Allow incoming HTTPS
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow local access to NB_Streamer
iptables -A INPUT -i lo -j ACCEPT

# Block direct access to NB_Streamer from external
iptables -A INPUT -p tcp --dport 8080 -s ! 127.0.0.1 -j DROP
```

### Rate Limiting

Implement rate limiting at the reverse proxy level:

```nginx
# nginx rate limiting
http {
    limit_req_zone $binary_remote_addr zone=events:10m rate=10r/s;
    
    server {
        location ~ ^/[^/]+/events$ {
            limit_req zone=events burst=20 nodelay;
            proxy_pass http://nb_streamer;
        }
    }
}
```

## Monitoring

### Access Logs

Configure your reverse proxy to log requests:

```nginx
# nginx log format
log_format nb_streamer '$remote_addr - $remote_user [$time_local] '
                      '"$request" $status $body_bytes_sent '
                      '"$http_referer" "$http_user_agent" '
                      '$request_time $upstream_response_time '
                      '"$http_x_request_id" "$upstream_addr"';

access_log /var/log/nginx/nb-streamer.log nb_streamer;
```

### Metrics Collection

Monitor key metrics:
- Request rate by tenant
- Response times
- Error rates (4xx, 5xx)
- Health check success rate
- Backend connection status

## Troubleshooting

### Common Issues

**503 Service Unavailable**
- Check NB_Streamer container is running: `docker ps`
- Verify port binding: `netstat -tlnp | grep 8080`
- Check health endpoint: `curl http://127.0.0.1:8080/health`

**Tenant Not Found (404)**
- Verify tenant is in `NB_TENANTS` list
- Check URL path format: `/tenant/events` not `/tenant/event`
- Review logs: `docker logs nb-streamer-mt`

**Authentication Failed (401)**
- Confirm `NB_AUTH_TOKEN` is correctly configured
- Check `Authorization: Bearer <token>` header
- Verify reverse proxy forwards auth headers

### Debug Mode

Enable debug logging temporarily:

```bash
# Update environment and restart
echo "NB_LOG_LEVEL=DEBUG" >> .env
docker compose -f docker-compose.external-proxy.yml restart
```

### Test Endpoints

```bash
# Health check
curl -i https://streamer.example.com/health

# Test tenant endpoint (with auth)
curl -i -X POST https://streamer.example.com/n2con/events \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"test": "event"}'
```

---

**Version**: 0.3.0  
**Last Updated**: 2025-08-28
