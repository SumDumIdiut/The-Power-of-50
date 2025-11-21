"""
Beatmap loader for The Power of 50 (custom maps only)
Adds lead-in offset so notes appear on screen before they reach playhead
"""
import os
import sys
import json

# How many seconds ahead notes appear before playhead
NOTE_LEAD = 1.5  # seconds

def get_base_path():
    """Return the base folder for resources"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_beatmaps_folder():
    """Folder for custom beatmaps"""
    return os.path.join(get_base_path(), "beatmaps")

def get_difficulty_color(difficulty):
    colors = {
        "Beginner": (150, 255, 150),
        "Easy": (100, 255, 100),
        "Normal": (100, 200, 255),
        "Hard": (255, 200, 100),
        "Expert": (255, 150, 100),
        "Master": (255, 100, 100),
        "Extreme": (255, 50, 150),
        "Insane": (200, 50, 255),
        "Demon": (150, 0, 200),
        "God": (255, 215, 0),
    }
    return colors.get(difficulty, (100, 200, 255))

def load_beatmap(filepath):
    """Load a single beatmap JSON file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Apply lead-in to all notes
        notes = data.get("notes", [])
        for note in notes:
            note["time"] = max(0, note["time"] - NOTE_LEAD)

        beatmap = {
            "name": data.get("song_name", "Unknown"),
            "artist": data.get("artist", "Unknown"),
            "difficulty": data.get("difficulty", "Normal"),
            "bpm": data.get("bpm", 120),
            "stars": data.get("stars", 1),
            "color": get_difficulty_color(data.get("difficulty", "Normal")),
            "notes": notes,
            "song_file": data.get("song_file", ""),
            "filepath": filepath
        }

        folder = os.path.dirname(filepath)
        if beatmap["song_file"]:
            beatmap["song_path"] = os.path.join(folder, beatmap["song_file"])
            if not os.path.exists(beatmap["song_path"]):
                print(f"Warning: Song file missing: {beatmap['song_path']}")
                beatmap["song_path"] = None
        else:
            beatmap["song_path"] = None

        return beatmap
    except Exception as e:
        print(f"Failed to load beatmap {filepath}: {e}")
        return None

def scan_beatmaps():
    """Scan custom beatmaps folder"""
    folder = get_beatmaps_folder()
    beatmaps = []

    if not os.path.exists(folder):
        print(f"No custom beatmaps folder found at: {folder}")
        return beatmaps

    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            beatmap_file = os.path.join(item_path, "beatmap.json")
            if os.path.exists(beatmap_file):
                bm = load_beatmap(beatmap_file)
                if bm:
                    bm["folder"] = item_path
                    beatmaps.append(bm)
    return beatmaps
