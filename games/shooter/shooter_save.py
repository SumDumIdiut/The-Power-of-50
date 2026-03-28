"""
Shooter run save — stores in-progress run state and best score.

Save file:  games/shooter/shooter_save.json
Best file:  games/shooter/shooter_best.json

Save data format:
{
  "seed":          "AB12CD34",
  "kills":         12,
  "player_x":      9000.0,
  "player_y":      9200.0,
  "player": {
    "health": 8, "fire_rate": 14, "multi_shot": 2,
    "damage": 6, "bullet_bounce": 1, "bullet_pierce": 0,
    "speed": 7.5, "has_orbital": false, "orbital_count": 0,
    "has_dual_gun": false, "dual_gun_count": 0,
    "bullet_explode": 0, "magnet": false
  }
}
"""
from __future__ import annotations
import json
import os
import random
import string

_DIR      = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(_DIR, 'shooter_save.json')
BEST_PATH = os.path.join(_DIR, 'shooter_best.json')


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def new_seed() -> str:
    """Return a random 8-character alphanumeric seed string."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


def seed_to_int(seed: str) -> int:
    """Deterministic integer from a seed string (for random.seed)."""
    h = 0
    for c in seed.upper():
        h = h * 31 + ord(c)
    return h & 0x7FFFFFFF


# ---------------------------------------------------------------------------
# Run save
# ---------------------------------------------------------------------------

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
        print(f'[shooter_save] write failed: {e}')


def delete() -> None:
    try:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Best score
# ---------------------------------------------------------------------------

def get_best_kills() -> int:
    try:
        if os.path.exists(BEST_PATH):
            with open(BEST_PATH, 'r', encoding='utf-8') as f:
                return int(json.load(f).get('best_kills', 0))
    except Exception:
        pass
    return 0


def update_best_kills(kills: int) -> None:
    if kills > get_best_kills():
        try:
            with open(BEST_PATH, 'w', encoding='utf-8') as f:
                json.dump({'best_kills': kills}, f)
        except Exception:
            pass
