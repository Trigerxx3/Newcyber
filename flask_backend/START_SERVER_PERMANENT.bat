@echo off
title Cyber Intelligence Platform - Permanent Server Manager
color 0A

echo.
echo ===============================================
echo   Cyber Intelligence Platform Backend
echo   PERMANENT SERVER MANAGER
echo ===============================================
echo.
echo 🔄 Starting permanent server manager...
echo 📋 This will keep the server running automatically
echo 🛑 Press Ctrl+C to stop the manager
echo.

cd /d "%~dp0"

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul

REM Install required packages if needed
python -c "import requests" 2>nul || pip install requests

REM Start the permanent server manager
python server_manager.py

echo.
echo ❌ Server manager stopped. Press any key to close...
pause >nul