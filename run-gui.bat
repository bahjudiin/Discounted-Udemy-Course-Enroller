@echo off
cd /d "%~dp0"
python gui.py
if errorlevel 1 (
    echo.
    echo ============================================
    echo Something went wrong. The error is above.
    echo ============================================
    pause
)