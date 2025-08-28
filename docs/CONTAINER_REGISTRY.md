# Container Registry Setup - Complete Guide

This guide walks you through setting up NB_Streamer with pre-built Docker images stored in a container registry.

## 🎯 What You'll Achieve

- **No more local building**: Pull ready-to-use images
- **Faster deployments**: Skip the build process entirely  
- **Consistent environments**: Same image across all deployments
- **Automated builds**: CI/CD pipeline builds images automatically
- **Easy rollbacks**: Switch between image versions instantly

## 🚀 Quick Setup (5 minutes)

### Step 1: Choose Your Registry

**GitHub Container Registry (Recommended - Free)**
```bash
export IMAGE_REGISTRY="ghcr.io"
export IMAGE_NAMESPACE="your-github-username"
```

**Docker Hub**
```bash
export IMAGE_REGISTRY="docker.io"  
export IMAGE_NAMESPACE="your-dockerhub-username"
```

### Step 2: Authentication

**GitHub Container Registry:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create token with `write:packages` and `read:packages` scopes
3. Login to registry:
```bash
echo YOUR_TOKEN | docker login ghcr.io -u your-username --password-stdin
```

**Docker Hub:**
```bash
docker login
# Enter your Docker Hub credentials
```

### Step 3: Build and Push Your First Image

```bash
# Clone and navigate to your repository
cd /path/to/NB_Streamer

# Build and push (one command does it all!)
./scripts/build-and-push.sh
```

### Step 4: Deploy from Registry

```bash
# Deploy using pre-built image
./scripts/deploy.sh
```

Done! Your service is running from the registry image.

## 📁 Files Created

This setup adds these files to your project:

```
scripts/
├── build-and-push.sh      # Build and push images to registry
└── deploy.sh              # Deploy using registry images

docker-compose.production.yml # Production deployment config

.github/workflows/
└── build-and-push.yml     # Automated builds on GitHub

docs/
├── CONTAINER_REGISTRY_SETUP.md  # Registry configuration guide
├── DEPLOYMENT.md               # Deployment guide
└── CONTAINER_REGISTRY.md       # This overview

.env.registry.example      # Registry configuration template
```

## 🔄 Typical Workflow

### Development Workflow
1. Make code changes
2. Push to GitHub
3. GitHub Actions automatically builds and pushes new image
4. Deploy updated image: `./scripts/deploy.sh`

### Production Workflow  
1. Tag a release: `git tag v0.3.1`
2. Push tag: `git push origin v0.3.1`
3. GitHub builds versioned image
4. Deploy specific version: `IMAGE_TAG=0.3.1 ./scripts/deploy.sh`

## 🛠 Available Commands

### Building and Pushing
```bash
# Build and push with defaults
./scripts/build-and-push.sh

# Build specific version
VERSION=0.3.1 ./scripts/build-and-push.sh

# Use different registry
IMAGE_REGISTRY=docker.io IMAGE_NAMESPACE=myuser ./scripts/build-and-push.sh
```

### Deployment
```bash
# Deploy latest
./scripts/deploy.sh

# Deploy specific version  
IMAGE_TAG=0.3.1 ./scripts/deploy.sh

# Use different compose file
COMPOSE_FILE=my-compose.yml ./scripts/deploy.sh
```

### Manual Operations
```bash
# Pull specific image
docker pull ghcr.io/username/nb-streamer:0.3.1

# Run container directly
docker run -p 8080:8080 ghcr.io/username/nb-streamer:latest

# Check available tags
# Visit: https://github.com/users/USERNAME/packages/container/nb-streamer
```

## 🏗 Architecture

### Before (Local Builds)
```
Code Changes → Local Docker Build → Run Container
    ↓              ↓                    ↓
  5-10 mins     Every time          Inconsistent
```

### After (Registry)
```
Code Changes → GitHub Actions → Registry → Pull & Deploy
    ↓              ↓            ↓         ↓
  Push only    Once per change  Stored   Seconds
```

## 🔍 Troubleshooting

### Can't Push to Registry
```bash
# Check login status
docker login ghcr.io

# Verify token has correct permissions
# GitHub: Settings → Developer settings → Personal access tokens
```

### Can't Pull Images
```bash
# Check if image exists
docker pull ghcr.io/username/nb-streamer:latest

# Try different tag
docker pull ghcr.io/username/nb-streamer:main
```

### Deployment Fails
```bash
# Check logs
docker compose -f docker-compose.production.yml logs

# Verify environment file
cat .env
```

## 📊 Registry Comparison

| Feature | GitHub Container Registry | Docker Hub | Private Registry |
|---------|--------------------------|------------|------------------|
| **Cost** | Free for public | Free tier (1 private) | Setup/hosting costs |
| **Privacy** | Public/private repos | Limited private | Full control |
| **Integration** | Excellent with GitHub | Universal | Varies |
| **Reliability** | High | High | Depends on setup |
| **Recommendation** | ✅ Best for most cases | Good for simple projects | Enterprise only |

## 🎉 Benefits You'll See

1. **Faster deployments**: No more waiting for builds
2. **Consistent environments**: Same image everywhere
3. **Easy rollbacks**: `IMAGE_TAG=0.3.0 ./scripts/deploy.sh`
4. **Team collaboration**: Everyone uses same images
5. **CI/CD ready**: Automated builds on code changes

## 🔜 Next Steps

1. **Set up your registry** following Step 1-2 above
2. **Run your first build**: `./scripts/build-and-push.sh`
3. **Deploy from registry**: `./scripts/deploy.sh`  
4. **Set up GitHub Actions** (automatic if using GitHub)
5. **Update your deployment docs** for your team

## 📞 Need Help?

- Check the logs: `./scripts/deploy.sh` shows detailed output
- Verify your setup: All variables in `.env.registry.example`
- Test manually: `docker pull your-registry/nb-streamer:latest`
- GitHub Actions: Check the Actions tab in your repository

Happy deploying! 🚀
