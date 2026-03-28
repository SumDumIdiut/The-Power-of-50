"""
Snake run save — stores in-progress game state.

Save file: games/snake/snake_save.json

Save data format:
{
  "seed":           "A3X7KP",
  "score":          12,
  "snake":          [[640, 360], [620, 360], ...],
  "direction":      [1, 0],
  "next_direction": [1, 0],
  "apple_pos":      [400, 300],
  "walls":          [[100, 200], ...],
  "wall_segments":  [[[100, 200]], ...],
  "move_timer":     3
}
"""
from __future__ import annotations
import json
import os
import random
import string

_DIR      = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(_DIR, 'snake_save.json')


def new_seed() -> str:
    """Return a random 6-character alphanumeric seed string."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=6))


def seed_to_int(seed: str) -> int:
    """Deterministic integer from a seed string (for random.Random seeding)."""
    h = 0
    for c in seed.upper():
        h = h * 31 + ord(c)
    return h & 0x7FFFFFFF


def has_save() -> bool:
    return os.path.exists(SAVE_PATH)


def load() -> dict | None:
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def save(data: dict) -> None:
    try:
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f'[snake_save] write failed: {e}')


def delete() -> None:
    try:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
    except Exception:
        pass
