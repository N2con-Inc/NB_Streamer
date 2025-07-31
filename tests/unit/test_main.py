"""Unit tests for main FastAPI application.

This is a placeholder test file for the development environment setup.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "NB_Streamer Development Environment"
    assert data["status"] == "Development setup complete"


def test_health_check() -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "nb-streamer-dev"


def test_events_placeholder() -> None:
    """Test the events placeholder endpoint."""
    response = client.post("/events")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Events endpoint placeholder"
    assert data["status"] == "To be implemented in Phase 1"


@pytest.mark.unit
def test_app_creation() -> None:
    """Test that the FastAPI app is created properly."""
    assert app.title == "NB_Streamer"
    assert app.version == "1.0.0"
