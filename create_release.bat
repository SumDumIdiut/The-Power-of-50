@echo off
title The Power of 50 — Release Creator
chcp 65001 >nul

:: Color definitions
set GREEN=0A
set RED=0C
set YELLOW=0E
set CYAN=0B
set MAGENTA=0D
set GRAY=07

:: Banner
color %CYAN%
echo.
echo ======================================================
echo                 THE POWER OF 50 - RELEASE MAKER
echo ======================================================
echo.

:: Check Git
git --version >nul 2>&1
if errorlevel 1 (
    color %RED%
    echo ERROR: Git is not installed.
    echo Install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

color %GREEN%
echo Git detected.
echo.

:: List tags
color %YELLOW%
echo Current tags:
echo -------------------------
git tag
echo.

:: Prompt for version
set /p VERSION="Enter version number (e.g., 1.0.0): "
if "%VERSION%"=="" (
    color %RED%
    echo ERROR: Version number required.
    pause
    exit /b 1
)

set TAG=v%VERSION%

echo.
color %CYAN%
echo Creating release %TAG%...
echo.

:: Stage changes
color %MAGENTA%
echo [1/5] Staging changes...
git add .

:: Commit
set /p COMMIT_MSG="Enter commit message (press Enter for default): "
if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=Release %TAG%
)
echo [2/5] Committing...
git commit -m "%COMMIT_MSG%"

:: Push main
echo [3/5] Pushing to main branch...
git push origin main

:: Create tag
echo [4/5] Creating tag %TAG%...
git tag -a %TAG% -m "Release version %VERSION%"

:: Push tag
echo [5/5] Pushing tag to GitHub...
git push origin %TAG%

:: Done
color %GREEN%
echo.
echo ======================================================
echo                       SUCCESS
echo ======================================================
echo.
echo Tag %TAG% has been created and pushed.
echo GitHub Actions will now:
echo   1. Build the executable
echo   2. Create the release
echo   3. Upload ThePowerOf50.exe
echo.
echo Check the GitHub Actions tab to monitor progress.
echo.
pause