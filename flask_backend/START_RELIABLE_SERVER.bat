@echo off
title Cyber Intelligence Platform - Reliable Server
color 0A

echo.
echo ===============================================
echo   Cyber Intelligence Platform Backend
echo   RELIABLE SERVER MANAGER
echo ===============================================
echo.
echo Starting reliable server manager...
echo This manager will automatically restart the server if it stops
echo Press Ctrl+C to stop the server manager
echo.

cd /d "%~dp0"

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul

REM Start the reliable server manager
python simple_server_manager.py

echo.
echo Server manager stopped. Press any key to close...
pause >nul