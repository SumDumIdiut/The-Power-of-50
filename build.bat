@echo off
echo Installing PyInstaller if needed...
pip install pyinstaller

echo.
echo Building The Power of 50 executable...
echo.

python build_exe.py

echo.
echo Build complete! Check the 'dist' folder for ThePowerOf50.exe
pause
