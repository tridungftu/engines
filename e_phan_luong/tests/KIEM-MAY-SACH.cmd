@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "PYTHONPATH="
set "PYTHONHOME="
set "PIP_NO_INDEX=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
set "BANH=%~1"
if not defined BANH set "BANH=%ROOT%\.venv\banh"
for %%I in ("%BANH%") do set "BANH=%%~fI"
set "WHEEL=%ROOT%\docs\goi-gui-engine\sdk-2.2.0\kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
python -B -c "import sys; assert sys.version_info >= (3,11), 'Can Python tu 3.11.'" || exit /b 1
python -B -c "import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest()=='0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984'" "%WHEEL%" || exit /b 1
for /f "delims=" %%I in ('python -B -c "import tempfile; print(tempfile.mkdtemp(prefix='kiem-phan-luong-DEMO-'))"') do set "TMP_DEMO=%%I"
if not defined TMP_DEMO exit /b 1
python -B -m venv "%TMP_DEMO%\venv" || exit /b 1
set "PY=%TMP_DEMO%\venv\Scripts\python.exe"
"%PY%" -B -m pip install --no-index --no-deps "%WHEEL%" || exit /b 1
"%PY%" -B -m pip install --no-index --find-links "%BANH%" --require-hashes --no-deps -r "%ROOT%\e_phan_luong\goi\e_phan_luong\requirements.lock" || exit /b 1
mkdir "%TMP_DEMO%\kiem\goi" || exit /b 1
mkdir "%TMP_DEMO%\kiem\tests" || exit /b 1
xcopy "%ROOT%\e_phan_luong\goi\e_phan_luong" "%TMP_DEMO%\kiem\goi\e_phan_luong\" /E /I /Q /Y >nul || exit /b 1
for %%T in (kiem_doc_lap.py kiem_bam_goi.py test_pl9c_dong_goi.py) do copy /Y "%ROOT%\e_phan_luong\tests\%%T" "%TMP_DEMO%\kiem\tests\" >nul || exit /b 1
pushd "%TMP_DEMO%\kiem" || exit /b 1
rem Adapter calls kiem_bam_goi.kiem with the package SQL inventory.
"%PY%" -X utf8 -B tests\test_pl9c_dong_goi.py --kiem-ke goi\e_phan_luong\sql\kiem_ke.json --phu-thuoc
if errorlevel 1 (popd & exit /b 1)
"%PY%" -X utf8 -B -m kho_tri_thuc_sdk.thu goi/e_phan_luong
set "MA_CLI=%ERRORLEVEL%"
"%PY%" -X utf8 -B tests\kiem_doc_lap.py
set "MA_DOC_LAP=%ERRORLEVEL%"
popd
rem Giu bang chung de Anh xem; khong xoa tep.
echo Moi truong kiem: %TMP_DEMO%
if not "%MA_DOC_LAP%"=="0" exit /b %MA_DOC_LAP%
exit /b %MA_CLI%
