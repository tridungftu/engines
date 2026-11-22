@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
if not defined PYTHON set "PYTHON=%~dp0..\..\.venv\Scripts\python.exe"
rem Python helper creates a new venv and installs the wheel --no-index --no-deps.
rem No system-site-packages. Keep the venv as evidence, no recursive deletion.
"%PYTHON%" -B "%~dp0kiem_may_sach.py" --tao-venv %*
exit /b %errorlevel%
