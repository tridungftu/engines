@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
"%~dp0..\..\.venv\Scripts\python.exe" "%~dp0do_sua_tay_demo.py" --chay-kho %*
exit /b %errorlevel%
