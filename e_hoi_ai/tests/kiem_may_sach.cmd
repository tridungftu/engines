@echo off
setlocal
set "ROOT=%~dp0..\.."
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
if not defined PYTHON set "PYTHON=python"
:tao_thu_muc
set "TMP_VENV=%TEMP%\ktt-ai5-%RANDOM%-%RANDOM%"
if exist "%TMP_VENV%" goto tao_thu_muc
mkdir "%TMP_VENV%" || exit /b 1
"%PYTHON%" -m venv "%TMP_VENV%\venv" || goto loi
set "PY=%TMP_VENV%\venv\Scripts\python.exe"
"%PY%" -m pip install --no-index --no-deps "%ROOT%\docs\goi-gui-engine\sdk-2.0.0\kho_tri_thuc_sdk-2.0.0-py3-none-any.whl" || goto loi
"%PY%" -m pip install --no-index --no-deps -r "%ROOT%\e_hoi_ai\goi\e_hoi_ai\requirements.lock" || goto loi
"%PY%" "%ROOT%\e_hoi_ai\tests\chay_demo_voi_local_gia.py" || goto loi
rmdir /s /q "%TMP_VENV%"
exit /b 0
:loi
rmdir /s /q "%TMP_VENV%"
exit /b 1
