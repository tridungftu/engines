@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "TC11_ROOT=%~dp0..\.."
if not exist "%TC11_ROOT%\.venv\Scripts\python.exe" (
  echo Chua co venv. Nho lead cai SDK offline theo AGENTS.md.
  exit /b 2
)
"%TC11_ROOT%\.venv\Scripts\python.exe" -B "%~dp0thu_tra_cuu_that.py" %*
exit /b %errorlevel%
