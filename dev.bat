@echo off
REM Development startup script for Elephant Recruitment System
REM Starts both backend API and frontend dev server

echo.
echo ====================================
echo  ELEPHANT RECRUITMENT - Dev Mode
echo ====================================
echo.

set BACKEND_PORT=3002

echo Starting backend on port %BACKEND_PORT%...
start "Backend API" cmd /k "cd backend-api && npm start"

timeout /t 3 /nobreak

echo Starting frontend on port 5173...
start "Frontend Dev Server" cmd /k "cd frontend && npm run dev"

echo.
echo ✓ Both services starting:
echo   - Backend:  http://localhost:%BACKEND_PORT%/api/chat
echo   - Frontend: http://localhost:5173
echo.
