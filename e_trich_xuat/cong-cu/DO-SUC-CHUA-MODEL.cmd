@echo off
setlocal
set "TX6_ROOT=%~dp0..\.."
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
if not defined PYTHON set "PYTHON=python"
if exist "%TX6_ROOT%\.venv\Scripts\python.exe" goto chay
"%PYTHON%" -B -m venv "%TX6_ROOT%\.venv" || exit /b 2
:chay
"%TX6_ROOT%\.venv\Scripts\python.exe" -B -m pip install --no-compile --no-index --no-deps "%TX6_ROOT%\docs\goi-gui-engine\sdk-2.2.0\kho_tri_thuc_sdk-2.2.0-py3-none-any.whl" || exit /b 2
if not defined TX7_KHO_WHEEL set "TX7_KHO_WHEEL=%TX6_ROOT%\.venv\offline-wheels"
"%TX6_ROOT%\.venv\Scripts\python.exe" -B -m pip install --no-compile --no-index --no-deps --find-links "%TX7_KHO_WHEEL%" -r "%TX6_ROOT%\e_trich_xuat\goi\e_trich_xuat\requirements.lock" || exit /b 2
"%TX6_ROOT%\.venv\Scripts\python.exe" -B "%~dp0do_suc_chua_model.py" %*
exit /b %errorlevel%
