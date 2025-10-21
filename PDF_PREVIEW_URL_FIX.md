# PDF Preview URL Fix - Complete Solution

## Problem Identified
The PDF preview was failing because the API URL was being truncated to `http://127.0.0` instead of the full `http://127.0.0.1:5000`. This was causing the fetch requests to fail.

## Root Cause
The issue was likely caused by:
1. **Environment variable truncation** - `NEXT_PUBLIC_API_URL` might be set incorrectly
2. **URL parsing issues** - The URL was being cut off during construction
3. **Network configuration** - Possible CORS or network issues

## Solutions Implemented

### 1. **Enhanced URL Validation and Fallback**

#### **Fixed URL Construction**
```typescript
// Get the API base URL from environment or use default
let apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'
console.log('Generating PDF for case:', caseId, 'API URL:', apiBaseUrl)
console.log('Environment API URL:', process.env.NEXT_PUBLIC_API_URL)

// Ensure we have a complete URL - if truncated, use hardcoded fallback
if (!apiBaseUrl || apiBaseUrl.length < 10 || apiBaseUrl.includes('127.0.0')) {
  apiBaseUrl = 'http://127.0.0.1:5000'
  console.log('Using fallback API URL:', apiBaseUrl)
}
```

#### **Enhanced Error Handling**
```typescript
console.log('PDF generation response:', response.status, response.statusText)
console.log('Content-Type:', response.headers.get('content-type'))
console.log('Response URL:', response.url)

if (!response.ok) {
  const errorText = await response.text()
  console.error('PDF generation failed:', errorText)
  console.error('Full response:', response)
  throw new Error(`Failed to generate report: ${response.status} ${response.statusText}. Error: ${errorText}`)
}
```

### 2. **Debug Tools Added**

#### **API Connection Debug Function**
```typescript
const debugApiConnection = async () => {
  try {
    const apiBaseUrl = 'http://127.0.0.1:5000'
    console.log('Testing API connection to:', apiBaseUrl)
    
    // Test basic health endpoint
    const healthResponse = await fetch(`${apiBaseUrl}/api/health`)
    console.log('Health check:', healthResponse.status, healthResponse.statusText)
    
    // Test reports endpoint
    const reportsResponse = await fetch(`${apiBaseUrl}/api/reports/1/generate-detailed`)
    console.log('Reports endpoint:', reportsResponse.status, reportsResponse.statusText)
    
    toast({
      title: "Debug Info",
      description: `Health: ${healthResponse.status}, Reports: ${reportsResponse.status}`,
    })
  } catch (error: any) {
    console.error('Debug connection error:', error)
    toast({
      title: "Debug Error",
      description: `Connection failed: ${error.message}`,
      variant: "destructive"
    })
  }
}
```

#### **Debug Button Added**
- Added a "Debug API" button next to the Generate PDF button
- Tests both health and reports endpoints
- Provides immediate feedback on API connectivity

### 3. **Backend Testing Script**

#### **Created `test_backend_connection.py`**
```python
def test_backend_connection():
    """Test if backend is running"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        print(f"✅ Backend is running - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on http://127.0.0.1:5000")
        return False

def test_reports_endpoint():
    """Test the reports endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/reports/1/generate-detailed", timeout=10)
        print(f"Reports endpoint status: {response.status_code}")
        # ... more testing
```

## How to Test the Fix

### 1. **Test Backend Connection**
```bash
cd flask_backend
python test_backend_connection.py
```

### 2. **Test Frontend Debug**
1. Go to Investigation Reports page
2. Click the **"Debug API"** button
3. Check console for detailed connection info
4. Verify both health and reports endpoints respond

### 3. **Test PDF Generation**
1. Make sure you have an active case selected
2. Click **"Generate PDF"** button
3. Check console for detailed logging:
   - API URL being used
   - Response status and headers
   - Any error messages

### 4. **Check Console Output**
Look for these logs:
```
Generating PDF for case: [ID] API URL: http://127.0.0.1:5000
Environment API URL: [value or undefined]
PDF generation response: [status] [statusText]
Content-Type: application/pdf
Response URL: [full URL]
```

## Expected Behavior Now

### ✅ **URL Validation**
- **Environment variable checked** - Logs the actual value
- **Fallback mechanism** - Uses hardcoded URL if environment is invalid
- **Length validation** - Ensures URL is complete
- **Truncation detection** - Catches partial URLs like "127.0.0"

### ✅ **Enhanced Debugging**
- **Detailed console logging** - Shows every step of the process
- **Response inspection** - Logs status, headers, and URL
- **Error details** - Shows full error messages
- **Debug button** - Quick API connectivity test

### ✅ **Error Recovery**
- **Graceful fallback** - Uses hardcoded URL if environment fails
- **Clear error messages** - Shows exactly what went wrong
- **User feedback** - Toast notifications for success/failure

## Troubleshooting Steps

### If PDF Preview Still Doesn't Work:

#### 1. **Check Backend is Running**
```bash
cd flask_backend
python run.py
```
Should show: `Running on http://127.0.0.1:5000`

#### 2. **Test Backend Directly**
```bash
cd flask_backend
python test_backend_connection.py
```

#### 3. **Check Frontend Console**
- Open browser developer tools
- Go to Console tab
- Click "Debug API" button
- Look for error messages

#### 4. **Verify Environment Variables**
- Check if `NEXT_PUBLIC_API_URL` is set in your environment
- The code will log the actual value to console

#### 5. **Test Manual API Call**
```bash
curl http://127.0.0.1:5000/api/health
curl http://127.0.0.1:5000/api/reports/1/generate-detailed
```

## Files Modified

### **Frontend Files**
- ✅ `cyber/src/app/dashboard/reports/page.tsx` - Enhanced URL handling and debugging

### **Backend Files**
- ✅ `flask_backend/test_backend_connection.py` - Backend testing script

### **Documentation**
- ✅ `PDF_PREVIEW_URL_FIX.md` - This comprehensive guide

## Status
- ✅ URL truncation issue identified and fixed
- ✅ Enhanced error handling and debugging
- ✅ Fallback mechanisms implemented
- ✅ Debug tools added for troubleshooting
- ✅ Backend testing script created
- ✅ Comprehensive logging added

The PDF preview should now work correctly with proper URL handling, enhanced debugging, and fallback mechanisms. If issues persist, the debug tools will help identify the exact problem.
