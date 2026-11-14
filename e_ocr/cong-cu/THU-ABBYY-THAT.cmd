@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "ROOT=%~dp0..\.."
set "PY=%ROOT%\.venv\Scripts\python.exe"
if exist "%PY%" goto install
py -3 -m venv --system-site-packages "%ROOT%\.venv"
if errorlevel 1 exit /b 1
:install
"%PY%" -m pip install --no-index --no-deps "%ROOT%\docs\goi-gui-engine\sdk-2.0.0\kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
if errorlevel 1 exit /b 1
echo Mac dinh chay kho; --that can cau hinh va thu muc DEMO rieng.
"%PY%" "%~dp0thu_abbyy_that.py" %*
exit /b %errorlevel%
