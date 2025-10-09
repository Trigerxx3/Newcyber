#!/usr/bin/env python3
"""
Test authentication flow and content endpoint
"""
import requests
import json

def test_auth_flow():
    """Test the complete authentication flow"""
    base_url = "http://localhost:5000"
    
    print("🔐 Testing Authentication Flow...")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1️⃣ Attempting login...")
    login_data = {
        "email": "admin@cyber.com",
        "password": "admin123456"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get('status') == 'success':
                token = login_result.get('data', {}).get('access_token')
                print(f"✅ Login successful! Token: {token[:20]}...")
                
                # Step 2: Test content endpoint with token
                print("\n2️⃣ Testing content endpoint with token...")
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                content_response = requests.get(
                    f"{base_url}/api/content?per_page=10",
                    headers=headers
                )
                
                print(f"Content Status: {content_response.status_code}")
                
                if content_response.status_code == 200:
                    content_result = content_response.json()
                    print(f"✅ Content endpoint working!")
                    print(f"   Total items: {content_result.get('pagination', {}).get('total', 0)}")
                    print(f"   Items returned: {len(content_result.get('data', []))}")
                else:
                    print(f"❌ Content endpoint failed: {content_response.text}")
                    
            else:
                print(f"❌ Login failed: {login_result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Login request failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Authentication Flow Test Complete!")

if __name__ == "__main__":
    test_auth_flow()
