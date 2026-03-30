# OSINT Tools Setup Complete Guide

## ✅ **Setup Status: COMPLETE**

All OSINT tools have been successfully configured and are ready for use in the Cyber Intelligence Platform.

## 🔧 **Tools Installed & Configured**

### 1. **Spiderfoot** ✅
- **Status**: Running on `http://127.0.0.1:5001`
- **Purpose**: Comprehensive OSINT gathering and analysis
- **Features**: Web interface, API access, multiple scan types
- **Installation**: Complete with all dependencies

### 2. **Sherlock** ✅
- **Status**: Installed and functional
- **Purpose**: Username investigation across 300+ social networks
- **Features**: Fast scanning, multiple output formats, timeout handling
- **Installation**: Complete with all dependencies

## 🚀 **How to Use**

### **Starting the Tools**

1. **Start Spiderfoot Server**:
   ```bash
   cd "D:\new cyber"
   .\start_spiderfoot.bat
   ```
   - Server will run on: `http://127.0.0.1:5001`
   - Keep this terminal window open while using the platform

2. **Sherlock is Ready**:
   - No additional startup required
   - Automatically integrated with the backend

### **Using the Investigation Interface**

1. **Navigate to Investigation Page**:
   - Go to the main dashboard
   - Click on "Investigation" or "OSINT Tools"

2. **Run an Investigation**:
   - Enter a username in the "Username" field
   - Click "Start Investigation"
   - Wait for results (typically 30-60 seconds)

3. **View Results**:
   - Results will show findings from all tools
   - Each tool's status and findings are displayed separately
   - Links to discovered profiles are provided

## 📊 **Expected Results**

### **Tool Status Indicators**:
- 🟢 **Success**: Tool completed successfully with findings
- 🟡 **Timeout**: Tool is still running (normal for Sherlock)
- 🔴 **Unavailable**: Tool needs to be started (Spiderfoot)

### **Sample Investigation Results**:
```
Found X potential profiles for username 'username'

Spiderfoot:
- Status: success
- Findings: [Detailed analysis results]
- Number of Findings: X

Sherlock:
- Status: success  
- Findings: [List of discovered profiles]
- Number of Findings: X

URL Checker:
- Status: success
- Profiles Found: X
- Method: fallback_url_check
```

## 🔧 **Troubleshooting**

### **If Spiderfoot Shows "Unavailable"**:
1. Check if `start_spiderfoot.bat` is running
2. Verify server is accessible at `http://127.0.0.1:5001`
3. Restart the batch file if needed

### **If Sherlock Shows "Timeout"**:
- This is normal behavior
- Sherlock scans 300+ sites and can take 30-60 seconds
- Results will appear when scanning completes

### **If No Results Found**:
- Username might not exist on any platforms
- Try different usernames for testing
- Check network connectivity

## 🛠 **Technical Details**

### **File Locations**:
- **Spiderfoot**: `osint_tools/spiderfoot/`
- **Sherlock**: `osint_tools/sherlock/`
- **Backend Integration**: `flask_backend/services/osint_tools.py`

### **Ports Used**:
- **Spiderfoot Web UI**: `127.0.0.1:5001`
- **Backend API**: `127.0.0.1:5000`

### **Dependencies Installed**:
- All Python packages for both tools
- Network libraries for web scraping
- Authentication and security libraries

## 🎯 **Next Steps**

1. **Test the Interface**: Run a sample investigation
2. **Explore Results**: Review the detailed findings
3. **Link to Cases**: Use findings in case management
4. **Generate Reports**: Include OSINT data in reports

## 📝 **Notes**

- **Spiderfoot** provides comprehensive analysis but requires the web server to be running
- **Sherlock** is fast and doesn't require additional setup
- Both tools work together to provide comprehensive username investigation
- Results are automatically integrated into the case management system

## ✅ **Verification**

To verify everything is working:

1. **Check Spiderfoot**: Visit `http://127.0.0.1:5001` in your browser
2. **Test Investigation**: Run a username investigation in the platform
3. **Review Results**: Ensure all tools show results or appropriate status

---

**Setup Complete!** 🎉
Your OSINT tools are now fully integrated and ready for use in the Cyber Intelligence Platform.



