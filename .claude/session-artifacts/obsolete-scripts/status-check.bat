@echo off
echo.
echo ============================================================
echo   Elephant AI - System Status Check
echo ============================================================
echo.

REM Check Python AI Router (port 8888)
echo [1/3] Python AI Router (port 8888)
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue; if($conn) { Write-Host '       Status: RUNNING (PID: ' $conn.OwningProcess ')' -ForegroundColor Green; try { $health = Invoke-RestMethod -Uri 'http://localhost:8888/health' -TimeoutSec 2; Write-Host '       Health: ' $health.status -ForegroundColor Green } catch { Write-Host '       Health: ERROR' -ForegroundColor Red } } else { Write-Host '       Status: NOT RUNNING' -ForegroundColor Red }"

echo.

REM Check Node.js Backend (port 3002)
echo [2/3] Node.js Backend (port 3002)
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue; if($conn) { Write-Host '       Status: RUNNING (PID: ' $conn.OwningProcess ')' -ForegroundColor Green; try { $health = Invoke-RestMethod -Uri 'http://localhost:3002/health' -TimeoutSec 2; Write-Host '       Health: ' $health.status -ForegroundColor Green } catch { Write-Host '       Health: ERROR' -ForegroundColor Red } } else { Write-Host '       Status: NOT RUNNING' -ForegroundColor Red }"

echo.

REM Check React Frontend (port 3000)
echo [3/3] React Frontend (port 3000)
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue; if($conn) { Write-Host '       Status: RUNNING (PID: ' $conn.OwningProcess ')' -ForegroundColor Green } else { Write-Host '       Status: NOT RUNNING' -ForegroundColor Red }"

echo.
echo ============================================================
echo   URLs:
echo ============================================================
echo   AI Router:  http://localhost:8888/health
echo   Backend:    http://localhost:3002/health
echo   Frontend:   http://localhost:3000
echo.
echo ============================================================
echo.
pause
