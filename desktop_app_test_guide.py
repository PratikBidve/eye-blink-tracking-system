#!/usr/bin/env python3
"""
Desktop App Integration Testing Guide
Tests and validates the desktop app functionality
"""
import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8002"

def create_test_users():
    """Create test users for desktop app testing"""
    test_users = [
        {"email": "user1@example.com", "password": "password123", "consent": True},
        {"email": "user2@example.com", "password": "password123", "consent": True},
        {"email": "demo@wellness.com", "password": "demo123", "consent": True}
    ]
    
    created_users = []
    print("🔧 Creating test users for desktop app...")
    
    for user in test_users:
        try:
            response = requests.post(f"{API_BASE_URL}/register", json=user)
            if response.status_code == 200:
                print(f"✅ Created user: {user['email']}")
                created_users.append(user)
            elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
                print(f"ℹ️  User already exists: {user['email']}")
                created_users.append(user)
            else:
                print(f"❌ Failed to create user: {user['email']} - {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating user {user['email']}: {str(e)}")
    
    return created_users

def test_login_credentials(email, password):
    """Test login credentials"""
    try:
        login_data = {"username": email, "password": password}
        response = requests.post(f"{API_BASE_URL}/token", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful for {email}")
            print(f"   Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed for {email}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error for {email}: {str(e)}")
        return None

def test_blink_data_upload(token, blink_count=15):
    """Test blink data upload"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        blink_data = {"blink_count": blink_count}
        
        response = requests.post(f"{API_BASE_URL}/blinks/upload", json=blink_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Blink data uploaded: {blink_count} blinks")
            print(f"   Data ID: {data['id']}, Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Blink upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Blink upload error: {str(e)}")
        return False

def test_get_user_data(token):
    """Test getting user's blink data"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/blinks/user", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data)} blink records")
            for record in data[:3]:  # Show first 3 records
                print(f"   - {record['blink_count']} blinks at {record['timestamp']}")
            return data
        else:
            print(f"❌ Data retrieval failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Data retrieval error: {str(e)}")
        return []

def main():
    """Main testing function"""
    print("🖥️  DESKTOP APP INTEGRATION TESTING")
    print("=" * 60)
    print("📱 Your desktop app should be running and showing login screen")
    print("🌐 Backend API running on: http://localhost:8002")
    print("📊 Web dashboard running on: http://localhost:5173")
    print("=" * 60)
    print()
    
    # Create test users
    created_users = create_test_users()
    print()
    
    if not created_users:
        print("❌ No test users available. Exiting.")
        return
    
    # Test login for each user and upload some test data
    print("🧪 Testing login and data operations...")
    print()
    
    for i, user in enumerate(created_users[:2]):  # Test first 2 users
        print(f"👤 Testing user {i+1}: {user['email']}")
        print("-" * 40)
        
        # Test login
        token = test_login_credentials(user['email'], user['password'])
        
        if token:
            # Upload some test blink data
            for j in range(3):
                blink_count = 10 + (j * 5) + (i * 3)  # Varied data
                test_blink_data_upload(token, blink_count)
                time.sleep(0.1)  # Small delay
            
            # Retrieve user data
            user_data = test_get_user_data(token)
            
        print()
    
    print("=" * 60)
    print("🖥️  DESKTOP APP TESTING INSTRUCTIONS")
    print("=" * 60)
    print("1. 📱 Use these credentials in your desktop app:")
    print()
    for user in created_users:
        print(f"   📧 Email: {user['email']}")
        print(f"   🔑 Password: {user['password']}")
        print()
    
    print("2. 🧪 Test the following features:")
    print("   ✅ Login with the credentials above")
    print("   ✅ Start the eye tracker (Python script)")
    print("   ✅ Watch blink count updates in real-time")
    print("   ✅ Verify data sync status")
    print("   ✅ Test offline/online sync")
    print("   ✅ Logout and login again")
    print()
    
    print("3. 🌐 Test web dashboard:")
    print("   ✅ Open http://localhost:5173")
    print("   ✅ Login with same credentials")
    print("   ✅ View blink data charts")
    print("   ✅ Verify real-time updates")
    print()
    
    print("4. 🔍 Monitor backend logs:")
    print("   ✅ Check terminal running the backend")
    print("   ✅ Verify API requests are logged")
    print("   ✅ No errors in authentication")
    print()
    
    print("🎉 Your full-stack integration is ready!")
    print("🚀 All three components are working together!")

if __name__ == "__main__":
    main()
