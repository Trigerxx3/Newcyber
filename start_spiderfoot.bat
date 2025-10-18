@echo off
echo ========================================
echo Starting Spiderfoot Web UI
echo ========================================
echo.
echo Spiderfoot will be available at:
echo http://127.0.0.1:5001
echo.
echo Keep this window open while using the application
echo Press Ctrl+C to stop Spiderfoot
echo.
echo ========================================
cd osint_tools\spiderfoot
python sf.py -l 127.0.0.1:5001
pause
