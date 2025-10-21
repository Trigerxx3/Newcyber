"""
Test script to verify PDF generation is working
"""
import requests
import json

def test_pdf_generation():
    """Test the PDF generation endpoint"""
    case_id = 1  # Replace with actual case ID
    token = "your_jwt_token_here"  # Replace with actual JWT token
    
    url = f"http://127.0.0.1:5000/api/reports/{case_id}/generate"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print("✅ PDF generation endpoint is working!")
                print(f"PDF size: {len(response.content)} bytes")
            else:
                print("❌ Response is not a PDF")
                print(f"Response content: {response.text[:200]}...")
        else:
            print("❌ PDF generation endpoint has issues")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start the Flask server first.")
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")

def test_detailed_pdf_generation():
    """Test the detailed PDF generation endpoint"""
    case_id = 1  # Replace with actual case ID
    
    url = f"http://127.0.0.1:5000/api/reports/{case_id}/generate-detailed"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print("✅ Detailed PDF generation endpoint is working!")
                print(f"PDF size: {len(response.content)} bytes")
            else:
                print("❌ Response is not a PDF")
                print(f"Response content: {response.text[:200]}...")
        else:
            print("❌ Detailed PDF generation endpoint has issues")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start the Flask server first.")
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")

if __name__ == "__main__":
    print("Testing PDF generation endpoints...")
    print("Note: You need to update the case_id and token variables with real values")
    print("\n1. Testing basic PDF generation:")
    test_pdf_generation()
    print("\n2. Testing detailed PDF generation:")
    test_detailed_pdf_generation()
