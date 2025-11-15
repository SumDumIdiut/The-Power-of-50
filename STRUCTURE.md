# Project Structure

## Current Structure

```
The Power of 50/
│
├── main.py                    # Main menu launcher
├── run.bat                    # Windows shortcut
│
├── games/                     # Games (2 games)
│   ├── snake/
│   │   ├── snake_game.py
│   │   ├── helpers.py
│   │   ├── assets/
│   │   └── README.md
│   └── shooter/
│       ├── shooter_game.py
│       ├── helpers.py
│       ├── assets/
│       └── README.md
│
├── Utils/                     # Utilities (not games)
│   ├── portal.py             # Portal animation
│   ├── portal_helpers.py     # Physics helpers
│   ├── textbox.py            # Dialogue system
│   ├── __init__.py
│   └── README.md
│
└── dev/                       # Development tools
    ├── menu.py               # Dev menu
    └── README.md
```

## Games vs Utils

### Games (in `games/`)
- **Snake**: Collect 50 apples
- **Shooter**: Kill 50 enemies

### Utils (in `Utils/`)
- **Portal**: Interactive animation (not a game)
- **Textbox**: Dialogue system
- **Portal Helpers**: Physics utilities

## Why Portal is a Utility

Portal is an **animation/demo**, not a game with a goal. It's a reusable component that demonstrates:
- Physics simulation
- Particle effects
- Interactive animations

It belongs in Utils because it's a **tool/component**, not a standalone game.

## How to Use

### Play Games
```bash
python main.py
```

### Test with Dev Menu
```bash
python dev/menu.py
```

### Use Utilities
```python
from Utils.portal import PortalAnimation
from Utils.textbox import Textbox

# Use in your own games
```

## Adding New Content

### New Game
Add to `games/[gamename]/`

### New Utility
Add to `Utils/`

Portal is correctly categorized as a utility! ✅
