import os
import json
from typing import Dict, Any

# Single save file for the whole game
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'save.json')
SAVE_FILE = os.path.abspath(SAVE_FILE)

# Legacy rhythm progress file (to migrate from)
LEGACY_RHYTHM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'games', 'rhythm', 'beatmap_progress.json')
LEGACY_RHYTHM_FILE = os.path.abspath(LEGACY_RHYTHM_FILE)

DEFAULT_DATA: Dict[str, Any] = {
    "snake": {
        "completed": False
    },
    "shooter": {
        "won": False,
        "progress": 0  # You can decide what this means (levels, percent, etc.)
    },
    "rhythm": {
        "beatmaps": {},  # id -> best stars
    }
}


def _ensure_dirs():
    base_dir = os.path.dirname(SAVE_FILE)
    os.makedirs(base_dir, exist_ok=True)


def load_save() -> Dict[str, Any]:
    _ensure_dirs()
    data = DEFAULT_DATA.copy()
    # Deep copy nested dicts
    data["snake"] = dict(DEFAULT_DATA["snake"]) 
    data["shooter"] = dict(DEFAULT_DATA["shooter"]) 
    data["rhythm"] = {"beatmaps": dict(DEFAULT_DATA["rhythm"]["beatmaps"]) }

    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                on_disk = json.load(f)
                # Merge shallow
                for k, v in on_disk.items():
                    data[k] = v
        except Exception as e:
            print(f"Failed to load save.json: {e}")

    # Migrate legacy rhythm progress if present
    migrated = False
    if os.path.exists(LEGACY_RHYTHM_FILE):
        try:
            with open(LEGACY_RHYTHM_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
                if isinstance(legacy, dict):
                    beatmaps = data.setdefault("rhythm", {}).setdefault("beatmaps", {})
                    for bm_id, best in legacy.items():
                        try:
                            prev = int(beatmaps.get(bm_id, 0))
                            beatmaps[bm_id] = max(prev, int(best))
                            migrated = True
                        except Exception:
                            continue
        except Exception as e:
            print(f"Failed to migrate legacy rhythm progress: {e}")
        # Optionally delete legacy file after successful migration
        if migrated:
            try:
                os.remove(LEGACY_RHYTHM_FILE)
            except Exception:
                pass

    return data


def save_save(data: Dict[str, Any]) -> None:
    _ensure_dirs()
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to write save.json: {e}")


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


# Rhythm helpers

def get_rhythm_progress_map() -> Dict[str, int]:
    beatmaps = load_save().get("rhythm", {}).get("beatmaps", {})
    # Coerce to int
    return {k: int(v) for k, v in beatmaps.items()}

def update_rhythm_best(beatmap_id: str, new_best: int) -> None:
    data = load_save()
    bm = data.setdefault("rhythm", {}).setdefault("beatmaps", {})
    try:
        prev = int(bm.get(beatmap_id, 0))
        nb = max(prev, int(new_best))
        if nb != prev:
            bm[beatmap_id] = nb
            save_save(data)
    except Exception:
        pass

def get_total_rhythm_stars(cap: int = 50) -> int:
    total = sum(int(v) for v in get_rhythm_progress_map().values())
    return min(cap, total)
