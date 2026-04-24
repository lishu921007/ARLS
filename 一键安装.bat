@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d %~dp0

set "LOGDIR=%~dp0logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%" >nul 2>nul
set "LOG=%LOGDIR%\install.log"
set "NPM_CACHE_DIR=%~dp0.npm-cache"
if not exist "%NPM_CACHE_DIR%" mkdir "%NPM_CACHE_DIR%" >nul 2>nul

> "%LOG%" echo ========================================
>> "%LOG%" echo ARLS One-Click Install v4 (Force npm10)
>> "%LOG%" echo ========================================
>> "%LOG%" echo Current Dir: %cd%
>> "%LOG%" echo Log File: %LOG%
>> "%LOG%" echo NPM_CACHE_DIR: %NPM_CACHE_DIR%

echo Installing... Please do not close this window.
call :log Installing... Please do not close this window.

call :check_project
if errorlevel 1 goto :fail

call :find_python
if errorlevel 1 goto :fail

call :find_npm
if errorlevel 1 goto :fail

call :log [1/6] Creating backend virtual environment...
if not exist "backend\.venv\Scripts\python.exe" (
  %PY_CMD% -m venv backend\.venv >> "%LOG%" 2>&1
  if errorlevel 1 (
    call :log [ERROR] Failed to create backend virtual environment
    goto :fail
  )
)

call :log [2/6] Upgrading pip...
backend\.venv\Scripts\python.exe -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] Failed to upgrade pip
  goto :fail
)

call :log [3/6] Installing backend dependencies...
backend\.venv\Scripts\pip.exe install -r backend\requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] Failed to install backend dependencies
  goto :fail
)

call :log [4/6] Checking npm registry...
set "CURRENT_REG="
for /f "delims=" %%i in ('npm config get registry 2^>nul') do set "CURRENT_REG=%%i"
call :log Current npm registry: !CURRENT_REG!
if /I not "!CURRENT_REG!"=="https://registry.npmmirror.com/" (
  npm config set registry https://registry.npmmirror.com/ >> "%LOG%" 2>&1
)

call :log [5/6] Installing frontend dependencies with npm@10...
cd /d "%~dp0frontend"
set "npm_config_cache=%NPM_CACHE_DIR%"
set "npm_config_fund=false"
set "npm_config_audit=false"
set "npm_config_prefer_online=true"

call :log Step A: verify npm@10 availability
npx -y npm@10 -v >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [INFO] npx npm@10 failed, trying global npm@10 install
  npm install -g npm@10 --registry=https://registry.npmmirror.com/ >> "%LOG%" 2>&1
  if errorlevel 1 (
    call :log [ERROR] Failed to prepare npm@10
    goto :fail
  )
)

call :log Step B: install frontend dependencies using npm@10
npx -y npm@10 install --no-fund --no-audit >> "%LOG%" 2>&1
if not errorlevel 1 goto frontend_done_main

call :log [INFO] npm@10 install via npx failed, trying current npm after npm@10 global prep
npm install --no-fund --no-audit >> "%LOG%" 2>&1
if not errorlevel 1 goto frontend_done_main

call :log [INFO] Retry after cache cleanup
if exist "%NPM_CACHE_DIR%" rmdir /s /q "%NPM_CACHE_DIR%" >> "%LOG%" 2>&1
mkdir "%NPM_CACHE_DIR%" >> "%LOG%" 2>&1
npm cache clean --force >> "%LOG%" 2>&1
npx -y npm@10 install --no-fund --no-audit >> "%LOG%" 2>&1
if not errorlevel 1 goto frontend_done_main

call :log [INFO] Final retry after removing node_modules and package-lock.json
if exist node_modules (
  rmdir /s /q node_modules >> "%LOG%" 2>&1
)
if exist package-lock.json (
  del /f /q package-lock.json >> "%LOG%" 2>&1
)
npx -y npm@10 install --no-fund --no-audit >> "%LOG%" 2>&1
if not errorlevel 1 goto frontend_done_main

call :log [ERROR] Frontend dependency installation failed
goto :fail

:frontend_done_main
if not exist "node_modules\.bin\vite.cmd" (
  call :log [ERROR] vite.cmd not found after frontend install
  goto :fail
)
call :log Frontend dependencies installed successfully. vite.cmd detected.

call :log [6/6] Prebuilding frontend (failure does not block startup)...
npm run build >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [INFO] Frontend build failed, but dev mode can still be used.
) else (
  call :log Frontend build succeeded.
)

cd /d "%~dp0"
call :log ========================================
call :log Installation completed
call :log Next step: double-click StartSystem.bat or 启动系统.bat
call :log ========================================

echo.
echo Installation completed.
echo Next step: double-click StartSystem.bat or 启动系统.bat
echo If there is any issue, send me this log file:
echo %LOG%
pause
exit /b 0

:check_project
if not exist "backend\requirements.txt" (
  call :log [ERROR] backend\requirements.txt not found. Please ensure the package is fully extracted.
  exit /b 1
)
if not exist "frontend\package.json" (
  call :log [ERROR] frontend\package.json not found. Please ensure the package is fully extracted.
  exit /b 1
)
exit /b 0

:find_python
set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=py -3"
  call :log Python launcher detected: py -3
  exit /b 0
)
where python >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=python"
  call :log Python detected: python
  exit /b 0
)
call :log [ERROR] Python not found. Please install Python 3.11+ and add it to PATH.
exit /b 1

:find_npm
where npm >nul 2>nul
if %errorlevel%==0 (
  call :log npm detected
  exit /b 0
)
call :log [ERROR] npm not found. Please install Node.js LTS.
exit /b 1

:log
echo %*
>> "%LOG%" echo %*
exit /b 0

:fail
echo.
echo Installation failed. Please send me this log file:
echo %LOG%
pause
exit /b 1
