@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "PIP_NO_INDEX=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
if not defined TC10_PYTHON set "TC10_PYTHON=python"
"%TC10_PYTHON%" -B "%~dp0kiem_may_sach.py" %*
exit /b %errorlevel%
