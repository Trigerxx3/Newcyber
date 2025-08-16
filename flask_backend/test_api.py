"""
Test script for API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_auth():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication...")
    
    # Test signup
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser",
        "role": "Analyst"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Signup: {response.status_code} - {response.json()}")
    
    # Test signin
    signin_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"Signin successful! Token: {token[:20]}...")
        return token
    else:
        print(f"Signin failed: {response.json()}")
        return None

def test_sources(token):
    """Test sources endpoints"""
    print("\n📡 Testing Sources...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get sources
    response = requests.get(f"{BASE_URL}/sources", headers=headers)
    print(f"Get sources: {response.status_code}")
    
    # Test create source (if admin)
    source_data = {
        "platform": "Telegram",
        "source_handle": "@test_channel",
        "source_name": "Test Channel",
        "source_type": "Channel"
    }
    
    response = requests.post(f"{BASE_URL}/sources", json=source_data, headers=headers)
    print(f"Create source: {response.status_code} - {response.json()}")

def test_api_docs():
    """Test API documentation"""
    print("\n📚 Testing API Documentation...")
    
    response = requests.get(f"{BASE_URL}")
    print(f"API docs: {response.status_code}")
    if response.status_code == 200:
        print("Available endpoints:")
        for category, endpoints in response.json()['endpoints'].items():
            print(f"  {category}: {len(endpoints)} endpoints")

if __name__ == "__main__":
    print("🚀 Testing API Endpoints...")
    print("=" * 50)
    
    # Test API docs first
    test_api_docs()
    
    # Test authentication
    token = test_auth()
    
    if token:
        # Test other endpoints
        test_sources(token)
    
    print("\n✅ API testing completed!") 
