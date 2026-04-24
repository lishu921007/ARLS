@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
set "LOGDIR=%ROOT%logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%" >nul 2>nul
set "LOG=%LOGDIR%\install.log"
set "NPM_CACHE_DIR=%ROOT%.npm-cache"
if not exist "%NPM_CACHE_DIR%" mkdir "%NPM_CACHE_DIR%" >nul 2>nul

echo ======================================== > "%LOG%"
echo ARLS One-Click Install v4 SAFE V2 >> "%LOG%"
echo ======================================== >> "%LOG%"
echo Current Dir: %cd% >> "%LOG%"
echo Log File: %LOG% >> "%LOG%"
echo NPM_CACHE_DIR: %NPM_CACHE_DIR% >> "%LOG%"

echo Installing... Please do not close this window.
call :log Installing... Please do not close this window.

if not exist "%ROOT%backend\requirements.txt" (
  call :log [ERROR] backend\requirements.txt not found.
  goto :fail
)
if not exist "%ROOT%frontend\package.json" (
  call :log [ERROR] frontend\package.json not found.
  goto :fail
)

set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 set "PY_CMD=py -3"
if not defined PY_CMD (
  where python >nul 2>nul
  if %errorlevel%==0 set "PY_CMD=python"
)
if not defined PY_CMD (
  call :log [ERROR] Python 3 not found.
  goto :fail
)
call :log Python command: %PY_CMD%

where npm >nul 2>nul
if errorlevel 1 (
  call :log [ERROR] npm not found. Please install Node.js LTS.
  goto :fail
)
call :log npm detected

call :log [1/6] Creating backend virtual environment...
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  %PY_CMD% -m venv "%ROOT%backend\.venv" >> "%LOG%" 2>&1
  if errorlevel 1 (
    call :log [ERROR] Failed to create venv
    goto :fail
  )
)

call :log [2/6] Upgrading pip...
"%ROOT%backend\.venv\Scripts\python.exe" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] Failed to upgrade pip
  goto :fail
)

call :log [3/6] Installing backend dependencies...
"%ROOT%backend\.venv\Scripts\pip.exe" install -r "%ROOT%backend\requirements.txt" >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] Failed to install backend dependencies
  goto :fail
)

call :log [4/6] Setting npm registry...
call npm config set registry https://registry.npmmirror.com/ >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] Failed to set npm registry
  goto :fail
)

call :log [5/6] Installing frontend dependencies with npm 10...
cd /d "%ROOT%frontend"
set "npm_config_cache=%NPM_CACHE_DIR%"
set "npm_config_fund=false"
set "npm_config_audit=false"
set "npm_config_prefer_online=true"

call :log Step A: prepare npm 10
call npx -y npm@10 -v >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [INFO] npx npm@10 failed, try global install
  call npm install -g npm@10 --registry=https://registry.npmmirror.com/ >> "%LOG%" 2>&1
  if errorlevel 1 (
    call :log [ERROR] Failed to prepare npm 10
    goto :fail
  )
)

call :log Step B: npm install
call npx -y npm@10 install --no-fund --no-audit >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [INFO] First install failed, clean cache and retry
  if exist "%NPM_CACHE_DIR%" rmdir /s /q "%NPM_CACHE_DIR%" >> "%LOG%" 2>&1
  mkdir "%NPM_CACHE_DIR%" >> "%LOG%" 2>&1
  call npm cache clean --force >> "%LOG%" 2>&1
  if exist node_modules rmdir /s /q node_modules >> "%LOG%" 2>&1
  if exist package-lock.json del /f /q package-lock.json >> "%LOG%" 2>&1
  call npx -y npm@10 install --no-fund --no-audit >> "%LOG%" 2>&1
  if errorlevel 1 (
    call :log [ERROR] Failed to install frontend dependencies
    goto :fail
  )
)

if not exist "node_modules\.bin\vite.cmd" (
  call :log [ERROR] vite.cmd not found after install
  goto :fail
)
call :log Frontend dependencies installed successfully.

call :log [6/6] Prebuilding frontend...
call npm run build >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [INFO] Frontend build failed, but runtime may still work.
) else (
  call :log Frontend build succeeded.
)

cd /d "%ROOT%"
call :log ========================================
call :log Installation completed
call :log Next step: run StartSystem.bat or 启动系统.bat
call :log ========================================

echo.
echo Installation completed.
echo If there is any issue, send me this log file:
echo %LOG%
pause
exit /b 0

:log
echo %*
echo %*>> "%LOG%"
exit /b 0

:fail
echo.
echo Installation failed. Please send me this log file:
echo %LOG%
pause
exit /b 1
