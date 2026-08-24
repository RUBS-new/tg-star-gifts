@echo off
chcp 65001 > nul
title Telegram Star Gifts

echo ========================================================
echo   Telegram Star Gifts Sender (MTProto)
echo ========================================================
echo.

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [*] First start: creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [*] Installing requirements...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo [*] Starting server...
python app.py

pause
