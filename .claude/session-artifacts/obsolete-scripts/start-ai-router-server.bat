@echo off
echo Starting AI Router HTTP Server...
echo.
echo This will keep the Python model loaded in memory for fast responses.
echo Leave this window open while using the application.
echo.

cd /d %~dp0

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Set environment variables (replace with your actual keys)
set GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
set ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE

echo Starting Python HTTP server on port 8888...
python -m utils.ai_router.http_server

pause
