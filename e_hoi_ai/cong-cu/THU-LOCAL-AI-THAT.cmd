@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
"%~dp0..\..\.venv\Scripts\python.exe" "%~dp0thu_local_ai_that.py" %*
pause
