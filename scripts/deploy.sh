#!/bin/bash

# NB_Streamer - Production Deployment Script
# Pulls and deploys the latest image from container registry

set -e

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.production.yml}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-ghcr.io}"
IMAGE_NAMESPACE="${IMAGE_NAMESPACE:-$USER}"
IMAGE_NAME="${IMAGE_NAME:-nb-streamer}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 NB_Streamer Production Deployment"
echo "===================================="
echo "Compose file: ${COMPOSE_FILE}"
echo "Registry: ${IMAGE_REGISTRY}"
echo "Image: ${IMAGE_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your configuration."
    echo "See .env.example for reference."
    exit 1
fi

# Check if logged into registry (for private registries)
echo "🔐 Checking registry access..."
if [[ "${IMAGE_REGISTRY}" == "ghcr.io" ]] || [[ "${IMAGE_REGISTRY}" == *"private"* ]]; then
    if ! docker info | grep -q "Registry:"; then
        echo "⚠️  Warning: You may need to login to the registry"
        echo "Run: docker login ${IMAGE_REGISTRY}"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Pull the latest image
echo "📥 Pulling latest image..."
export IMAGE_REGISTRY IMAGE_NAMESPACE IMAGE_TAG
docker compose -f "${COMPOSE_FILE}" pull

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker compose -f "${COMPOSE_FILE}" down

# Start the new deployment
echo "▶️  Starting new deployment..."
docker compose -f "${COMPOSE_FILE}" up -d

# Wait for health check
echo "🏥 Waiting for health check..."
sleep 10

# Check status
if docker compose -f "${COMPOSE_FILE}" ps | grep -q "healthy\|starting"; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📋 Service Status:"
    docker compose -f "${COMPOSE_FILE}" ps
    echo ""
    echo "📊 Service logs (last 20 lines):"
    docker compose -f "${COMPOSE_FILE}" logs --tail=20
    echo ""
    echo "🌐 Service should be available at: http://localhost:8080"
    echo "🔍 Health check: http://localhost:8080/health"
else
    echo "❌ Deployment failed!"
    echo "📊 Error logs:"
    docker compose -f "${COMPOSE_FILE}" logs
    exit 1
fi
