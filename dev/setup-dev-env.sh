#!/bin/bash
# NB_Streamer Development Environment Setup Script
# Alternative to Docker Compose for environments where Docker is not feasible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Script banner
echo -e "${BLUE}"
echo "=================================================="
echo "  NB_Streamer Development Environment Setup"
echo "=================================================="
echo -e "${NC}"

log_info "Setting up NB_Streamer development environment using Python virtual environment..."

# Check if running in project directory
if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt not found. Please run this script from the NB_Streamer project root directory."
    exit 1
fi

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 is not installed. Please install Python 3.10+ and try again."
    exit 1
fi

python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_major=3
required_minor=10

current_major=$(echo $python_version | cut -d. -f1)
current_minor=$(echo $python_version | cut -d. -f2)

if [ "$current_major" -lt "$required_major" ] || ([ "$current_major" -eq "$required_major" ] && [ "$current_minor" -lt "$required_minor" ]); then
    log_error "Python 3.10+ required. Found: Python $python_version"
    log_info "Please install Python 3.10+ and try again."
    exit 1
fi

log_success "Python $python_version detected"

# Check if virtual environment exists
if [ -d "venv" ]; then
    log_warning "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Removing existing virtual environment..."
        rm -rf venv
    else
        log_info "Using existing virtual environment..."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip --quiet

# Install production dependencies
log_info "Installing production dependencies..."
pip install -r requirements.txt --quiet
log_success "Production dependencies installed"

# Install development dependencies
log_info "Installing development dependencies..."
pip install -r requirements-dev.txt --quiet
log_success "Development dependencies installed"

# Install pre-commit hooks
log_info "Installing pre-commit hooks..."
pre-commit install --hook-type pre-commit --hook-type pre-push
log_success "Pre-commit hooks installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating .env file from template..."
    cp .env.sample .env
    log_success ".env file created"
    log_warning "Please edit .env file with your configuration before starting the application"
else
    log_info ".env file already exists"
fi

# Create necessary directories
log_info "Creating project directories..."
mkdir -p src/models src/services src/utils tests/unit tests/integration tests/e2e notebooks logs
log_success "Project directories created"

# Create basic project files if they don't exist
if [ ! -f "src/__init__.py" ]; then
    touch src/__init__.py
    touch src/models/__init__.py
    touch src/services/__init__.py
    touch src/utils/__init__.py
    touch tests/__init__.py
    touch tests/unit/__init__.py
    touch tests/integration/__init__.py
    touch tests/e2e/__init__.py
    log_success "Python package files created"
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    log_warning "Git repository not initialized."
    read -p "Do you want to initialize a git repository? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        git add .
        git commit -m "Initial commit - development environment setup"
        log_success "Git repository initialized"
    fi
fi

# Success message and next steps
echo -e "${GREEN}"
echo "=================================================="
echo "         Setup Complete Successfully!"
echo "=================================================="
echo -e "${NC}"

log_success "NB_Streamer development environment is ready!"
echo ""
log_info "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "2. Edit your configuration:"
echo "   ${BLUE}nano .env${NC}"
echo ""
echo "3. Start the development server:"
echo "   ${BLUE}python -m uvicorn src.main:app --reload --port 8080${NC}"
echo ""
echo "4. Start JupyterLab (in another terminal with venv activated):"
echo "   ${BLUE}jupyter lab --port 8888${NC}"
echo ""
echo "5. Run tests:"
echo "   ${BLUE}pytest${NC}"
echo ""
echo "6. Run code quality checks:"
echo "   ${BLUE}pre-commit run --all-files${NC}"
echo ""
log_info "Access points once running:"
echo "  - FastAPI app: ${BLUE}http://localhost:8080${NC}"
echo "  - API docs: ${BLUE}http://localhost:8080/docs${NC}"
echo "  - JupyterLab: ${BLUE}http://localhost:8888${NC}"
echo ""
log_warning "Note: This setup doesn't include Graylog. For full integration testing,"
log_warning "consider using the Docker Compose setup instead."
echo ""
log_info "For Docker Compose setup, run: ${BLUE}docker compose up --build${NC}"
echo ""
log_success "Happy coding! 🚀"
