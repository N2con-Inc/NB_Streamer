#!/bin/bash

# NB_Streamer - Docker Build and Push Script
# Builds the Docker image and pushes it to the configured registry

set -e  # Exit on any error

# Default values - can be overridden by environment variables
IMAGE_REGISTRY="${IMAGE_REGISTRY:-ghcr.io}"
IMAGE_NAMESPACE="${IMAGE_NAMESPACE:-$USER}"
IMAGE_NAME="${IMAGE_NAME:-nb-streamer}"
VERSION="${VERSION:-0.3.1}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"

# Construct image names
FULL_IMAGE_NAME="${IMAGE_REGISTRY}/${IMAGE_NAMESPACE}/${IMAGE_NAME}"
VERSION_TAG="${FULL_IMAGE_NAME}:${VERSION}"
LATEST_TAG="${FULL_IMAGE_NAME}:latest"

echo "🚀 NB_Streamer Docker Build and Push"
echo "=================================="
echo "Registry: ${IMAGE_REGISTRY}"
echo "Namespace: ${IMAGE_NAMESPACE}"
echo "Image: ${IMAGE_NAME}"
echo "Version: ${VERSION}"
echo "Full image name: ${FULL_IMAGE_NAME}"
echo "=================================="

# Check if logged into registry
echo "🔐 Checking registry authentication..."
if ! docker info | grep -q "Registry:"; then
    echo "⚠️  Warning: Docker registry authentication not detected"
    echo "Please run: docker login ${IMAGE_REGISTRY}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build the image
echo "🔨 Building Docker image..."
docker build \
    -t "${VERSION_TAG}" \
    -t "${LATEST_TAG}" \
    -f "${DOCKERFILE}" \
    --target production \
    .

echo "✅ Build completed successfully!"

# Push the images
echo "📤 Pushing images to registry..."
docker push "${VERSION_TAG}"
docker push "${LATEST_TAG}"

echo "🎉 Successfully pushed images:"
echo "  - ${VERSION_TAG}"
echo "  - ${LATEST_TAG}"

# Show image info
echo ""
echo "📋 Image Information:"
docker images "${FULL_IMAGE_NAME}" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"

echo ""
echo "🚀 Images are now available for deployment!"
echo "To pull and run: docker run -p 8080:8080 ${VERSION_TAG}"
