# Container Registry Setup Guide

## GitHub Container Registry (ghcr.io) Setup

### Prerequisites
- GitHub account with repository access
- Docker installed and running
- Git repository pushed to GitHub

### 1. Create Personal Access Token (PAT)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `write:packages` (to push images)
   - `read:packages` (to pull images)
   - `delete:packages` (optional, to delete images)
4. Copy the generated token securely

### 2. Docker Login to GitHub Container Registry

```bash
# Login using your GitHub username and PAT as password
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Or interactively
docker login ghcr.io
# Username: your-github-username
# Password: your-personal-access-token
```

### 3. Environment Variables Setup

Add to your `.env` or shell profile:

```bash
export GITHUB_USERNAME="your-github-username"
export GITHUB_TOKEN="your-personal-access-token"
export IMAGE_REGISTRY="ghcr.io"
export IMAGE_NAMESPACE="$GITHUB_USERNAME"
export IMAGE_NAME="nb-streamer"
```

## Alternative: Docker Hub Setup

### 1. Create Docker Hub Account
Visit https://hub.docker.com and create account

### 2. Docker Login
```bash
docker login
# Username: your-dockerhub-username
# Password: your-dockerhub-password
```

### 3. Environment Variables
```bash
export DOCKERHUB_USERNAME="your-dockerhub-username"
export IMAGE_REGISTRY="docker.io"
export IMAGE_NAMESPACE="$DOCKERHUB_USERNAME"
export IMAGE_NAME="nb-streamer"
```

## Image Naming Convention

Images will be tagged as:
- `ghcr.io/username/nb-streamer:0.3.1`
- `ghcr.io/username/nb-streamer:latest`
- `ghcr.io/username/nb-streamer:main`

## Next Steps

1. Configure your environment variables
2. Test authentication with `docker login`
3. Proceed with image building and pushing
