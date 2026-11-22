@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "PYTHONPATH="
set "PYTHONHOME="
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
set "PY_GOC=%ROOT%\.venv\Scripts\python.exe"
if not exist "%PY_GOC%" set "PY_GOC=python"
set "BANH=%~1"
if not defined BANH set "BANH=%ROOT%\e_kiem_excel\goi\e_kiem_excel\wheels"
for %%I in ("%BANH%") do set "BANH=%%~fI"
set "WHEEL=%ROOT%\docs\goi-gui-engine\sdk-2.5.0\kho_tri_thuc_sdk-2.5.0-py3-none-any.whl"
"%PY_GOC%" -B -c "import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest()=='b235b513deb557f65f5a90c81e1d81e9b51799093fdaefb3bb5c5e1e954d2b55'" "%WHEEL%" || exit /b 1
if not exist "%ROOT%\.venv" mkdir "%ROOT%\.venv" || exit /b 1
for /f "delims=" %%I in ('call "%PY_GOC%" -B -c "import tempfile,sys; print(tempfile.mkdtemp(prefix='kiem-excel-DEMO-', dir=sys.argv[1]))" "%ROOT%\.venv"') do set "TMP_DEMO=%%I"
if not defined TMP_DEMO exit /b 1
"%PY_GOC%" -B -m venv "%TMP_DEMO%\venv" || exit /b 1
set "PY=%TMP_DEMO%\venv\Scripts\python.exe"
"%PY%" -I -X utf8 -B -m pip install --isolated --no-index --no-deps "%WHEEL%" || exit /b 1
"%PY%" -I -X utf8 -B -m pip install --isolated --no-index --find-links "%BANH%" --require-hashes --only-binary :all: --no-deps -r "%ROOT%\e_kiem_excel\goi\e_kiem_excel\requirements.lock" || exit /b 1
mkdir "%TMP_DEMO%\kiem\goi" || exit /b 1
mkdir "%TMP_DEMO%\kiem\tests" || exit /b 1
xcopy "%ROOT%\e_kiem_excel\goi\e_kiem_excel" "%TMP_DEMO%\kiem\goi\e_kiem_excel\" /E /I /Q /Y >nul || exit /b 1
copy /Y "%ROOT%\e_kiem_excel\tests\kiem_doc_lap.py" "%TMP_DEMO%\kiem\tests\" >nul || exit /b 1
copy /Y "%ROOT%\e_kiem_excel\tests\kiem_bam_goi.py" "%TMP_DEMO%\kiem\tests\" >nul || exit /b 1
copy /Y "%ROOT%\e_kiem_excel\tests\demo\bam-goi.json" "%TMP_DEMO%\kiem\tests\" >nul || exit /b 1
pushd "%TMP_DEMO%\kiem" || exit /b 1
"%PY%" -X utf8 -B tests\kiem_bam_goi.py --kiem-ke tests\bam-goi.json --goi goi/e_kiem_excel --phu-thuoc
if errorlevel 1 (popd & exit /b 1)
"%PY%" -X utf8 -B -m kho_tri_thuc_sdk.thu goi/e_kiem_excel
set "MA_CLI=%ERRORLEVEL%"
"%PY%" -X utf8 -B tests\kiem_doc_lap.py
set "MA_DOC_LAP=%ERRORLEVEL%"
popd
if not "%MA_DOC_LAP%"=="0" exit /b %MA_DOC_LAP%
rem Giu moi bang chung trong thu muc DEMO de Anh xem, khong xoa tep.
echo Moi truong kiem: %TMP_DEMO%
exit /b %MA_CLI%
