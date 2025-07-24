#!/usr/bin/env python3
"""
Final comprehensive API test summary for Eye Blink Tracking API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import json
import random
from datetime import datetime

client = TestClient(app)

class APITestSuite:
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
        
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        print(f"🧪 Running: {test_name}")
        self.test_results["total"] += 1
        
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                self.test_results["passed"] += 1
                self.test_results["details"].append(f"✅ {test_name}")
            else:
                print(f"❌ FAILED: {test_name}")
                self.test_results["failed"] += 1
                self.test_results["details"].append(f"❌ {test_name}")
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.test_results["failed"] += 1
            self.test_results["details"].append(f"❌ {test_name} - ERROR: {str(e)}")
        
        print()
    
    def test_root_endpoint(self):
        """Test root health check endpoint"""
        response = client.get("/")
        return response.status_code == 200 and response.json()["msg"] == "Wellness at Work API is running."
    
    def test_user_registration(self):
        """Test user registration functionality"""
        email = f"test{random.randint(10000, 99999)}@example.com"
        user_data = {
            "email": email,
            "password": "testpass123",
            "consent": True
        }
        response = client.post("/register", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            return (data["email"] == email and 
                   data["consent"] == True and 
                   "id" in data and 
                   "created_at" in data)
        return False
    
    def test_duplicate_registration(self):
        """Test duplicate email registration handling"""
        email = f"duplicate{random.randint(10000, 99999)}@example.com"
        user_data = {
            "email": email,
            "password": "testpass123",
            "consent": True
        }
        
        # First registration
        response1 = client.post("/register", json=user_data)
        if response1.status_code != 200:
            return False
            
        # Second registration with same email
        response2 = client.post("/register", json=user_data)
        return response2.status_code == 400 and "already registered" in response2.json()["detail"]
    
    def test_user_login(self):
        """Test user login functionality"""
        # Register user first
        email = f"login{random.randint(10000, 99999)}@example.com"
        user_data = {
            "email": email,
            "password": "loginpass123",
            "consent": True
        }
        reg_response = client.post("/register", json=user_data)
        if reg_response.status_code != 200:
            return False
        
        # Test login
        login_data = {
            "username": email,
            "password": "loginpass123"
        }
        response = client.post("/token", data=login_data)
        
        if response.status_code == 200:
            data = response.json()
            return ("access_token" in data and 
                   data["token_type"] == "bearer" and 
                   len(data["access_token"]) > 0)
        return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        return response.status_code == 401
    
    def test_blink_data_upload_and_retrieval(self):
        """Test complete blink data workflow"""
        # Register and login
        email = f"blink{random.randint(10000, 99999)}@example.com"
        user_data = {
            "email": email,
            "password": "blinkpass123",
            "consent": True
        }
        reg_response = client.post("/register", json=user_data)
        if reg_response.status_code != 200:
            return False
        
        login_data = {"username": email, "password": "blinkpass123"}
        login_response = client.post("/token", data=login_data)
        if login_response.status_code != 200:
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload blink data
        blink_data = {"blink_count": 15}
        upload_response = client.post("/blinks/upload", json=blink_data, headers=headers)
        if upload_response.status_code != 200:
            return False
        
        # Retrieve blink data
        get_response = client.get("/blinks/user", headers=headers)
        if get_response.status_code != 200:
            return False
        
        data = get_response.json()
        return (len(data) == 1 and 
               data[0]["blink_count"] == 15 and 
               "timestamp" in data[0])
    
    def test_unauthorized_access(self):
        """Test that endpoints require proper authentication"""
        # Test upload without auth
        blink_data = {"blink_count": 10}
        upload_response = client.post("/blinks/upload", json=blink_data)
        
        # Test get without auth
        get_response = client.get("/blinks/user")
        
        return (upload_response.status_code == 401 and 
               get_response.status_code == 401)
    
    def test_invalid_token(self):
        """Test handling of invalid JWT tokens"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        upload_response = client.post("/blinks/upload", 
                                    json={"blink_count": 10}, 
                                    headers=headers)
        get_response = client.get("/blinks/user", headers=headers)
        
        return (upload_response.status_code == 401 and 
               get_response.status_code == 401)
    
    def test_user_data_isolation(self):
        """Test that users can only access their own data"""
        # Create two users
        email1 = f"user1_{random.randint(10000, 99999)}@example.com"
        email2 = f"user2_{random.randint(10000, 99999)}@example.com"
        
        # Register users
        for email in [email1, email2]:
            user_data = {"email": email, "password": "password123", "consent": True}
            response = client.post("/register", json=user_data)
            if response.status_code != 200:
                return False
        
        # Login both users
        tokens = {}
        for email in [email1, email2]:
            login_data = {"username": email, "password": "password123"}
            response = client.post("/token", data=login_data)
            if response.status_code != 200:
                return False
            tokens[email] = response.json()["access_token"]
        
        # User 1 uploads data
        headers1 = {"Authorization": f"Bearer {tokens[email1]}"}
        upload_response = client.post("/blinks/upload", 
                                    json={"blink_count": 10}, 
                                    headers=headers1)
        if upload_response.status_code != 200:
            return False
        
        # User 2 uploads data
        headers2 = {"Authorization": f"Bearer {tokens[email2]}"}
        upload_response = client.post("/blinks/upload", 
                                    json={"blink_count": 20}, 
                                    headers=headers2)
        if upload_response.status_code != 200:
            return False
        
        # Check that each user sees only their data
        get_response1 = client.get("/blinks/user", headers=headers1)
        get_response2 = client.get("/blinks/user", headers=headers2)
        
        if get_response1.status_code != 200 or get_response2.status_code != 200:
            return False
        
        data1 = get_response1.json()
        data2 = get_response2.json()
        
        return (len(data1) == 1 and data1[0]["blink_count"] == 10 and
               len(data2) == 1 and data2[0]["blink_count"] == 20)
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting comprehensive API test suite...")
        print("=" * 60)
        
        # Run all tests
        self.run_test("Root Endpoint Health Check", self.test_root_endpoint)
        self.run_test("User Registration", self.test_user_registration)
        self.run_test("Duplicate Registration Handling", self.test_duplicate_registration)
        self.run_test("User Login", self.test_user_login)
        self.run_test("Invalid Login Handling", self.test_invalid_login)
        self.run_test("Blink Data Upload and Retrieval", self.test_blink_data_upload_and_retrieval)
        self.run_test("Unauthorized Access Protection", self.test_unauthorized_access)
        self.run_test("Invalid Token Handling", self.test_invalid_token)
        self.run_test("User Data Isolation", self.test_user_data_isolation)
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ PASSED: {self.test_results['passed']}")
        print(f"❌ FAILED: {self.test_results['failed']}")
        print(f"📈 TOTAL:  {self.test_results['total']}")
        print(f"🎯 SUCCESS RATE: {(self.test_results['passed']/self.test_results['total']*100):.1f}%")
        print()
        
        print("📋 DETAILED RESULTS:")
        for detail in self.test_results['details']:
            print(f"   {detail}")
        
        print()
        if self.test_results['failed'] == 0:
            print("🎉 ALL TESTS PASSED! Your API is working perfectly!")
        else:
            print(f"⚠️  {self.test_results['failed']} test(s) failed. Review the issues above.")
        
        print("=" * 60)

def main():
    """Main test execution"""
    test_suite = APITestSuite()
    test_suite.run_all_tests()
    
    print()
    print("🔗 API ENDPOINTS SUMMARY:")
    print("   GET  /                - Health check")
    print("   POST /register        - User registration")  
    print("   POST /token           - User login (get JWT)")
    print("   POST /blinks/upload   - Upload blink data (requires auth)")
    print("   GET  /blinks/user     - Get user's blink data (requires auth)")
    print()
    print("📖 For interactive testing, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
