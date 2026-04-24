@echo off
cd /d %~dp0..\backend
start "ARLS Backend" cmd /k python -m venv .venv ^&^& call .venv\Scripts\activate.bat ^&^& pip install -r requirements.txt ^&^& python run.py
cd /d %~dp0..\frontend
start "ARLS Frontend" cmd /k npm install ^&^& npm run dev
timeout /t 5 >nul
start http://127.0.0.1:18080
