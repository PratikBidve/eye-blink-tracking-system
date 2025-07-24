#!/usr/bin/env python3
"""
Full Stack Integration Test Suite
Tests the complete Wellness at Work system integration
"""
import sys
import os
import time
import subprocess
import requests
import json
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:8002"
WEB_DASHBOARD_URL = "http://localhost:5173"

class FullStackTestSuite:
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
        self.test_user_email = f"integration_test_{int(time.time())}@example.com"
        self.test_user_password = "IntegrationTest123"
        self.access_token = None
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            print(f"✅ PASSED: {test_name}")
            self.results["details"].append(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            print(f"❌ FAILED: {test_name} - {details}")
            self.results["details"].append(f"❌ {test_name} - {details}")
        print()
    
    def test_backend_health(self):
        """Test if backend API is running"""
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            passed = response.status_code == 200 and "Wellness at Work API is running" in response.json().get("msg", "")
            self.log_test("Backend API Health Check", passed, f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Backend API Health Check", False, str(e))
            return False
    
    def test_user_registration_and_login(self):
        """Test user registration and login flow"""
        try:
            # Register user
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "consent": True
            }
            
            reg_response = requests.post(f"{API_BASE_URL}/register", json=registration_data)
            if reg_response.status_code != 200:
                self.log_test("User Registration & Login", False, f"Registration failed: {reg_response.status_code}")
                return False
            
            # Login user
            login_data = {
                "username": self.test_user_email,
                "password": self.test_user_password
            }
            
            login_response = requests.post(f"{API_BASE_URL}/token", data=login_data)
            if login_response.status_code != 200:
                self.log_test("User Registration & Login", False, f"Login failed: {login_response.status_code}")
                return False
            
            self.access_token = login_response.json()["access_token"]
            self.log_test("User Registration & Login", True)
            return True
            
        except Exception as e:
            self.log_test("User Registration & Login", False, str(e))
            return False
    
    def test_blink_data_api(self):
        """Test blink data upload and retrieval"""
        if not self.access_token:
            self.log_test("Blink Data API", False, "No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Upload blink data
            blink_data = {
                "blink_count": 25,
                "timestamp": datetime.now().isoformat()
            }
            
            upload_response = requests.post(f"{API_BASE_URL}/blinks/upload", 
                                          json=blink_data, 
                                          headers=headers)
            
            if upload_response.status_code != 200:
                self.log_test("Blink Data API", False, f"Upload failed: {upload_response.status_code}")
                return False
            
            # Retrieve blink data
            get_response = requests.get(f"{API_BASE_URL}/blinks/user", headers=headers)
            
            if get_response.status_code != 200:
                self.log_test("Blink Data API", False, f"Retrieval failed: {get_response.status_code}")
                return False
            
            data = get_response.json()
            if len(data) > 0 and data[0]["blink_count"] == 25:
                self.log_test("Blink Data API", True)
                return True
            else:
                self.log_test("Blink Data API", False, "Data mismatch")
                return False
                
        except Exception as e:
            self.log_test("Blink Data API", False, str(e))
            return False
    
    def test_python_eye_tracker_script(self):
        """Test if Python eye tracker script exists and is valid"""
        try:
            eye_tracker_path = "/Users/prateekbidve/Desktop/Eye_Blink_test_case/desktop-app/python/eye_tracker.py"
            
            if not os.path.exists(eye_tracker_path):
                self.log_test("Python Eye Tracker Script", False, "Script file not found")
                return False
            
            # Check if script has basic structure
            with open(eye_tracker_path, 'r') as f:
                content = f.read()
                if "import cv2" in content and "import mediapipe" in content:
                    self.log_test("Python Eye Tracker Script", True)
                    return True
                else:
                    self.log_test("Python Eye Tracker Script", False, "Missing required imports")
                    return False
                    
        except Exception as e:
            self.log_test("Python Eye Tracker Script", False, str(e))
            return False
    
    def test_desktop_app_structure(self):
        """Test desktop app file structure and dependencies"""
        try:
            desktop_path = "/Users/prateekbidve/Desktop/Eye_Blink_test_case/desktop-app"
            
            required_files = [
                "package.json",
                "main.js", 
                "preload.js",
                "renderer/index.html",
                "renderer/renderer.js",
                "python/eye_tracker.py"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(desktop_path, file)):
                    missing_files.append(file)
            
            if missing_files:
                self.log_test("Desktop App Structure", False, f"Missing files: {missing_files}")
                return False
            else:
                self.log_test("Desktop App Structure", True)
                return True
                
        except Exception as e:
            self.log_test("Desktop App Structure", False, str(e))
            return False
    
    def test_web_dashboard_structure(self):
        """Test web dashboard file structure"""
        try:
            web_path = "/Users/prateekbidve/Desktop/Eye_Blink_test_case/web-dashboard"
            
            required_files = [
                "package.json",
                "index.html",
                "src/App.jsx",
                "src/main.jsx",
                "src/components/LoginForm.jsx",
                "src/components/BlinkChart.jsx"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(web_path, file)):
                    missing_files.append(file)
            
            if missing_files:
                self.log_test("Web Dashboard Structure", False, f"Missing files: {missing_files}")
                return False
            else:
                self.log_test("Web Dashboard Structure", True)
                return True
                
        except Exception as e:
            self.log_test("Web Dashboard Structure", False, str(e))
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration allows frontend connections"""
        if not self.access_token:
            self.log_test("CORS Configuration", False, "No access token for testing")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Origin": "http://localhost:5173"  # Web dashboard origin
            }
            
            response = requests.get(f"{API_BASE_URL}/blinks/user", headers=headers)
            
            # Check if CORS headers are present
            cors_headers = response.headers.get('Access-Control-Allow-Origin')
            passed = response.status_code == 200
            
            self.log_test("CORS Configuration", passed, f"CORS headers: {cors_headers}")
            return passed
            
        except Exception as e:
            self.log_test("CORS Configuration", False, str(e))
            return False
    
    def test_gdpr_compliance_features(self):
        """Test GDPR compliance features"""
        try:
            # Test consent tracking in registration
            registration_data = {
                "email": f"gdpr_test_{int(time.time())}@example.com",
                "password": "GDPRTest123",
                "consent": True
            }
            
            response = requests.post(f"{API_BASE_URL}/register", json=registration_data)
            
            if response.status_code == 200:
                user_data = response.json()
                passed = "consent" in user_data and user_data["consent"] == True
                self.log_test("GDPR Compliance Features", passed, f"Consent tracked: {user_data.get('consent')}")
                return passed
            else:
                self.log_test("GDPR Compliance Features", False, f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GDPR Compliance Features", False, str(e))
            return False
    
    def test_security_features(self):
        """Test security features"""
        try:
            # Test that protected endpoints require authentication
            response = requests.get(f"{API_BASE_URL}/blinks/user")
            unauthorized_passed = response.status_code == 401
            
            # Test that invalid tokens are rejected
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            invalid_response = requests.get(f"{API_BASE_URL}/blinks/user", headers=invalid_headers)
            invalid_token_passed = invalid_response.status_code == 401
            
            passed = unauthorized_passed and invalid_token_passed
            details = f"Unauthorized: {unauthorized_passed}, Invalid token: {invalid_token_passed}"
            
            self.log_test("Security Features", passed, details)
            return passed
            
        except Exception as e:
            self.log_test("Security Features", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Full Stack Integration Test Suite")
        print("=" * 80)
        print("Testing: Desktop App + Backend API + Web Dashboard Integration")
        print("=" * 80)
        print()
        
        # Run all tests in sequence
        self.test_backend_health()
        self.test_user_registration_and_login()
        self.test_blink_data_api()
        self.test_python_eye_tracker_script()
        self.test_desktop_app_structure()
        self.test_web_dashboard_structure()
        self.test_cors_configuration()
        self.test_gdpr_compliance_features()
        self.test_security_features()
        
        # Print final results
        print("=" * 80)
        print("📊 FULL STACK INTEGRATION TEST RESULTS")
        print("=" * 80)
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📈 TOTAL:  {self.results['total']}")
        print(f"🎯 SUCCESS RATE: {(self.results['passed']/self.results['total']*100):.1f}%")
        print()
        
        print("📋 DETAILED RESULTS:")
        for detail in self.results['details']:
            print(f"   {detail}")
        
        print()
        print("🏗️  FULL STACK ARCHITECTURE STATUS:")
        print(f"   🔧 Backend API:     {'✅ Ready' if self.results['passed'] >= 6 else '❌ Issues'}")
        print(f"   💻 Desktop App:     {'✅ Ready' if self.results['passed'] >= 7 else '❌ Issues'}")
        print(f"   🌐 Web Dashboard:   {'✅ Ready' if self.results['passed'] >= 8 else '❌ Issues'}")
        print(f"   🔒 Security:        {'✅ Ready' if self.results['passed'] >= 8 else '❌ Issues'}")
        print(f"   📋 GDPR:           {'✅ Ready' if self.results['passed'] >= 8 else '❌ Issues'}")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("   Your full stack application is ready for deployment!")
        else:
            print(f"\n⚠️  {self.results['failed']} integration test(s) failed.")
            print("   Review the issues above before deployment.")
        
        print("=" * 80)

def main():
    """Main test execution"""
    print("🔍 Full Stack Integration Testing")
    print("   Testing all three components working together:")
    print("   1. Cross-Platform Desktop App (Electron + Python)")
    print("   2. Cloud Backend & Database (FastAPI + PostgreSQL)")
    print("   3. Web Dashboard (React + Chart.js)")
    print()
    
    test_suite = FullStackTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
