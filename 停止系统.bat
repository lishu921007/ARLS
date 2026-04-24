@echo off
chcp 65001 >nul
echo 正在关闭系统，请稍候...
taskkill /FI "WINDOWTITLE eq ARLS Backend*" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq ARLS Frontend*" /T /F >nul 2>nul
for %%p in (18080 18081) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING') do taskkill /PID %%a /T /F >nul 2>nul
)
echo 已停止。
pause
