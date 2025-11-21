@echo off
title The Power of 50 - Build Script
chcp 65001 >nul
color 0A

echo =====================================================
echo          The Power of 50 - Build Script
echo =====================================================
echo.

:: --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.x from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python detected: %pythonversion%
echo.

:: --- Install PyInstaller if missing ---
echo Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
)
echo PyInstaller is ready.
echo.

:: --- Optional: Clean previous builds ---
set /p clean_build="Do you want to clean previous builds? (Y/N): "
if /I "%clean_build%"=="Y" (
    echo Cleaning build and dist folders...
    rmdir /s /q build 2>nul
    rmdir /s /q dist 2>nul
    del /q *.spec 2>nul
    echo Cleaned previous builds.
    echo.
)

:: --- Run the build ---
echo Building The Power of 50 executable...
echo.
python build_exe.py
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

:: --- Done ---
echo.
echo =====================================================
echo          Build complete! Check the 'dist' folder.
echo =====================================================
echo.
pause
