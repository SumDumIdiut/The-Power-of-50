# The Power of 50 🎮

A collection of three arcade-style games where the goal is always to reach 50!

## 🎯 Games Included

### 🐍 Snake Game
Classic snake gameplay - eat 50 apples to win!
- Smooth controls
- Progressive difficulty
- Score tracking

### 🔫 Shooter Game
Top-down shooter with procedurally generated levels using a tilemap system.
- Kill 50 enemies to win
- Color-coded tiles (Green/Red/Blue based on neighbors)
- Boss battles every 10 kills
- Power-ups and upgrades
- Large open arenas

### 🗼 Tower Defense
Defend your base against waves of enemies!
- Strategic tower placement
- Multiple tower types
- Wave-based gameplay

## 📥 Download & Play

### Option 1: Download Executable (Recommended)
1. Go to [Releases](../../releases)
2. Download the latest `ThePowerOf50.exe`
3. Run it - no installation needed!

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/the-power-of-50.git
cd the-power-of-50

# Install dependencies
pip install -r requirements.txt

# Run the game
python dev/menu.py
```

## 🛠️ Development

### Project Structure
```
The Power of 50/
├── .github/workflows/    # GitHub Actions for automated builds
├── Assets/              # Global assets (logo, etc.)
├── dev/                 # Development entry point
│   └── menu.py         # Main menu system
├── games/              # Game modules
│   ├── snake/          # Snake game
│   ├── shooter/        # Shooter game with tilemap
│   │   ├── tilemap.py
│   │   └── wall_renderer.py
│   └── tower_defense/  # Tower Defense game
├── Utils/              # Shared utilities
│   ├── portal.py       # Portal animation
│   └── textbox.py      # Dialogue system
├── build_exe.py        # Build script for executable
└── requirements.txt    # Python dependencies
```

### Building the Executable

```bash
# Install build dependencies
pip install pyinstaller

# Build the executable
python build_exe.py

# Output will be in dist/ThePowerOf50.exe
```

### Creating a Release

Releases are automated via GitHub Actions:

1. **Create a version tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **GitHub Actions will automatically:**
   - Build the executable
   - Create a GitHub release
   - Upload the .exe file
   - Generate release notes

## 🎨 Features

### Shooter Game Tilemap System
- **Procedural Generation**: Rooms and corridors generated algorithmically
- **Color-Coded Tiles**: 
  - 🟢 Green: 4 neighbors (interior walls)
  - 🔴 Red: 3 neighbors (edges)
  - 🔵 Blue: 2 neighbors (corners)
- **Smart Collision**: Only collides on exposed tile edges
- **Performance Optimized**: Merged tiles and chunk-based rendering

## 🔧 Technologies

- **Python 3.12**
- **Pygame 2.6+**
- **PyInstaller** (for executable builds)
- **GitHub Actions** (for automated releases)

## 📋 Requirements

### For Playing (Executable)
- Windows 10/11
- ~35 MB disk space

### For Development
- Python 3.11+
- Pygame 2.0+
- See `requirements.txt` for full list

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

This project is open source and available under the MIT License.

## 🎮 Controls

### Snake Game
- Arrow Keys: Move
- ESC: Return to menu

### Shooter Game
- WASD: Move
- Mouse: Auto-aim
- Auto-fire enabled
- ESC: Return to menu

### Tower Defense
- Mouse: Place towers
- Click: Select/Place
- ESC: Return to menu

## 🚀 Roadmap

- [ ] Add more game modes
- [ ] Implement high score system
- [ ] Add sound effects and music
- [ ] Create level editor for shooter
- [ ] Add multiplayer support

---

Made with ❤️ using Python and Pygame
