@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONPATH="
set "PYTHONHOME="
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
set "BANH=%~1"
if not defined BANH set "BANH=%ROOT%\.venv\banh"
set "WHEEL=%ROOT%\docs\goi-gui-engine\sdk-2.2.0\kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
python -B -c "import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest()=='0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984'" "%WHEEL%" || exit /b 1
if not exist "%ROOT%\.venv" mkdir "%ROOT%\.venv" || exit /b 1
for /f "delims=" %%I in ('python -B -c "import tempfile,sys; print(tempfile.mkdtemp(prefix='kiem-excel-DEMO-', dir=sys.argv[1]))" "%ROOT%\.venv"') do set "TMP_DEMO=%%I"
if not defined TMP_DEMO exit /b 1
python -B -m venv "%TMP_DEMO%\venv" || exit /b 1
set "PY=%TMP_DEMO%\venv\Scripts\python.exe"
"%PY%" -B -m pip install --no-index --no-deps "%WHEEL%" || exit /b 1
"%PY%" -B -m pip install --no-index --find-links "%BANH%" --require-hashes --no-deps -r "%ROOT%\e_kiem_excel\goi\e_kiem_excel\requirements.lock" || exit /b 1
mkdir "%TMP_DEMO%\kiem\goi" || exit /b 1
mkdir "%TMP_DEMO%\kiem\tests" || exit /b 1
xcopy "%ROOT%\e_kiem_excel\goi\e_kiem_excel" "%TMP_DEMO%\kiem\goi\e_kiem_excel\" /E /I /Q /Y >nul || exit /b 1
copy /Y "%ROOT%\e_kiem_excel\tests\kiem_doc_lap.py" "%TMP_DEMO%\kiem\tests\" >nul || exit /b 1
pushd "%TMP_DEMO%\kiem" || exit /b 1
"%PY%" -X utf8 -B -m kho_tri_thuc_sdk.thu goi/e_kiem_excel
set "MA_CLI=%ERRORLEVEL%"
"%PY%" -X utf8 -B tests\kiem_doc_lap.py
set "MA_DOC_LAP=%ERRORLEVEL%"
popd
if not "%MA_DOC_LAP%"=="0" exit /b %MA_DOC_LAP%
rem EX-0: giu ma thoat CLI that, khong doi CHUA_LAM thanh XONG.
exit /b %MA_CLI%
