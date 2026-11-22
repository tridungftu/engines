@echo off
setlocal
set "ROOT=%~dp0..\.."
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "P=%ROOT%\.venv\Scripts\python.exe"
if not exist "%P%" set "P=python"
"%P%" -B -X utf8 "%ROOT%\e_ocr\tests\kiem_may_sach.py"
exit /b %errorlevel%
