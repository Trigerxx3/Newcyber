"""
Test script to verify the Narcotics Intelligence Platform report format
"""
import requests
import json

def test_narcotics_report_generation():
    """Test the Narcotics Intelligence Platform report generation"""
    case_id = 1  # Replace with actual case ID
    
    print("Testing Narcotics Intelligence Platform Report Generation...")
    print("=" * 60)
    
    # Test detailed report endpoint
    try:
        url = f"http://127.0.0.1:5000/api/reports/{case_id}/generate-detailed"
        print(f"Testing URL: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print("✅ Narcotics Intelligence Platform report generated successfully!")
                print(f"PDF size: {len(response.content)} bytes")
                
                # Save the PDF for inspection
                with open('test_narcotics_report.pdf', 'wb') as f:
                    f.write(response.content)
                print("✅ PDF saved as 'test_narcotics_report.pdf' for inspection")
                
                return True
            else:
                print("❌ Response is not a PDF")
                print(f"Response content: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Report generation failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start the Flask server first.")
        print("Run: cd flask_backend && python run.py")
        return False
    except Exception as e:
        print(f"❌ Error testing report generation: {str(e)}")
        return False

def test_basic_report_generation():
    """Test the basic report generation endpoint"""
    case_id = 1  # Replace with actual case ID
    
    print("\nTesting Basic Report Generation...")
    print("=" * 40)
    
    try:
        url = f"http://127.0.0.1:5000/api/reports/{case_id}/generate"
        print(f"Testing URL: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print("✅ Basic report generated successfully!")
                print(f"PDF size: {len(response.content)} bytes")
                return True
            else:
                print("❌ Response is not a PDF")
                return False
        else:
            print(f"❌ Basic report generation failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing basic report: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Narcotics Intelligence Platform Report Format")
    print("=" * 60)
    
    # Test detailed report (should use new format)
    detailed_success = test_narcotics_report_generation()
    
    # Test basic report (should also use new format)
    basic_success = test_basic_report_generation()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Detailed Report: {'✅ SUCCESS' if detailed_success else '❌ FAILED'}")
    print(f"Basic Report: {'✅ SUCCESS' if basic_success else '❌ FAILED'}")
    
    if detailed_success or basic_success:
        print("\n📄 Check the generated PDF to verify it uses the Narcotics Intelligence Platform format:")
        print("- Header: 'Narcotics Intelligence Platform' + 'Investigation Report'")
        print("- Case Overview: Blue header box with case information")
        print("- Description: Red header with case description")
        print("- Investigation Summary: Red header with summary table")
        print("- Flagged Content Analysis: Blue header box")
        print("- OSINT Results: Blue header box")
        print("- Next Steps: Red header with numbered list")
        print("- Footer: Copyright and security notice")
    else:
        print("\n❌ No reports were generated successfully.")
        print("Please check that the backend server is running and the case ID exists.")
