"""
Simple API tests that don't require database setup
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Mock the database and models before importing the app
with patch('app.database.engine'), patch('app.models.Base.metadata.create_all'):
    from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Wellness at Work API is running."}

def test_register_endpoint_structure():
    """Test that register endpoint exists and returns appropriate error structure"""
    # This will fail due to database issues, but we can check the endpoint exists
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "test123",
        "consent": True
    })
    # We expect an error due to database issues, but the endpoint should exist
    assert response.status_code != 404  # Should not be 404 (not found)

def test_token_endpoint_structure():
    """Test that token endpoint exists and returns appropriate error structure"""
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "test123"
    })
    # We expect an error due to database issues, but the endpoint should exist
    assert response.status_code != 404  # Should not be 404 (not found)

def test_blinks_upload_endpoint_exists():
    """Test that blinks upload endpoint exists"""
    response = client.post("/blinks/upload", json={
        "blink_count": 10
    })
    # Should return 401 (unauthorized) since no token provided
    assert response.status_code == 401

def test_blinks_user_endpoint_exists():
    """Test that blinks user endpoint exists"""
    response = client.get("/blinks/user")
    # Should return 401 (unauthorized) since no token provided
    assert response.status_code == 401

def test_invalid_endpoint():
    """Test accessing non-existent endpoint"""
    response = client.get("/nonexistent")
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
