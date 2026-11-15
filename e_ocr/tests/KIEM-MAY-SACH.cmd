@echo off
setlocal
set "ROOT=%~dp0..\.."
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
for /f "delims=" %%i in ('python -c "import tempfile; print(tempfile.mkdtemp(prefix=\"e-ocr-clean-\"))"') do set "VENV=%%i"
if not defined VENV exit /b 1
python -m venv "%VENV%" || exit /b 1
set "P=%VENV%\Scripts\python.exe"
"%P%" -c "import hashlib,pathlib,sys; assert hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest() == sys.argv[2]" "%ROOT%\docs\goi-gui-engine\sdk-2.2.0\kho_tri_thuc_sdk-2.2.0-py3-none-any.whl" 0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984 || exit /b 1
"%P%" -m pip install --no-index --no-deps "%ROOT%\docs\goi-gui-engine\sdk-2.2.0\kho_tri_thuc_sdk-2.2.0-py3-none-any.whl" || exit /b 1
"%P%" -m pip install --require-hashes --no-deps --only-binary=:all: -r "%ROOT%\e_ocr\goi\e_ocr\requirements.lock" || exit /b 1
"%P%" "%ROOT%\e_ocr\tests\chay_demo.py" --gia || exit /b 1
exit /b 0
