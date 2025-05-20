"""
Integration tests for FastAPI app entrypoint and health check endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """
    Ensures the health check root endpoint returns the expected status and message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smile Detection API is running."}
