@echo off
chcp 65001 >nul
cd /d %~dp0
echo ========================================
echo 行政复议答复事项管理系统 - 环境检测
echo ========================================
echo.
echo [1] Python
where py
where python
echo.
echo [2] Node / npm
where node
where npm
echo.
echo [3] 项目文件
if exist backend\requirements.txt (echo OK backend\requirements.txt) else (echo 缺失 backend\requirements.txt)
if exist frontend\package.json (echo OK frontend\package.json) else (echo 缺失 frontend\package.json)
echo.
echo [4] 安装状态
if exist backend\.venv\Scripts\python.exe (echo OK backend\.venv) else (echo 未安装 backend\.venv)
if exist frontend\node_modules\.bin\vite.cmd (echo OK vite) else (echo 未安装前端依赖或 vite 缺失)
echo.
echo 检测完成。
pause
