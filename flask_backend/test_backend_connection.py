"""
Test script to verify backend connection and PDF generation
"""
import requests
import json

def test_backend_connection():
    """Test if backend is running"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        print(f"✅ Backend is running - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {str(e)}")
        return False

def test_reports_endpoint():
    """Test the reports endpoint"""
    try:
        # Test without authentication first
        response = requests.get("http://127.0.0.1:5000/api/reports/1/generate-detailed", timeout=10)
        print(f"Reports endpoint status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("✅ Reports endpoint is working (authentication required)")
            return True
        elif response.status_code == 200:
            print("✅ Reports endpoint is working (no auth required)")
            return True
        else:
            print(f"❌ Unexpected response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing reports endpoint: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    try:
        response = requests.options("http://127.0.0.1:5000/api/reports/1/generate-detailed")
        print(f"CORS preflight status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        return True
    except Exception as e:
        print(f"❌ Error testing CORS: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing backend connection...")
    print("=" * 50)
    
    print("\n1. Testing backend connection:")
    backend_running = test_backend_connection()
    
    if backend_running:
        print("\n2. Testing reports endpoint:")
        test_reports_endpoint()
        
        print("\n3. Testing CORS headers:")
        test_cors_headers()
    else:
        print("\n❌ Cannot test endpoints - backend is not running")
        print("Please start the Flask backend server first:")
        print("cd flask_backend && python run.py")
