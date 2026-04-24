@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
set "LOG=%ROOT%logs\start.log"

echo ======================================== > "%LOG%"
echo ARLS Start System FINAL >> "%LOG%"
echo ======================================== >> "%LOG%"
echo Current Dir: %cd% >> "%LOG%"

if not exist "%ROOT%backend\requirements.txt" (
  call :log [ERROR] backend\requirements.txt not found
  goto :fail
)
if not exist "%ROOT%frontend\package.json" (
  call :log [ERROR] frontend\package.json not found
  goto :fail
)
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  call :log [ERROR] backend venv not found. Please run install first.
  goto :fail
)
if not exist "%ROOT%frontend\node_modules\.bin\vite.cmd" (
  call :log [ERROR] frontend dependencies not found. Please run install first.
  goto :fail
)

call :log [1/4] Cleaning old processes and port usage...
call :free_port 18080
call :free_port 18081
taskkill /FI "WINDOWTITLE eq ARLS Backend*" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq ARLS Frontend*" /T /F >nul 2>nul

call :log [2/4] Starting backend...
start "ARLS Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe run.py"
if errorlevel 1 (
  call :log [ERROR] Failed to start backend
  goto :fail
)

timeout /t 4 >nul
call :log [3/4] Starting frontend...
start "ARLS Frontend" cmd /k "cd /d %~dp0frontend && call npm run dev"
if errorlevel 1 (
  call :log [ERROR] Failed to start frontend
  goto :fail
)

timeout /t 8 >nul
call :log [4/4] Opening browser http://localhost:18080/
start "" "http://localhost:18080/"
if errorlevel 1 (
  call :log [WARN] Browser auto-open failed. Please open manually: http://localhost:18080/
)

echo.
echo System started.
echo Browser URL: http://localhost:18080/
echo Default user: admin
echo Default password: admin123
pause
exit /b 0

:free_port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%1 ^| findstr LISTENING') do taskkill /PID %%a /T /F >nul 2>nul
exit /b 0

:log
echo %*
echo %*>> "%LOG%"
exit /b 0

:fail
echo.
echo Start failed. Please send me this log file:
echo %LOG%
pause
exit /b 1
