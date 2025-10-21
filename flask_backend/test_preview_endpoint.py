"""
Test script to verify the preview endpoint is working
"""
import requests
import json

def test_preview_endpoint():
    """Test the preview endpoint"""
    # You'll need to replace this with a real case ID and token
    case_id = 1  # Replace with actual case ID
    token = "your_jwt_token_here"  # Replace with actual JWT token
    
    url = f"http://127.0.0.1:5000/api/reports/{case_id}/preview"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print("✅ Preview endpoint is working!")
                print(f"Case: {data['data']['case']['title']}")
                print(f"Statistics: {data['data']['statistics']}")
            else:
                print("⚠️ Preview endpoint returned success but no data")
        else:
            print("❌ Preview endpoint has issues")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start the Flask server first.")
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")

if __name__ == "__main__":
    print("Testing preview endpoint...")
    print("Note: You need to update the case_id and token variables with real values")
    test_preview_endpoint()
