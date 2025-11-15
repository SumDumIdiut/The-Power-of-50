# The Power of 50

A collection of games themed around the number 50!

## Games

### 1. Snake
Collect 50 apples in this classic snake game with pixel art scoring.

### 2. Top-Down Shooter
Eliminate 50 enemies in procedurally generated dungeons with auto-aim and power-ups.

## How to Run

```bash
python main.py
```

## Controls

### Main Menu
- **↑↓**: Navigate between games
- **ENTER**: Select game
- **ESC**: Quit

### In-Game
Each game has its own controls - press ESC to return to the main menu.

## Project Structure

```
The Power of 50/
├── main.py                 # Main menu launcher
├── games/                  # Games folder
│   ├── snake/             # Snake game
│   │   ├── snake_game.py  # Game code
│   │   ├── helpers.py     # Helper functions
│   │   ├── assets/        # Game assets
│   │   └── README.md      # Game documentation
│   └── shooter/           # Shooter game
│       ├── shooter_game.py
│       ├── helpers.py
│       ├── assets/
│       └── README.md
├── Utils/                 # Reusable utilities
│   ├── portal.py         # Portal animation
│   ├── portal_helpers.py # Physics helpers
│   ├── textbox.py        # Dialogue system
│   └── README.md         # Utils documentation
└── dev/                   # Development tools

```

## Requirements

- Python 3.7+
- Pygame

```bash
pip install pygame
```

## Development

Each game is self-contained in its own folder with:
- Main game code
- Helper functions module
- Assets folder for game-specific resources
- README with game-specific documentation

## Credits

Created as a collection of 50-themed mini-games.
