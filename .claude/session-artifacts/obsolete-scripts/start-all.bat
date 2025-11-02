@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM   Elephant AI - One-Command Startup Script
REM ============================================================
REM   This script starts all 3 servers with ONE command:
REM   - Python AI Router (port 8888)
REM   - Node.js Backend (port 3002)
REM   - React Frontend (port 3000)
REM
REM   To STOP: Just press Ctrl+C in this window
REM ============================================================

echo.
echo ============================================================
echo   Starting Elephant AI - Complete System
echo ============================================================
echo.

REM Change to project root
cd /d %~dp0

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Clean up old log files
if exist logs\ai-router.log del logs\ai-router.log
if exist logs\backend.log del logs\backend.log

echo [1/4] Starting Python AI Router server (port 8888)...
echo       This will take ~13 seconds to load the ML model...

REM Start Python AI Router in background
start /B cmd /c "python -m utils.ai_router.http_server > logs\ai-router.log 2>&1"

REM Wait for Python server to initialize (15 seconds for model loading)
echo [2/4] Waiting for AI Router to initialize...
echo.
powershell -Command "Write-Host '       ' -NoNewline; for($i=15; $i -gt 0; $i--) { Write-Host \"$i...\" -NoNewline; Start-Sleep -Seconds 1 }"
echo.
echo.

REM Check if Python server is running
powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://localhost:8888/health' -TimeoutSec 2 -ErrorAction Stop; 'ok' } catch { 'failed' }; if($response -eq 'ok') { Write-Host '       [OK] AI Router is ready' -ForegroundColor Green } else { Write-Host '       [WARN] AI Router may not be ready (check logs/ai-router.log)' -ForegroundColor Yellow }"

echo.
echo [3/4] Starting Node.js backend (port 3002)...

REM Start backend in background
cd backend-api
start /B cmd /c "npm start > ..\logs\backend.log 2>&1"
cd ..

REM Wait for backend to start
powershell -Command "Start-Sleep -Seconds 5"

REM Check if backend is running
powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://localhost:3002/health' -TimeoutSec 2 -ErrorAction Stop; 'ok' } catch { 'failed' }; if($response -eq 'ok') { Write-Host '       [OK] Backend API is ready' -ForegroundColor Green } else { Write-Host '       [WARN] Backend may not be ready (check logs/backend.log)' -ForegroundColor Yellow }"

echo.
echo [4/4] Starting React frontend (port 3000)...
echo.
echo ============================================================
echo   All backend systems initialized!
echo ============================================================
echo.
echo   AI Router:  http://localhost:8888/health
echo   Backend:    http://localhost:3002/health
echo   Frontend:   http://localhost:3000 (opening now...)
echo.
echo   Logs:       logs\ai-router.log
echo               logs\backend.log
echo.
echo   To STOP everything: Press Ctrl+C in this window
echo.
echo ============================================================
echo.

REM Start frontend in foreground (so you see the output and can stop it easily)
cd frontend
npm start

REM When frontend closes, cleanup background processes
echo.
echo.
echo ============================================================
echo   Shutting down all services...
echo ============================================================

REM Kill background processes on port 8888 (Python) and 3002 (Node)
powershell -Command "Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
powershell -Command "Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo.
echo   All services stopped.
echo.
pause
