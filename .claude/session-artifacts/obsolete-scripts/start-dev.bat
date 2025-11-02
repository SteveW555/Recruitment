@echo off
echo.
echo ====================================
echo   Starting Elephant Development
echo ====================================
echo.

REM Kill any existing node processes to avoid port conflicts
echo Cleaning up existing processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start backend on port 3002
echo.
echo [1/2] Starting Backend API on port 3002...
cd backend-api
start "Backend API (Port 3002)" cmd /k "set BACKEND_PORT=3002 && npm start"
cd ..

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend on port 3000
echo.
echo [2/2] Starting Frontend Dashboard on port 3000...
cd frontend
start "Frontend Dashboard (Port 3000)" cmd /k "npm start"
cd ..

echo.
echo ====================================
echo   Development servers starting...
echo ====================================
echo.
echo   Backend:  http://localhost:3002
echo   Frontend: http://localhost:3000
echo.
echo   Press Ctrl+C in each window to stop
echo ====================================
