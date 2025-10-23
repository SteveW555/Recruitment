# Windows-Specific Troubleshooting Guide

## Quick Diagnostic Commands

### Port Checking

**Method 1: PowerShell Test-NetConnection (Fastest)**
```powershell
Test-NetConnection -ComputerName localhost -Port 3002 -InformationLevel Quiet
```
- Returns: `True` (port is listening) or `False` (port not listening)
- Fastest method for quick checks
- No output parsing needed

**Method 2: netstat (Detailed)**
```cmd
netstat -ano | findstr :3002
```
- Output: `TCP 0.0.0.0:3002 ... LISTENING 12345`
- Shows PID of process using the port
- Useful for identifying which process to kill

**Method 3: PowerShell Get-NetTCPConnection**
```powershell
Get-NetTCPConnection -LocalPort 3002 -State Listen -ErrorAction SilentlyContinue
```
- Most detailed information
- Shows process ID and owning process

### Process Management

**Find Node Processes**
```powershell
# List all node processes
Get-Process node -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime

# With command line details (requires admin)
Get-WmiObject Win32_Process -Filter "name='node.exe'" | Select-Object ProcessId, CommandLine
```

**Kill Processes**
```cmd
# Kill all node processes
taskkill /F /IM node.exe

# Kill specific process by PID
taskkill /F /PID 12345

# PowerShell alternative
Stop-Process -Name node -Force

# PowerShell by PID
Stop-Process -Id 12345 -Force
```

### Testing Endpoints

**Method 1: curl (if available)**
```cmd
curl http://localhost:3002/health
curl -X POST http://localhost:3002/api/chat -H "Content-Type: application/json" -d "{\"message\":\"test\"}"
```

**Method 2: PowerShell Invoke-WebRequest**
```powershell
# GET request
Invoke-WebRequest -Uri http://localhost:3002/health -UseBasicParsing | Select-Object StatusCode, Content

# POST request
$body = @{message="test"; sessionId="test-session"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:3002/api/chat -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Method 3: PowerShell Invoke-RestMethod (Better for JSON)**
```powershell
# GET request with JSON parsing
Invoke-RestMethod -Uri http://localhost:3002/health

# POST request
$body = @{
    message = "test"
    sessionId = "test-session"
    useHistory = $true
    agent = "general-chat"
}
Invoke-RestMethod -Uri http://localhost:3002/api/chat -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
```

## Common Windows-Specific Issues

### Issue 1: Path Separators in Scripts

**Problem**: Scripts using `/` instead of `\` for paths
```javascript
// ❌ May fail on Windows
dotenv.config({ path: '../.env' });

// ✅ Better - Node.js handles both
import path from 'path';
dotenv.config({ path: path.join(__dirname, '..', '.env') });
```

### Issue 2: Environment Variables Not Persisting

**Problem**: Setting environment variables in Command Prompt doesn't persist to new windows

**Solution 1: Use PowerShell with proper scope**
```powershell
# Set for current session only
$env:BACKEND_PORT = "3002"

# Set permanently for user
[System.Environment]::SetEnvironmentVariable('BACKEND_PORT', '3002', 'User')

# Set permanently for machine (requires admin)
[System.Environment]::SetEnvironmentVariable('BACKEND_PORT', '3002', 'Machine')
```

**Solution 2: Use .env files exclusively**
- Rely on dotenv package instead of system environment
- More portable across platforms

### Issue 3: Port 3000/3002 Blocked by Firewall

**Check Firewall Rules**
```powershell
# Check if port is blocked
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*3002*"}

# Check listening ports allowed through firewall
Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq 3002}
```

**Allow Port Through Firewall**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Node Dev Server 3002" -Direction Inbound -LocalPort 3002 -Protocol TCP -Action Allow
```

### Issue 4: Multiple Node Versions Interfering

**Check Node Version**
```cmd
node --version
npm --version
where node
```

**Problem**: Multiple Node installations (nvm, direct install, VS Code extension)

**Solution**: Use nvm-windows for version management
```cmd
nvm list
nvm use 18.0.0
```

### Issue 5: Line Ending Issues (CRLF vs LF)

**Problem**: Scripts fail with `\r: command not found`

**Solution**: Configure Git to handle line endings
```bash
# Configure for repository
git config core.autocrlf true

# Convert existing files
git add --renormalize .
```

## Automated Startup Scripts

### Enhanced start-dev.bat with Error Handling

```batch
@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Frontend-Backend Development Environment Startup
echo ============================================================
echo.

REM Check if Node is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Display Node version
echo Node.js version:
node --version
echo.

REM Kill existing node processes
echo [1/5] Cleaning up existing Node processes...
taskkill /F /IM node.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo       Successfully killed existing processes
) else (
    echo       No existing processes to clean up
)
echo.

REM Load environment from .env file
echo [2/5] Loading environment configuration...
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
        if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
    )
    echo       BACKEND_PORT=%BACKEND_PORT%
    echo       FRONTEND_PORT=%FRONTEND_PORT%
) else (
    echo       [WARNING] .env file not found, using defaults
    set BACKEND_PORT=3002
    set FRONTEND_PORT=3000
)
echo.

REM Check if ports are available
echo [3/5] Checking port availability...
powershell -Command "Test-NetConnection -ComputerName localhost -Port %BACKEND_PORT% -InformationLevel Quiet" | findstr "False" >nul
if %ERRORLEVEL% EQU 0 (
    echo       Port %BACKEND_PORT% is available for backend
) else (
    echo       [WARNING] Port %BACKEND_PORT% is already in use
    netstat -ano | findstr :%BACKEND_PORT%
)
echo.

REM Start backend
echo [4/5] Starting backend server on port %BACKEND_PORT%...
cd backend-api
if %ERRORLEVEL% NEQ 0 (
    echo       [ERROR] backend-api directory not found
    pause
    exit /b 1
)

start "Backend Server" cmd /k "set BACKEND_PORT=%BACKEND_PORT% && npm start"
cd ..
echo       Backend starting in new window...
echo.

REM Wait for backend to initialize
echo [5/5] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Test backend health
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:%BACKEND_PORT%/health' -TimeoutSec 2; Write-Host '       Backend health check: OK' } catch { Write-Host '       Backend health check: FAILED - '$_.Exception.Message }"
echo.

REM Start frontend
echo [6/5] Starting frontend server on port %FRONTEND_PORT%...
cd frontend
if %ERRORLEVEL% NEQ 0 (
    echo       [ERROR] frontend directory not found
    pause
    exit /b 1
)

start "Frontend Server" cmd /k "npm start"
cd ..
echo       Frontend starting in new window...
echo.

echo ============================================================
echo   Development Environment Ready!
echo ============================================================
echo.
echo   Backend:  http://localhost:%BACKEND_PORT%
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo   Health:   http://localhost:%BACKEND_PORT%/health
echo.
echo   Press any key to open browser...
pause >nul

start http://localhost:%FRONTEND_PORT%

exit /b 0
```

### PowerShell Alternative (start-dev.ps1)

```powershell
#!/usr/bin/env pwsh
# Frontend-Backend Development Startup Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Backend Development Environment Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js installation
try {
    $nodeVersion = node --version
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Clean up existing processes
Write-Host "[1/5] Cleaning up existing Node processes..." -ForegroundColor Yellow
try {
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "      Successfully killed existing processes" -ForegroundColor Green
} catch {
    Write-Host "      No existing processes to clean up" -ForegroundColor Gray
}
Write-Host ""

# Load environment configuration
Write-Host "[2/5] Loading environment configuration..." -ForegroundColor Yellow
$envFile = ".env"
$backendPort = 3002
$frontendPort = 3000

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^BACKEND_PORT=(.*)$') {
            $backendPort = $Matches[1].Trim()
        }
        if ($_ -match '^FRONTEND_PORT=(.*)$') {
            $frontendPort = $Matches[1].Trim()
        }
    }
    Write-Host "      BACKEND_PORT=$backendPort" -ForegroundColor Green
    Write-Host "      FRONTEND_PORT=$frontendPort" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] .env file not found, using defaults" -ForegroundColor Yellow
}
Write-Host ""

# Check port availability
Write-Host "[3/5] Checking port availability..." -ForegroundColor Yellow
$backendPortFree = -not (Test-NetConnection -ComputerName localhost -Port $backendPort -InformationLevel Quiet)
if ($backendPortFree) {
    Write-Host "      Port $backendPort is available for backend" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] Port $backendPort is already in use" -ForegroundColor Yellow
}
Write-Host ""

# Start backend
Write-Host "[4/5] Starting backend server on port $backendPort..." -ForegroundColor Yellow
if (Test-Path "backend-api") {
    $env:BACKEND_PORT = $backendPort
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend-api; `$env:BACKEND_PORT='$backendPort'; npm start"
    Write-Host "      Backend starting in new window..." -ForegroundColor Green
} else {
    Write-Host "      [ERROR] backend-api directory not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Wait for backend
Write-Host "[5/5] Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend health
try {
    $response = Invoke-RestMethod -Uri "http://localhost:$backendPort/health" -TimeoutSec 2
    Write-Host "      Backend health check: OK" -ForegroundColor Green
    Write-Host "      Service: $($response.service)" -ForegroundColor Gray
} catch {
    Write-Host "      Backend health check: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Start frontend
Write-Host "[6/5] Starting frontend server on port $frontendPort..." -ForegroundColor Yellow
if (Test-Path "frontend") {
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"
    Write-Host "      Frontend starting in new window..." -ForegroundColor Green
} else {
    Write-Host "      [ERROR] frontend directory not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Development Environment Ready!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend:  http://localhost:$backendPort" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:$frontendPort" -ForegroundColor Green
Write-Host "  Health:   http://localhost:$backendPort/health" -ForegroundColor Green
Write-Host ""
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:$frontendPort"
```

## Debugging Tips

### Enable Verbose Logging

**Frontend (Vite)**
```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3002',
        configure: (proxy) => {
          proxy.on('error', (err, req, res) => {
            console.error('[PROXY ERROR]', err);
          });
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log('[PROXY →]', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log('[PROXY ←]', proxyRes.statusCode, req.url);
          });
        }
      }
    }
  }
});
```

**Backend (Express)**
```javascript
// server.js - Add before routes
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  console.log('Headers:', JSON.stringify(req.headers, null, 2));
  if (req.body && Object.keys(req.body).length) {
    console.log('Body:', JSON.stringify(req.body, null, 2));
  }
  next();
});
```

### Monitor Network Traffic

```powershell
# PowerShell - Monitor HTTP traffic
while ($true) {
    Get-NetTCPConnection -LocalPort 3002 -State Established -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State
    Start-Sleep -Seconds 1
    Clear-Host
}
```

## Performance Optimization

### Windows Defender Exclusions

Add project directories to Windows Defender exclusions for faster npm installs and dev server startup:

```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "D:\Recruitment\node_modules"
Add-MpPreference -ExclusionPath "D:\Recruitment\frontend\node_modules"
Add-MpPreference -ExclusionPath "D:\Recruitment\backend-api\node_modules"
```

### Windows Terminal Integration

Add custom profiles to Windows Terminal (`settings.json`):

```json
{
  "profiles": {
    "list": [
      {
        "name": "Backend Dev",
        "commandline": "pwsh.exe -NoExit -Command \"cd D:\\Recruitment\\backend-api; $env:BACKEND_PORT='3002'; npm start\"",
        "startingDirectory": "D:\\Recruitment\\backend-api",
        "icon": "🔧"
      },
      {
        "name": "Frontend Dev",
        "commandline": "pwsh.exe -NoExit -Command \"cd D:\\Recruitment\\frontend; npm start\"",
        "startingDirectory": "D:\\Recruitment\\frontend",
        "icon": "🎨"
      }
    ]
  }
}
```

## Quick Troubleshooting Checklist for Windows

- [ ] Both servers running? `Get-Process node`
- [ ] Ports listening? `Test-NetConnection -Port 3002`
- [ ] Firewall blocking? Check Windows Defender Firewall rules
- [ ] Environment variables loaded? `$env:BACKEND_PORT`
- [ ] Node version correct? `node --version` (should be 18+)
- [ ] .env file present? `Test-Path .env`
- [ ] Backend health check passing? `curl http://localhost:3002/health`
- [ ] Proxy configured in vite.config.js?
- [ ] Using relative paths in fetch calls? (not `http://localhost:...`)
- [ ] Vite cache cleared? `Remove-Item frontend\node_modules\.vite -Recurse`

## Additional Resources

- [PowerShell Documentation](https://docs.microsoft.com/powershell/)
- [Windows Terminal Documentation](https://docs.microsoft.com/windows/terminal/)
- [Node.js on Windows Best Practices](https://nodejs.org/en/docs/guides/)
- [nvm-windows](https://github.com/coreybutler/nvm-windows)
