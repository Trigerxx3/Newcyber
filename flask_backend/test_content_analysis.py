"""
Test script to verify content analysis endpoint is working
"""
import requests
import json

def test_content_analysis():
    """Test the content analysis endpoint"""
    url = "http://127.0.0.1:5000/api/content-analysis/analyze"
    
    # Test data
    data = {
        "platform": "Instagram",
        "username": "test_user",
        "content": "This is a test content for analysis",
        "save_to_database": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"  # You'll need a real token
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Content analysis endpoint is working!")
        else:
            print("❌ Content analysis endpoint has issues")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start the Flask server first.")
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")

if __name__ == "__main__":
    test_content_analysis()
