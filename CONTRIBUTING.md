# Contributing to NB_Streamer

Welcome to the NB_Streamer project! This document outlines our development standards, workflows, and guidelines for contributing.

## Table of Contents

- [Development Philosophy](#development-philosophy)
- [Coding Standards](#coding-standards)
- [Branching Strategy](#branching-strategy)
- [Versioning Strategy](#versioning-strategy)
- [Development Environment](#development-environment)
- [Code Review Process](#code-review-process)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)

## Development Philosophy

**Simplicity First**: We prioritize simplicity in design. If any project component grows too complex, we evaluate breaking it into smaller, manageable modules or sub-programs.

**Containerized Development**: Whenever possible, we build and test using Docker images and target Docker Compose for deployment to avoid local environment conflicts.

**Virtual Environments**: For local development needs, always use virtual environments to prevent system-level dependency conflicts.

## Coding Standards

### Python Code Style

#### General Guidelines
- **Python Version**: Minimum Python 3.10+
- **Code Formatting**: Follow PEP 8 standards
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Import Organization**: Use isort for consistent import ordering
- **Type Hints**: Required for all public functions and class methods
- **Docstrings**: Required for all public modules, classes, and functions using Google style

#### Code Quality Tools
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ tests/

# Security scanning
bandit -r app/
```

#### File Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models for request/response
├── auth.py              # Authentication middleware
├── gelf.py              # GELF transformation logic
├── config.py            # Configuration management
└── utils.py             # Utility functions

tests/
├── __init__.py
├── conftest.py          # Pytest configuration and fixtures
├── test_auth.py         # Authentication tests
├── test_gelf.py         # GELF transformation tests
├── test_api.py          # API endpoint tests
└── integration/         # Integration tests
    └── test_e2e.py
```

#### Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Members**: Prefix with single underscore `_private_method`
- **Environment Variables**: `UPPER_SNAKE_CASE`

#### Error Handling
- Use specific exception types rather than generic `Exception`
- Log errors with appropriate context
- Return meaningful HTTP status codes
- Graceful degradation where possible

```python
# Good
try:
    result = process_event(event_data)
except ValidationError as e:
    logger.error(f"Event validation failed: {e}")
    raise HTTPException(status_code=400, detail="Invalid event format")
except GraylogConnectionError as e:
    logger.error(f"Failed to send to Graylog: {e}")
    raise HTTPException(status_code=502, detail="Logging service unavailable")

# Bad
try:
    result = process_event(event_data)
except Exception as e:
    raise HTTPException(status_code=500, detail="Something went wrong")
```

### Configuration Management
- All configuration via environment variables
- No hardcoded secrets or hostnames
- Provide sensible defaults where appropriate
- Validate configuration at startup

### Docker Standards
- Use multi-stage builds for optimization
- Run as non-root user (`USER nobody`)
- Minimal base images (`python:3.10-slim`)
- Health checks for all services
- Proper .dockerignore configuration

## Branching Strategy

We follow a **GitFlow-light** workflow with the following branches:

### Core Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Protected branch, requires PR approval
- **Deployment**: Automatically deploys to production
- **Direct Commits**: Prohibited (except hotfixes)

#### `develop` 
- **Purpose**: Integration branch for ongoing development
- **Protection**: Protected branch, requires PR approval
- **Testing**: All features must pass CI/CD before merge
- **Direct Commits**: Prohibited

### Supporting Branches

#### Feature Branches: `feature/*`
- **Naming**: `feature/issue-number-brief-description`
- **Examples**: 
  - `feature/123-add-bearer-auth`
  - `feature/456-gelf-compression`
- **Source**: Branch from `develop`
- **Merge Target**: `develop` via Pull Request
- **Lifetime**: Temporary, deleted after merge

#### Hotfix Branches: `hotfix/*`
- **Naming**: `hotfix/version-brief-description`
- **Examples**: 
  - `hotfix/1.2.1-fix-auth-bypass`
  - `hotfix/1.1.3-graylog-timeout`
- **Source**: Branch from `main`
- **Merge Target**: Both `main` AND `develop`
- **Lifetime**: Temporary, deleted after merge

### Workflow Examples

#### Feature Development
```bash
# Start feature
git checkout develop
git pull origin develop
git checkout -b feature/789-custom-header-auth

# Development work...
git add .
git commit -m "feat: implement custom header authentication"
git push origin feature/789-custom-header-auth

# Create PR: feature/789-custom-header-auth → develop
```

#### Hotfix Process
```bash
# Emergency fix
git checkout main
git pull origin main
git checkout -b hotfix/1.1.1-fix-memory-leak

# Fix work...
git add .
git commit -m "fix: resolve memory leak in UDP sender"
git push origin hotfix/1.1.1-fix-memory-leak

# Create PRs: 
# 1. hotfix/1.1.1-fix-memory-leak → main
# 2. hotfix/1.1.1-fix-memory-leak → develop
```

## Versioning Strategy

We use **Semantic Versioning (SemVer)** with the following increment rules:

### Version Format: `MAJOR.MINOR.PATCH`

#### Version Increment Rules
- **Bug fixes and tweaks**: `+0.0.1` (PATCH)
- **New features/functions**: `+0.1.0` (MINOR) 
- **Major versions**: `+1.0.0` (MAJOR) - Manual decision only

#### Examples
- `1.2.3` → `1.2.4` (bug fix)
- `1.2.3` → `1.3.0` (new feature)
- `1.2.3` → `2.0.0` (breaking change)

#### Pre-release Versions
- Development: `1.2.0-dev.1`, `1.2.0-dev.2`
- Release Candidates: `1.2.0-rc.1`, `1.2.0-rc.2`
- Alpha/Beta: `1.2.0-alpha.1`, `1.2.0-beta.1`

#### Version Tagging
```bash
# Create and push version tag
git tag -a v1.2.1 -m "Release version 1.2.1: Fix authentication bypass"
git push origin v1.2.1
```

#### Version in Code
Maintain version in `app/__init__.py`:
```python
__version__ = "1.2.1"
```

## Development Environment

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/your-org/NB_Streamer.git
cd NB_Streamer

# Setup development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Run setup for Docker Compose
python setup.py

# Start development environment
docker-compose up -d
```

### Local Development
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Code formatting
make format  # or: black . && isort .

# Type checking
make typecheck  # or: mypy app/
```

## Code Review Process

### Pull Request Requirements

#### Before Creating PR
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated (if applicable)
- [ ] No merge conflicts with target branch
- [ ] Commit messages follow conventional format

#### PR Checklist Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Security
- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] Error handling doesn't leak sensitive information
```

#### Review Criteria
- **Functionality**: Code works as intended
- **Security**: No vulnerabilities introduced
- **Performance**: No significant performance degradation
- **Maintainability**: Code is readable and well-structured
- **Testing**: Adequate test coverage
- **Documentation**: Changes documented appropriately

#### Approval Process
- **Feature PRs**: Require 1 approval
- **Hotfix PRs**: Require 1 approval (can be expedited)
- **Main Branch**: Requires 2 approvals
- **Breaking Changes**: Requires architecture review

## Testing Requirements

### Test Coverage
- **Minimum Coverage**: 80% overall
- **Critical Paths**: 95% coverage required
- **New Features**: 100% coverage required

### Test Types

#### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution (< 1 second per test)

```python
def test_gelf_transformation():
    """Test Netbird event to GELF transformation."""
    netbird_event = {
        "ID": "test-123",
        "Message": "Test event",
        "InitiatorID": "peer-abc"
    }
    
    gelf_message = transform_to_gelf(netbird_event)
    
    assert gelf_message["version"] == "1.1" 
    assert gelf_message["NB_ID"] == "test-123"
    assert gelf_message["short_message"] == "Test event"
```

#### Integration Tests
- Test API endpoints end-to-end
- Test authentication flows
- Test Graylog communication (mocked)

#### Performance Tests
- Load testing with 100+ events/second
- Memory usage validation
- Response time verification (< 100ms)

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_gelf.py

# Integration tests only
pytest tests/integration/

# Performance tests
pytest tests/performance/
```

## Documentation Standards

### Code Documentation
- **Docstrings**: Required for all public functions
- **Inline Comments**: For complex logic only
- **Type Hints**: Required for function signatures

### API Documentation
- Auto-generated via FastAPI/Swagger
- Include request/response examples
- Document authentication requirements
- Error response documentation

### Architecture Documentation  
- Keep ARCHITECTURE.md updated
- Document design decisions
- Include deployment diagrams
- Performance characteristics

### Change Documentation
- Update CHANGELOG.md for each release
- Document breaking changes
- Include migration instructions
- Reference related issues/PRs

## Getting Help

### Resources
- **Project Documentation**: See README.md and docs/
- **API Documentation**: Available at `/docs` when running
- **Architecture**: See ARCHITECTURE.md
- **Issues**: Use GitHub Issues for bugs and feature requests

### Contact
- **Maintainers**: Listed in CODEOWNERS
- **Security Issues**: Use private vulnerability reporting
- **General Questions**: Use GitHub Discussions

---

## Commit Message Format

We follow [Conventional Commits](https://conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix  
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Other changes

### Examples
```bash
feat(auth): add custom header authentication support

fix: resolve memory leak in UDP message sender
Closes #123

docs: update API documentation for /events endpoint

chore: bump dependencies to latest versions
```

---

**Thank you for contributing to NB_Streamer!** 🚀

By following these guidelines, you help maintain code quality and ensure smooth collaboration across the development team.
