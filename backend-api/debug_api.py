"""
Debug script to test API endpoints and see actual error responses
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_register():
    print("=== Testing Registration ===")
    import random
    email = f"debug{random.randint(1000, 9999)}@example.com"
    user_data = {
        "email": email,
        "password": "testpass123",
        "consent": True
    }
    response = client.post("/register", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return response, email

def test_login(email):
    print("=== Testing Login ===")
    login_data = {
        "username": email,
        "password": "testpass123"
    }
    response = client.post("/token", data=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return response

def test_blink_upload(token):
    print("=== Testing Blink Upload ===")
    headers = {"Authorization": f"Bearer {token}"}
    blink_data = {
        "blink_count": 10
    }
    response = client.post("/blinks/upload", json=blink_data, headers=headers)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response text: {response.text}")
    print()
    return response

def test_get_blinks(token):
    print("=== Testing Get Blinks ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/blinks/user", headers=headers)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response text: {response.text}")
    print()
    return response

def main():
    print("Starting API Debug Tests...")
    print()
    
    # Test registration
    reg_response, email = test_register()
    if reg_response.status_code != 200:
        print("Registration failed, stopping tests")
        return
    
    # Test login
    login_response = test_login(email)
    if login_response.status_code != 200:
        print("Login failed, stopping tests")
        return
    
    token = login_response.json()["access_token"]
    print(f"Got token: {token[:50]}...")
    print()
    
    # Test blink upload
    upload_response = test_blink_upload(token)
    
    # Test get blinks
    get_response = test_get_blinks(token)

if __name__ == "__main__":
    main()
