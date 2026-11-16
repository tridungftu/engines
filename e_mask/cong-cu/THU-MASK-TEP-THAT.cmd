@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "B10_PY=%~dp0..\..\.venv\Scripts\python.exe"
if not exist "%B10_PY%" (
  echo Chua co .venv trong worktree. Hay cai SDK offline theo AGENTS.md.
  exit /b 1
)
rem Mac dinh chay kho: khong mang, Office, COM, macro, thay doi Windows.
rem --that chi Anh tu chon; thu muc hien vat phai moi va duoc quote.
rem Vi du: --that --doi-chung --ca D01 --thu-muc-demo "DEMO Office moi"
"%B10_PY%" -B "%~dp0thu_mask_tep_that.py" %*
exit /b %errorlevel%
