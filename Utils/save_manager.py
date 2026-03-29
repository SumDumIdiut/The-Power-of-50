import os
import json
from typing import Dict, Any

_APPDATA  = os.environ.get('APPDATA') or os.path.expanduser('~')
_SAVE_DIR = os.path.join(_APPDATA, 'ThePowerOf50')
SAVE_FILE = os.path.join(_SAVE_DIR, 'save.json')

DEFAULT_DATA: Dict[str, Any] = {
    "snake": {
        "completed": False,
    },
    "shooter": {
        "won": False,
        "progress": 0,
    },
}


def _ensure_dir() -> None:
    os.makedirs(_SAVE_DIR, exist_ok=True)


def load_save() -> Dict[str, Any]:
    _ensure_dir()
    data: Dict[str, Any] = {
        "snake":   dict(DEFAULT_DATA["snake"]),
        "shooter": dict(DEFAULT_DATA["shooter"]),
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                for k, v in json.load(f).items():
                    data[k] = v
        except Exception as e:
            print(f"[save_manager] load failed: {e}")
    return data


def save_save(data: Dict[str, Any]) -> None:
    _ensure_dir()
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[save_manager] write failed: {e}")


# Snake helpers

def mark_snake_completed() -> None:
    data = load_save()
    data.setdefault("snake", {})["completed"] = True
    save_save(data)

def is_snake_completed() -> bool:
    return bool(load_save().get("snake", {}).get("completed", False))


# Shooter helpers

def set_shooter_progress(value: int) -> None:
    data = load_save()
    data.setdefault("shooter", {})["progress"] = int(value)
    save_save(data)

def get_shooter_progress() -> int:
    try:
        return int(load_save().get("shooter", {}).get("progress", 0))
    except Exception:
        return 0

def set_shooter_won(won: bool) -> None:
    data = load_save()
    data.setdefault("shooter", {})["won"] = bool(won)
    save_save(data)

def is_shooter_won() -> bool:
    return bool(load_save().get("shooter", {}).get("won", False))
