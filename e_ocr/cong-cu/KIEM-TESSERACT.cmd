@echo off
setlocal
if not "%~1"=="" goto cau_hinh
where tesseract.exe >nul 2>nul
if errorlevel 1 goto mac_dinh
set "TESSERACT=tesseract.exe"
goto kiem
:mac_dinh
set "TESSERACT=%ProgramFiles%\Tesseract-OCR\tesseract.exe"
goto kiem
:cau_hinh
set "TESSERACT=%~1"
:kiem
"%TESSERACT%" --version >nul 2>nul
if errorlevel 1 goto can_cai
"%TESSERACT%" --list-langs 2>nul | findstr /x /c:"vie" >nul
if errorlevel 1 goto can_ngon_ngu
"%TESSERACT%" --list-langs 2>nul | findstr /x /c:"eng" >nul
if errorlevel 1 goto can_ngon_ngu
echo [DAT] Da co Tesseract va du ngon ngu vie+eng.
echo Cau hinh tesseract.duong_dan neu khong dung PATH/vi tri mac dinh.
exit /b 0
:can_cai
echo [CAN CAI] Chua tim thay Tesseract hoac chua chay duoc.
echo Anh tu cai bo Tesseract Windows x64 offline da duoc phe duyet.
echo Chon ca ngon ngu tieng Viet va tieng Anh khi cai.
echo Chay lai: KIEM-TESSERACT.cmd "duong-dan-toi-tesseract.exe"
exit /b 1
:can_ngon_ngu
echo [CAN CAI] Thieu ngon ngu vie hoac eng.
echo Anh bo sung vie.traineddata va eng.traineddata bang bo cai offline.
echo Chay lai KIEM-TESSERACT.cmd de kiem tra, roi dat ngon_ngu=vie+eng.
exit /b 2
