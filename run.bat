@echo off
setlocal
title Gesture-based Intelligent AI Assistant

cd /d "%~dp0"

echo ======================================================
echo   Gesture-based Intelligent AI Assistant
echo ======================================================
echo.

if exist "venv\Scripts\activate.bat" goto :use_venv
goto :check_system_python

:use_venv
echo [INFO] Activating virtual environment: venv
call "venv\Scripts\activate.bat"
goto :run_app

:check_system_python
echo [WARNING] Virtual environment 'venv' not found.
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Using system Python...
    goto :run_app
)

echo [ERROR] Python was not found in your PATH.
echo Please install Python and set up the virtual environment:
echo   python -m venv venv
echo   venv\Scripts\activate
echo   pip install -r requirements.txt
echo.
pause
exit /b 1

:run_app
echo [INFO] Starting Gesture Assistant...
echo.

python src\gesture\hand_detector.py %*
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if %EXIT_CODE% neq 0 (
    echo [ERROR] Application terminated with error code %EXIT_CODE%.
) else (
    echo [INFO] Application closed successfully.
)

pause
exit /b %EXIT_CODE%
