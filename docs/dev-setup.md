# NB_Streamer Development Environment Setup

This document provides comprehensive instructions for setting up the NB_Streamer development environment using Docker Compose with an integrated Graylog stack for testing.

## Quick Start (Docker Compose - Recommended)

### Prerequisites

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git** for version control
- At least **4GB RAM** available for containers

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd NB_Streamer

# Copy environment configuration
cp .env.sample .env

# Edit .env file with your preferred settings
# The defaults work for development
```

### 2. Build and Start Development Environment

```bash
# Build and start all services (NB_Streamer + Graylog stack)
docker compose up --build

# Or run in background
docker compose up --build -d
```

### 3. Access Development Services

Once all containers are running:

- **JupyterLab**: http://localhost:8888 (no password required)
- **NB_Streamer API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Graylog Web Interface**: http://localhost:9000 (admin/admin)

### 4. Development Workflow

#### Interactive Development

```bash
# Enter the development container
docker compose exec nb-streamer-dev bash

# Run the FastAPI development server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

# Run tests
pytest

# Run code quality checks
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

#### Using JupyterLab

1. Open http://localhost:8888 in your browser
2. Navigate to notebooks in the `/app` directory
3. Create new notebooks for experimentation and prototyping

#### Pre-commit Hooks

Pre-commit hooks are automatically installed when the container starts:

```bash
# Manual installation if needed
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

### 5. Testing Integration

Send test events to your development instance:

```bash
# From inside the container or your host
curl -X POST http://localhost:8080/events \
  -H "Content-Type: application/json" \
  -d '{
    "ID": "test-123",
    "Timestamp": "2025-01-30T12:00:00Z",
    "Message": "Test peer connection",
    "InitiatorID": "peer-abc",
    "TargetID": "peer-def",
    "Meta": {"ip": "10.0.0.1"},
    "Reference": "https://netbird.io/test"
  }'
```

Check Graylog at http://localhost:9000 to see the processed events.

## Alternative Setup (Python Virtual Environment)

If Docker is not feasible, use this Python virtual environment setup:

### Prerequisites

- **Python 3.10+**
- **pip** or **pipenv**

### Setup Script

```bash
#!/bin/bash
# dev-setup.sh - Python virtual environment setup

set -e

echo "Setting up NB_Streamer development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "Error: Python 3.10+ required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing production dependencies..."
pip install -r requirements.txt

echo "Installing development dependencies..."
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.sample .env
    echo "Please edit .env file with your configuration"
fi

echo "Setup complete!"
echo ""
echo "To start development:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start development server: python -m uvicorn src.main:app --reload"
echo "3. Open browser: http://localhost:8080"
echo ""
echo "To run tests: pytest"
echo "To run code quality checks: pre-commit run --all-files"
```

### Manual Virtual Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit
pre-commit install

# Copy environment file
cp .env.sample .env

# Start development server
python -m uvicorn src.main:app --reload --port 8080

# In another terminal (with venv activated)
jupyter lab --port 8888
```

## Environment Configuration

### Core Environment Variables

Edit `.env` file with your configuration:

```bash
# Server Configuration
PORT=8080

# Authentication (for production)
AUTH_TYPE=none  # Options: none, bearer, basic, custom
AUTH_SECRET=your-secret-here
AUTH_CUSTOM_HEADER=X-Custom-Auth

# Graylog Configuration
GRAYLOG_HOST=localhost  # Use 'graylog' for Docker Compose
GRAYLOG_PORT=12201
GRAYLOG_PROTOCOL=udp

# GELF Settings
DEFAULT_HOST=nb-streamer
```

### Docker Compose Environment

When using Docker Compose, the following services are available:

- **nb-streamer-dev**: Main development container
- **graylog**: Log analysis platform
- **mongodb**: Graylog data store
- **elasticsearch**: Graylog search backend

## Development Commands

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only

# Run specific test file
pytest tests/test_specific.py
```

### Container Management

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Rebuild services
docker compose up --build

# View logs
docker compose logs -f nb-streamer-dev

# Shell into development container
docker compose exec nb-streamer-dev bash

# Clean up everything
docker compose down -v --remove-orphans
docker system prune -f
```

## Project Structure

```
NB_Streamer/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                  # Documentation
├── notebooks/             # Jupyter notebooks
├── docker-compose.yml     # Development environment
├── Dockerfile             # Production container
├── Dockerfile.dev         # Development container
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── .env.sample           # Environment template
├── .pre-commit-config.yaml # Code quality hooks
└── pyproject.toml        # Python project configuration
```

## Troubleshooting

### Common Issues

**Container fails to start:**
```bash
# Check logs
docker compose logs

# Rebuild containers
docker compose down
docker compose up --build
```

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :8080
lsof -i :8888
lsof -i :9000

# Modify ports in docker-compose.yml if needed
```

**Graylog not receiving events:**
1. Check Graylog is running: http://localhost:9000
2. Verify GRAYLOG_HOST in .env (should be 'graylog' for Docker Compose)
3. Check container networking: `docker compose logs graylog`

**Permission issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Memory Requirements

The full development stack requires approximately:
- **NB_Streamer**: ~100MB
- **Graylog**: ~1GB
- **Elasticsearch**: ~1.5GB
- **MongoDB**: ~200MB

**Total: ~3GB RAM minimum**

For memory-constrained environments, use the Python virtual environment setup instead.

## Production Deployment

This development environment includes production-ready configurations:

- **Production Dockerfile**: Optimized for deployment
- **Health checks**: Built-in container health monitoring
- **Security**: Non-root user execution
- **Logging**: Structured logging for production monitoring

See deployment documentation for production setup instructions.

---

## Next Steps

1. **Start Development**: Follow the Quick Start guide above
2. **Read Architecture**: Review `ARCHITECTURE.md` for system design
3. **Implement Features**: Begin with Phase 1 tasks from `PROJECT.md`
4. **Write Tests**: Add tests as you develop features
5. **Documentation**: Update docs as you add functionality

Happy coding! 🚀
