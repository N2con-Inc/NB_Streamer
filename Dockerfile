# Multi-stage production container for NB_Streamer v0.3.0
FROM python:3.11-slim AS base

# Set environment variables for build efficiency
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/venv/bin:$PATH"

# Build stage - install dependencies
FROM base AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /venv

# Copy and install Python dependencies
COPY requirements.txt ./
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base AS production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Create app directory and non-root user
RUN mkdir -p /app && \
    useradd --create-home --shell /bin/bash --uid 1000 --gid 100 appuser && \
    chown appuser:users /app

WORKDIR /app

# Copy application code with proper ownership
COPY --chown=appuser:users src/ ./src/

# Switch to non-root user for security
USER appuser

# Expose application port - standardized to 8080 for multi-tenancy
EXPOSE 8000

# Enhanced health check with proper timing for production
HEALTHCHECK --interval=10s --timeout=2s --retries=6 --start-period=20s \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Set working directory environment for the app
ENV NB_PORT=8000

# Default command
CMD ["/venv/bin/python", "-m", "src.main"]
