# Project Structure

```
The Power of 50/
│
├── .github/
│   └── workflows/
│       └── build-release.yml   # Build and publish on version tag push
│
├── Assets/
│   └── Logo Test.png
│
├── dev/
│   └── menu.py                 # Dev launcher — runs Snake or Shooter directly
│
├── games/
│   ├── __init__.py
│   ├── snake/
│   │   ├── __init__.py
│   │   ├── snake_game.py
│   │   ├── snake_save.py
│   │   ├── helpers.py
│   │   ├── assets/
│   │   └── README.md
│   └── shooter/
│       ├── __init__.py
│       ├── shooter_game.py
│       ├── shooter_save.py
│       ├── tilemap.py
│       ├── wall_renderer.py
│       ├── helpers.py
│       └── README.md
│
├── Utils/
│   ├── __init__.py
│   ├── textbox.py              # Dialogue system
│   ├── save_manager.py         # Save/load helpers
│   └── README.md
│
├── build_exe.py                # PyInstaller build script
├── build.bat                   # Windows build helper
├── create_release.bat          # Tag, push, and trigger release
├── requirements.txt
└── README.md
```

## Games

| Game    | Entry point                     | Goal              |
|---------|---------------------------------|-------------------|
| Snake   | `games/snake/snake_game.py`     | Collect 50 apples |
| Shooter | `games/shooter/shooter_game.py` | Kill 50 enemies   |

## Utils

| Module           | Purpose                          |
|------------------|----------------------------------|
| `textbox.py`     | Animated dialogue / typewriter   |
| `save_manager.py`| JSON save and load helpers       |

## Adding a New Game

1. Create `games/<name>/` with at minimum `__init__.py` and `<name>_game.py`
2. Export a `run(screen)` function from `<name>_game.py`
3. Import and wire it up in `dev/menu.py`

## Adding a New Utility

Add a `.py` file to `Utils/` and update `Utils/README.md`.
