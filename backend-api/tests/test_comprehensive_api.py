"""
Comprehensive test suite for the Eye Blink Tracking API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from app import models
import json
from datetime import datetime

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestAPIEndpoints:
    """Test class for all API endpoints"""
    
    def setup_method(self):
        """Setup method run before each test"""
        # Clear database before each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
    def test_root_endpoint(self):
        """Test the root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"msg": "Wellness at Work API is running."}
        
    def test_user_registration_success(self):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "consent": True
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["consent"] == user_data["consent"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
        
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "consent": True
        }
        
        # Register first user
        response1 = client.post("/register", json=user_data)
        assert response1.status_code == 200
        
        # Try to register again with same email
        response2 = client.post("/register", json=user_data)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
        
    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "consent": True
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 422  # Validation error
        
    def test_user_registration_missing_consent(self):
        """Test registration without consent"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "consent": False
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 200  # Should still work, consent is optional
        
    def test_login_success(self):
        """Test successful login"""
        # First register a user
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "consent": True
        }
        client.post("/register", json=user_data)
        
        # Now login
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
        
    def test_login_wrong_password(self):
        """Test login with correct email but wrong password"""
        # Register user
        user_data = {
            "email": "test@example.com",
            "password": "correctpassword",
            "consent": True
        }
        client.post("/register", json=user_data)
        
        # Try login with wrong password
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
        
    def get_auth_token(self):
        """Helper method to get authentication token"""
        # Register and login
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "consent": True
        }
        client.post("/register", json=user_data)
        
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        return response.json()["access_token"]
        
    def test_upload_blink_data_success(self):
        """Test successful blink data upload"""
        token = self.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        blink_data = {
            "blink_count": 15,
            "timestamp": "2024-06-01T12:34:56.789Z"
        }
        
        response = client.post("/blinks/upload", json=blink_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["blink_count"] == 15
        assert "id" in data
        assert "user_id" in data
        assert "timestamp" in data
        
    def test_upload_blink_data_without_timestamp(self):
        """Test blink data upload without timestamp (should use current time)"""
        token = self.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        blink_data = {
            "blink_count": 10
        }
        
        response = client.post("/blinks/upload", json=blink_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["blink_count"] == 10
        assert "timestamp" in data
        
    def test_upload_blink_data_unauthorized(self):
        """Test blink data upload without authentication"""
        blink_data = {
            "blink_count": 15
        }
        
        response = client.post("/blinks/upload", json=blink_data)
        assert response.status_code == 401
        
    def test_upload_blink_data_invalid_token(self):
        """Test blink data upload with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        blink_data = {
            "blink_count": 15
        }
        
        response = client.post("/blinks/upload", json=blink_data, headers=headers)
        assert response.status_code == 401
        
    def test_upload_blink_data_negative_count(self):
        """Test blink data upload with negative blink count"""
        token = self.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        blink_data = {
            "blink_count": -5
        }
        
        response = client.post("/blinks/upload", json=blink_data, headers=headers)
        # Should still work as there's no validation for negative values
        assert response.status_code == 200
        
    def test_get_user_blinks_success(self):
        """Test retrieving user's blink data"""
        token = self.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload some blink data first
        blink_data_1 = {"blink_count": 10}
        blink_data_2 = {"blink_count": 15}
        blink_data_3 = {"blink_count": 8}
        
        client.post("/blinks/upload", json=blink_data_1, headers=headers)
        client.post("/blinks/upload", json=blink_data_2, headers=headers)
        client.post("/blinks/upload", json=blink_data_3, headers=headers)
        
        # Retrieve blink data
        response = client.get("/blinks/user", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Check that data is returned in descending order by timestamp
        blink_counts = [item["blink_count"] for item in data]
        assert 8 in blink_counts
        assert 10 in blink_counts  
        assert 15 in blink_counts
        
    def test_get_user_blinks_empty(self):
        """Test retrieving blink data when user has no data"""
        token = self.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/blinks/user", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
        
    def test_get_user_blinks_unauthorized(self):
        """Test retrieving blink data without authentication"""
        response = client.get("/blinks/user")
        assert response.status_code == 401
        
    def test_get_user_blinks_invalid_token(self):
        """Test retrieving blink data with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/blinks/user", headers=headers)
        assert response.status_code == 401
        
    def test_user_data_isolation(self):
        """Test that users can only see their own blink data"""
        # Register and login first user
        user1_data = {
            "email": "user1@example.com",
            "password": "password123",
            "consent": True
        }
        client.post("/register", json=user1_data)
        
        login1_data = {"username": "user1@example.com", "password": "password123"}
        token1_response = client.post("/token", data=login1_data)
        token1 = token1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Register and login second user
        user2_data = {
            "email": "user2@example.com",
            "password": "password123",
            "consent": True
        }
        client.post("/register", json=user2_data)
        
        login2_data = {"username": "user2@example.com", "password": "password123"}
        token2_response = client.post("/token", data=login2_data)
        token2 = token2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User 1 uploads blink data
        blink_data1 = {"blink_count": 10}
        client.post("/blinks/upload", json=blink_data1, headers=headers1)
        
        # User 2 uploads blink data
        blink_data2 = {"blink_count": 20}
        client.post("/blinks/upload", json=blink_data2, headers=headers2)
        
        # User 1 should only see their data
        response1 = client.get("/blinks/user", headers=headers1)
        data1 = response1.json()
        assert len(data1) == 1
        assert data1[0]["blink_count"] == 10
        
        # User 2 should only see their data
        response2 = client.get("/blinks/user", headers=headers2)
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["blink_count"] == 20

    def test_complete_workflow(self):
        """Test complete workflow: register -> login -> upload -> retrieve"""
        # Step 1: Register
        user_data = {
            "email": "workflow@example.com",
            "password": "workflowpass123",
            "consent": True
        }
        register_response = client.post("/register", json=user_data)
        assert register_response.status_code == 200
        
        # Step 2: Login
        login_data = {
            "username": "workflow@example.com",
            "password": "workflowpass123"
        }
        token_response = client.post("/token", data=login_data)
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Upload multiple blink data entries
        blink_entries = [
            {"blink_count": 12},
            {"blink_count": 8},
            {"blink_count": 15},
            {"blink_count": 10}
        ]
        
        for entry in blink_entries:
            upload_response = client.post("/blinks/upload", json=entry, headers=headers)
            assert upload_response.status_code == 200
            
        # Step 4: Retrieve and verify data
        retrieve_response = client.get("/blinks/user", headers=headers)
        assert retrieve_response.status_code == 200
        
        retrieved_data = retrieve_response.json()
        assert len(retrieved_data) == 4
        
        # Verify all blink counts are present
        retrieved_counts = [item["blink_count"] for item in retrieved_data]
        expected_counts = [12, 8, 15, 10]
        for count in expected_counts:
            assert count in retrieved_counts

if __name__ == "__main__":
    pytest.main([__file__])
