@echo off
echo Starting Spiderfoot OSINT Server...
echo.
echo Spiderfoot will run on: http://127.0.0.1:5001
echo Press Ctrl+C to stop the server
echo.
cd osint_tools\spiderfoot
python sf.py -l 127.0.0.1:5001
