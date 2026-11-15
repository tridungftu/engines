@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "MASK_PY=%~dp0..\..\.venv\Scripts\python.exe"
if not exist "%MASK_PY%" (
  echo Chua co .venv. Can cai SDK offline theo AGENTS.md.
  exit /b 2
)
rem Default: dry run, no network. Real DEMO: --that --url "IP URL" --model "model"
rem Optional: --bao-cao "file outside repository.json"
rem In repo: also --thu-muc-bao-cao "explicit report directory"
rem Deadline: --timeout SECONDS --timeout-toi-da SECONDS
"%MASK_PY%" -B "%~dp0thu_mask_local_ai_that.py" %*
exit /b %errorlevel%
