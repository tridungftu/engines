@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "ROOT=%~dp0..\.."
set "PY=%ROOT%\.venv\Scripts\python.exe"
if exist "%PY%" goto run
py -3 -m venv "%ROOT%\.venv"
if errorlevel 1 exit /b 1
"%PY%" -m pip install --no-index --no-deps "%ROOT%\docs\goi-gui-engine\sdk-2.0.0\kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
if errorlevel 1 exit /b 1
:run
echo Mac dinh chay kho. De chay that, them --that --url http://^<IP Tailscale may AI^>:^<cong^>
"%PY%" "%~dp0thu_local_ai_that.py" %*
exit /b %errorlevel%
