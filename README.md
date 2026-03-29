# The Power of 50

A collection of arcade-style games where the goal is always to reach 50.

## Games

### Snake
Classic snake — eat 50 apples to win.
- Progressive difficulty
- Score tracking and high score saving

### Shooter
Top-down shooter with procedurally generated dungeons.
- Kill 50 enemies to win
- Auto-aim and auto-fire
- Boss battles every 10 kills
- Power-up drops (fire rate, multi-shot, damage)
- One hit = death

## Download & Play

**Option 1 — Executable (recommended):**
1. Go to [Releases](../../releases)
2. Download `ThePowerOf50.exe`
3. Run it — no installation needed

**Option 2 — Run from source:**
```bash
git clone https://github.com/YOUR_USERNAME/the-power-of-50.git
cd the-power-of-50
pip install -r requirements.txt
python dev/menu.py
```

## Controls

| Game    | Action       | Input            |
|---------|--------------|------------------|
| Snake   | Move         | Arrow Keys       |
| Snake   | Quit to menu | ESC              |
| Shooter | Move         | WASD / Arrow Keys|
| Shooter | Manual aim   | IJKL (optional)  |
| Shooter | Quit to menu | ESC              |

## Project Structure

```
The Power of 50/
├── .github/workflows/    # Automated build and release
├── Assets/               # Shared assets (logo, etc.)
├── dev/
│   └── menu.py           # Dev launcher
├── games/
│   ├── snake/            # Snake game
│   └── shooter/          # Shooter game
├── Utils/
│   ├── textbox.py        # Dialogue system
│   └── save_manager.py   # Save/load helpers
├── build_exe.py          # PyInstaller build script
├── build.bat             # Windows build helper
├── create_release.bat    # Tag and release helper
└── requirements.txt
```

## Building

```bash
# Quick build (Windows)
build.bat

# Or directly
python build_exe.py
# Output: dist/ThePowerOf50.exe
```

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for more detail.

## Releasing

```bash
create_release.bat
```

Pushes a version tag which triggers GitHub Actions to build and publish the release automatically. See [SETUP_GITHUB.md](SETUP_GITHUB.md) for first-time setup.

## Tech Stack

- Python 3.12
- Pygame 2.6+
- PyInstaller (executable builds)
- GitHub Actions (automated releases)

## Requirements

| Use case    | Requirements                    |
|-------------|---------------------------------|
| Playing     | Windows 10/11, ~50–100 MB space |
| Development | Python 3.11+, `pip install -r requirements.txt` |
