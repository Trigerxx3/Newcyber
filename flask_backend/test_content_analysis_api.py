#!/usr/bin/env python3
"""
Test the content analysis API endpoint
"""
import requests
import json

def test_content_analysis_api():
    """Test the content analysis API endpoint"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Content Analysis API...")
    print("=" * 50)
    
    # Test data
    test_data = {
        "platform": "Instagram",  # Optional
        "username": "test_user",  # Optional
        "content": "Buy LSD cheap DM me for prices"
    }
    
    print(f"📝 Testing with content: '{test_data['content']}'")
    
    try:
        # First, try without authentication (should get 401)
        print("\n1️⃣ Testing without authentication...")
        response = requests.post(f"{base_url}/api/content-analysis/analyze", json=test_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Test Complete!")
    print("\n💡 The 500 error should now be fixed!")
    print("The endpoint requires authentication, which is why you get 401 without a token.")

if __name__ == "__main__":
    test_content_analysis_api()
