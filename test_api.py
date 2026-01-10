import asyncio
import httpx
import pytest
from main import app
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_auth_endpoints_exist():
    """Test that auth endpoints are registered"""
    # We expect these endpoints to return 405 (method not allowed) or 422 (validation error)
    # rather than 404 (not found), which indicates they exist
    response = client.get("/api/auth/login")
    # Should not be 404, probably 405 since GET is not allowed
    assert response.status_code != 404

    response = client.get("/api/auth/signup")
    # Should not be 404, probably 405 since GET is not allowed
    assert response.status_code != 404

def test_task_endpoints_exist():
    """Test that task endpoints are registered"""
    # These should return 401 (unauthorized) rather than 404 (not found)
    response = client.get("/api/tasks")
    # Without auth, should return 401, not 404
    assert response.status_code != 404

if __name__ == "__main__":
    test_root_endpoint()
    test_auth_endpoints_exist()
    test_task_endpoints_exist()
    print("All tests passed!")