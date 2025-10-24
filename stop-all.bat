@echo off
echo.
echo ============================================================
echo   Stopping All Elephant AI Services
echo ============================================================
echo.

REM Kill Python AI Router (port 8888)
echo [1/3] Stopping Python AI Router (port 8888)...
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue; if($conn) { Stop-Process -Id $conn.OwningProcess -Force; Write-Host '       [OK] Stopped' -ForegroundColor Green } else { Write-Host '       [INFO] Not running' -ForegroundColor Gray }"

REM Kill Node.js Backend (port 3002)
echo [2/3] Stopping Node.js Backend (port 3002)...
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue; if($conn) { Stop-Process -Id $conn.OwningProcess -Force; Write-Host '       [OK] Stopped' -ForegroundColor Green } else { Write-Host '       [INFO] Not running' -ForegroundColor Gray }"

REM Kill React Frontend (port 3000)
echo [3/3] Stopping React Frontend (port 3000)...
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue; if($conn) { Stop-Process -Id $conn.OwningProcess -Force; Write-Host '       [OK] Stopped' -ForegroundColor Green } else { Write-Host '       [INFO] Not running' -ForegroundColor Gray }"

echo.
echo ============================================================
echo   All services stopped
echo ============================================================
echo.
pause
