@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Chua tim thay Python. Hay cai Python 3.10 tro len va chon Add Python to PATH.
  pause
  exit /b 1
)
python app.py
if errorlevel 1 (
  echo.
  echo Loi khoi dong. Neu cong 8765 dang duoc su dung, hay dong CMD cu.
  pause
)
