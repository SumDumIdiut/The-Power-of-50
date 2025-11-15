@echo off
echo ========================================
echo The Power of 50 - Release Creator
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Current tags:
git tag
echo.

set /p VERSION="Enter version number (e.g., 1.0.0): "
if "%VERSION%"=="" (
    echo ERROR: Version number is required!
    pause
    exit /b 1
)

set TAG=v%VERSION%

echo.
echo Creating release %TAG%...
echo.

REM Add all changes
echo [1/5] Staging changes...
git add .

REM Commit changes
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "
if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=Release %TAG%
)
echo [2/5] Committing changes...
git commit -m "%COMMIT_MSG%"

REM Push to main
echo [3/5] Pushing to main branch...
git push origin main

REM Create and push tag
echo [4/5] Creating tag %TAG%...
git tag -a %TAG% -m "Release version %VERSION%"

echo [5/5] Pushing tag to GitHub...
git push origin %TAG%

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
echo Tag %TAG% has been created and pushed to GitHub.
echo GitHub Actions will now automatically:
echo   1. Build the executable
echo   2. Create a release
echo   3. Upload ThePowerOf50.exe
echo.
echo Check your GitHub repository's Actions tab to monitor progress.
echo The release will appear in the Releases section when complete.
echo.
pause
