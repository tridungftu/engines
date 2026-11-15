@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONPATH="
set "PYTHONHOME="
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
set "WHEEL=%ROOT%\docs\goi-gui-engine\sdk-2.0.0\kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
set "EXPECTED=a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892"
python -B -c "import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() == sys.argv[2]" "%WHEEL%" "%EXPECTED%" || exit /b 1
if not exist "%ROOT%\.venv" mkdir "%ROOT%\.venv" || exit /b 1
for /f "delims=" %%I in ('python -B -c "import tempfile,sys; print(tempfile.mkdtemp(prefix='hoa-don-DEMO-', dir=sys.argv[1]))" "%ROOT%\.venv"') do set "TMP_DEMO=%%I"
if not defined TMP_DEMO exit /b 1
python -B -m venv "%TMP_DEMO%\venv" || exit /b 1
"%TMP_DEMO%\venv\Scripts\python.exe" -B -m pip install --no-index --no-deps "%WHEEL%" || exit /b 1
mkdir "%TMP_DEMO%\kiem\goi" || exit /b 1
mkdir "%TMP_DEMO%\kiem\tests" || exit /b 1
xcopy "%ROOT%\e_hoa_don\goi\e_hoa_don" "%TMP_DEMO%\kiem\goi\e_hoa_don\" /E /I /Q /Y >nul || exit /b 1
copy /Y "%ROOT%\e_hoa_don\tests\kiem_doc_lap.py" "%TMP_DEMO%\kiem\tests\" >nul || exit /b 1
pushd "%TMP_DEMO%\kiem" || exit /b 1
"%TMP_DEMO%\venv\Scripts\python.exe" -B -m kho_tri_thuc_sdk.thu goi/e_hoa_don || exit /b 1
"%TMP_DEMO%\venv\Scripts\python.exe" -B tests\kiem_doc_lap.py || exit /b 1
popd
echo Clean install DEMO: DAT (CoreGia)
