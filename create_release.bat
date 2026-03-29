@echo off
title The Power of 50 — Release Creator
chcp 65001 >nul
color 0B

echo.
echo ======================================================
echo             THE POWER OF 50 - RELEASE MAKER
echo ======================================================
echo.

:: Check Git
git --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Git is not installed.
    echo Install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

color 0A
echo Git detected.
echo.

:: List existing tags
color 0E
echo Current tags:
echo -------------------------
git tag
echo.

:: Prompt for version
set /p VERSION="Enter version number (e.g., 1.0.0): "
if "%VERSION%"=="" (
    color 0C
    echo ERROR: Version number required.
    pause
    exit /b 1
)

set TAG=v%VERSION%
color 0B
echo.
echo Creating release %TAG%...
echo.

:: Stage and commit
color 0D
echo [1/5] Staging changes...
git add .

set /p COMMIT_MSG="Enter commit message (press Enter for default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Release %TAG%

echo [2/5] Committing...
git commit -m "%COMMIT_MSG%"

:: Push main
echo [3/5] Pushing to main branch...
git push origin main

:: Create and push tag
echo [4/5] Creating tag %TAG%...
git tag -a %TAG% -m "Release version %VERSION%"

echo [5/5] Pushing tag to GitHub...
git push origin %TAG%

:: Done
color 0A
echo.
echo ======================================================
echo                       SUCCESS
echo ======================================================
echo.
echo Tag %TAG% has been created and pushed.
echo GitHub Actions will now build and publish the release.
echo.
pause
