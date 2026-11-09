@echo off
setlocal DisableDelayedExpansion
set "PYTHONDONTWRITEBYTECODE=1"
set "KTT_ABBYY_PY=D:\KTT-CD060-DEMO\python313\python.exe"
if not exist "%KTT_ABBYY_PY%" goto ThieuPython
"%KTT_ABBYY_PY%" -X utf8 -B "%~dp0abbyy_ket_noi_tam.py" dong %*
set "KTT_ABBYY_KQ=%ERRORLEVEL%"
echo.
echo Co the them --chay-kho de chi xem cac buoc, khong thay doi gi.
pause
exit /b %KTT_ABBYY_KQ%
:ThieuPython
echo Chua co Python cua phan mem. Can kiem tra bo chay da chuan bi.
pause
exit /b 1
