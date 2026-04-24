@echo off
cd /d %~dp0..\backend
call .venv\Scripts\activate.bat
python -c "from app.db.init_db import init_db; init_db(); print('db ok')"
powershell -Command "Copy-Item '.\data\app.db' '.\data\backups\app_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db'"
