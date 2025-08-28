# NB_Streamer Production Deployment Guide

This guide covers deploying NB_Streamer using pre-built Docker images from a container registry.

## Overview

Instead of building Docker images locally each time, we now:
1. Build images once and push to a container registry
2. Pull pre-built images for deployment
3. Use automated CI/CD for continuous deployment

## Quick Start

### 1. Set Up Container Registry Access

Choose your registry and set up authentication:

#### GitHub Container Registry (Recommended)
```bash
# Set environment variables
export IMAGE_REGISTRY="ghcr.io"
export IMAGE_NAMESPACE="your-github-username"
export GITHUB_TOKEN="your-personal-access-token"

# Login to registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $IMAGE_NAMESPACE --password-stdin
```

#### Docker Hub
```bash
# Set environment variables
export IMAGE_REGISTRY="docker.io"
export IMAGE_NAMESPACE="your-dockerhub-username"

# Login to registry
docker login
```

### 2. Deploy Using Pre-built Images

```bash
# Deploy latest version
./scripts/deploy.sh

# Deploy specific version
IMAGE_TAG=0.3.1 ./scripts/deploy.sh
```

That's it! The service will be available at http://localhost:8080

## Manual Deployment Steps

### 1. Configuration

Create or update your `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings
```

### 2. Pull and Start

```bash
# Pull latest images
docker compose -f docker-compose.production.yml pull

# Start services
docker compose -f docker-compose.production.yml up -d
```

### 3. Verify Deployment

```bash
# Check service status
docker compose -f docker-compose.production.yml ps

# View logs
docker compose -f docker-compose.production.yml logs

# Test health endpoint
curl http://localhost:8080/health
```

## Building and Pushing Images

### Manual Build and Push

```bash
# Set your registry details
export IMAGE_REGISTRY="ghcr.io"
export IMAGE_NAMESPACE="your-username"
export VERSION="0.3.1"

# Build and push
./scripts/build-and-push.sh
```

### Automated with GitHub Actions

1. Push code to GitHub repository
2. GitHub Actions will automatically:
   - Build Docker image
   - Push to GitHub Container Registry
   - Create tags for branches and releases

## Environment Variables

### Registry Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `IMAGE_REGISTRY` | Container registry URL | `ghcr.io` |
| `IMAGE_NAMESPACE` | Registry namespace/username | `myusername` |
| `IMAGE_TAG` | Image tag to deploy | `latest` or `0.3.1` |

### Application Configuration

Use the same `.env` file as before. Key variables:

```bash
# Required
NB_TENANTS=tenant1,tenant2
NB_AUTH_TOKEN=your-secure-token

# Graylog
NB_GRAYLOG_HOST=your-graylog-host
NB_GRAYLOG_PORT=12201

# Optional
NB_LOG_LEVEL=INFO
NB_EXPOSE_TENANTS=false
```

## Deployment Strategies

### Production Deployment

```bash
# Use specific version for stability
IMAGE_TAG=0.3.1 ./scripts/deploy.sh
```

### Staging/Testing

```bash
# Use latest for testing new features
IMAGE_TAG=latest ./scripts/deploy.sh
```

### Rollback

```bash
# Rollback to previous version
IMAGE_TAG=0.3.0 ./scripts/deploy.sh
```

## Monitoring and Maintenance

### Health Checks

The container includes built-in health checks:
```bash
# Check container health
docker compose -f docker-compose.production.yml ps

# Manual health check
curl http://localhost:8080/health
```

### Logs

```bash
# View recent logs
docker compose -f docker-compose.production.yml logs --tail=100

# Follow logs in real-time
docker compose -f docker-compose.production.yml logs -f
```

### Updates

```bash
# Update to latest image
docker compose -f docker-compose.production.yml pull
docker compose -f docker-compose.production.yml up -d
```

## Troubleshooting

### Registry Authentication Issues

```bash
# Re-authenticate
docker login ghcr.io

# Verify authentication
docker info | grep Registry
```

### Image Pull Issues

```bash
# Check if image exists
docker pull ghcr.io/username/nb-streamer:latest

# Use specific tag
IMAGE_TAG=0.3.1 docker compose -f docker-compose.production.yml pull
```

### Container Startup Issues

```bash
# Check container logs
docker compose -f docker-compose.production.yml logs nb-streamer

# Check environment variables
docker compose -f docker-compose.production.yml exec nb-streamer env
```

## Security Considerations

1. **Private Registries**: Use private registries for sensitive applications
2. **Access Tokens**: Securely manage registry access tokens
3. **Image Scanning**: Regularly scan images for vulnerabilities
4. **Network Security**: Configure proper firewall rules
5. **Environment Variables**: Secure sensitive configuration data

## CI/CD Integration

The included GitHub Actions workflow automatically:
- Builds images on code changes
- Pushes to GitHub Container Registry
- Tags images appropriately
- Provides security attestations

### Triggering Deployments

1. **Push to main**: Creates `latest` tag
2. **Create release tag**: Creates version-specific tags
3. **Pull requests**: Creates PR-specific tags for testing

## Performance and Scaling

### Resource Limits

The production compose file includes resource limits:
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

Adjust based on your needs.

### Scaling

For high-traffic deployments, consider:
- Load balancer in front of multiple instances
- Container orchestration (Kubernetes, Docker Swarm)
- Database clustering for Graylog
- Monitoring and alerting

## Support

- Check logs first: `docker compose -f docker-compose.production.yml logs`
- Verify configuration: Review `.env` file
- Test connectivity: `curl http://localhost:8080/health`
- Check GitHub Issues for known problems
