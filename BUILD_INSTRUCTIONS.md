# Building The Power of 50 Executable

## Quick Build (Recommended)

Simply double-click `build.bat` or run:
```bash
build.bat
```

This will:
1. Install PyInstaller if needed
2. Build the executable
3. Place it in the `dist` folder

## Manual Build

If you prefer to build manually:

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Run PyInstaller
```bash
pyinstaller --name=ThePowerOf50 --onefile --windowed --add-data="Assets;Assets" --add-data="games;games" --add-data="Utils;Utils" --hidden-import=pygame dev/menu.py
```

### 3. Find Your Executable
The executable will be in: `dist/ThePowerOf50.exe`

## Build Options

### Single File (Recommended)
- Uses `--onefile` flag
- Creates one portable .exe file
- Slower startup (extracts to temp folder)
- Easier to distribute

### Directory Build (Faster Startup)
Remove `--onefile` from the command to create a folder with the .exe and dependencies
- Faster startup
- Larger distribution size (folder with multiple files)

## Troubleshooting

### Missing Assets
If assets don't load, make sure the `--add-data` paths are correct:
- Windows: `--add-data="Assets;Assets"`
- Linux/Mac: `--add-data="Assets:Assets"`

### Import Errors
Add missing modules with `--hidden-import=module_name`

### Antivirus False Positives
Some antivirus software may flag PyInstaller executables. This is normal.
You can:
1. Add an exception for your exe
2. Sign the executable with a code signing certificate
3. Use `--onedir` instead of `--onefile`

## File Size

The executable will be approximately 50-100 MB due to:
- Python runtime
- Pygame library
- Game assets

To reduce size:
- Use `--onedir` instead of `--onefile`
- Use UPX compression: `pip install upx` then add `--upx-dir=path/to/upx`
