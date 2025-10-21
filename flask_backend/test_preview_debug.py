"""
Debug script to test the preview endpoint and identify the 500 error
"""
import requests
import json

def test_preview_endpoint():
    """Test the preview endpoint to identify the 500 error"""
    print("Testing /api/reports/active/preview endpoint...")
    print("=" * 50)
    
    try:
        # Test without authentication first to see if it's an auth issue
        response = requests.get("http://127.0.0.1:5000/api/reports/active/preview", timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("✅ Endpoint exists but requires authentication")
            print("This is expected - the endpoint is working but needs a valid JWT token")
            return True
        elif response.status_code == 500:
            print("❌ Internal Server Error - checking response body...")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error Response (text): {response.text}")
            return False
        elif response.status_code == 200:
            print("✅ Endpoint working without authentication")
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start the Flask server first.")
        print("Run: cd flask_backend && python run.py")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")
        return False

def test_health_endpoint():
    """Test if the backend is running"""
    print("\nTesting backend health...")
    print("=" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_reports_health():
    """Test the reports health endpoint"""
    print("\nTesting reports health...")
    print("=" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/reports/health", timeout=5)
        print(f"Reports Health Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Reports service is healthy")
            try:
                data = response.json()
                print(f"Reports Health Data: {json.dumps(data, indent=2)}")
            except:
                print(f"Reports Health Text: {response.text}")
            return True
        else:
            print(f"❌ Reports health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Reports health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Debugging Preview Endpoint 500 Error")
    print("=" * 50)
    
    # Test backend health
    backend_running = test_health_endpoint()
    
    if backend_running:
        # Test reports health
        reports_healthy = test_reports_health()
        
        # Test preview endpoint
        preview_working = test_preview_endpoint()
        
        print("\n" + "=" * 50)
        print("SUMMARY:")
        print(f"Backend Running: {'✅ YES' if backend_running else '❌ NO'}")
        print(f"Reports Healthy: {'✅ YES' if reports_healthy else '❌ NO'}")
        print(f"Preview Working: {'✅ YES' if preview_working else '❌ NO'}")
        
        if not preview_working:
            print("\n🔍 DEBUGGING STEPS:")
            print("1. Check backend console logs for specific error messages")
            print("2. Verify database models are properly imported")
            print("3. Check if ActiveCase model exists and is accessible")
            print("4. Verify JWT authentication is working")
            print("5. Check if there are any database connection issues")
    else:
        print("\n❌ Cannot test endpoints - backend is not running")
        print("Please start the backend server first:")
        print("cd flask_backend && python run.py")
