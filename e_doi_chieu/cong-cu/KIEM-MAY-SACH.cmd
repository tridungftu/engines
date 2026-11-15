@echo off
setlocal
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
rem Mac dinh chay kho; them --cai chi khi da du wheel/hash duoc duyet.
rem Khong dung system-site-packages, khong tai mang.
python -B "%~dp0kiem_may_sach.py" %*
exit /b %errorlevel%
