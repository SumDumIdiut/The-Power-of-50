# Build Instructions

## Quick Build (Recommended)

Double-click `build.bat` or run:
```bash
build.bat
```

This will check for PyInstaller, optionally clean previous builds, then run `build_exe.py`. The finished executable lands in `dist/ThePowerOf50.exe`.

## Manual Build

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the build script
```bash
python build_exe.py
```

### 3. Find the executable
```
dist/ThePowerOf50.exe
```

## Build Options

### Single file (`--onefile`) — default
- One portable `.exe`
- Slightly slower startup (extracts to temp on first run)
- Easiest to distribute

### Directory build (`--onedir`)
Remove `--onefile` from `build_exe.py` to produce a folder instead:
- Faster startup
- Larger distribution (folder with many files)

## Troubleshooting

**Missing assets at runtime**
Ensure `--add-data` paths in `build_exe.py` are correct. Windows uses `;` as the separator; Linux/Mac use `:`.

**ImportError on launch**
Add the missing module to the `hidden_imports` list in `build_exe.py`:
```python
"your.missing.module",
```

**Antivirus false positive**
PyInstaller-packed executables are sometimes flagged. Options:
- Add an antivirus exception for the `.exe`
- Switch to `--onedir` which tends to trigger fewer false positives
- Sign the executable with a code-signing certificate

## File Size

Expect roughly 50–100 MB due to the bundled Python runtime and Pygame. To reduce size:
- Use `--onedir` instead of `--onefile`
- Add UPX compression: install UPX, then pass `--upx-dir=path/to/upx` to PyInstaller
