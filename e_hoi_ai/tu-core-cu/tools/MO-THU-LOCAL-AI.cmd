@echo off
setlocal
set PYTHONDONTWRITEBYTECODE=1
if not exist "D:\KTT-CD060-DEMO\python313\python.exe" (
  echo Python DEMO is unavailable.
  pause
  exit /b 2
)
if "%~1"=="" (
  "D:\KTT-CD060-DEMO\python313\python.exe" -X utf8 -B "%~dp0tools\thu_local_ai_that.py" --chay-kho
) else (
  "D:\KTT-CD060-DEMO\python313\python.exe" -X utf8 -B "%~dp0tools\thu_local_ai_that.py" %*
)
set "THU_LOCAL_EXIT=%ERRORLEVEL%"
pause
exit /b %THU_LOCAL_EXIT%
