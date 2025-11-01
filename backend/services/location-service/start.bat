@echo off
REM Start Location Service
REM ProActive People - UK Postcode & Geography API

echo ========================================
echo Location Service - Starting
echo ========================================

REM Navigate to project root (3 levels up)
cd /d "%~dp0..\..\..\"

REM Check if virtual environment exists in project root
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo Warning: Virtual environment not found at project root
    echo Consider creating one: python -m venv venv
)

REM Check if dependencies are installed
python -c "import fastapi" 2>NUL
if errorlevel 1 (
    echo Installing dependencies from project root...
    pip install -r requirements-location-service.txt
)

REM Start the service (from project root)
echo Starting Location Service on port 8001...
cd backend\services\location-service
python -m src.main

pause
