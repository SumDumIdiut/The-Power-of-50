# Utils

Shared utilities used across the games.

## textbox.py

Animated dialogue system with typewriter text effect.

**Features:**
- Typewriter character-by-character reveal
- Speaker highlighting
- Dialogue sequence support

**Usage:**
```python
from Utils.textbox import Textbox

textbox = Textbox(screen)
result = textbox.run()  # returns 'menu' or 'quit'
```

**Controls:**
- `SPACE` — advance / skip text animation
- `ESC` — exit

## save_manager.py

JSON-based save and load helpers used by the game modules. Saves to `%APPDATA%\ThePowerOf50\save.json`.

**Usage:**
```python
from Utils.save_manager import save_save, load_save

data = load_save()
save_save(data)
```

---

## Guidelines for New Utilities

- Keep them generic — no game-specific logic
- Export a clear public interface
- Update this README when adding a new module
