@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
"%~dp0..\..\.venv\Scripts\python.exe" -B "%~dp0thu_doi_chieu_that.py" %*
exit /b %errorlevel%
