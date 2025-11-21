"""
Beatmap loader for custom maps
"""
import json
import os
import pygame


def load_beatmap(filepath):
    """Load a beatmap from JSON file"""
    try:
        with open(filepath, 'r') as f:
            beatmap = json.load(f)
        
        return {
            'name': beatmap['song_name'],
            'artist': beatmap['artist'],
            'difficulty': beatmap['difficulty'],
            'bpm': beatmap['bpm'],
            'stars': beatmap['stars'],
            'color': get_difficulty_color(beatmap['difficulty']),
            'notes': beatmap['notes'],
            'song_file': beatmap.get('song_file', '')
        }
    except Exception as e:
        print(f"Failed to load beatmap {filepath}: {e}")
        return None


def get_difficulty_color(difficulty):
    """Get color for difficulty"""
    colors = {
        'Beginner': (150, 255, 150),
        'Easy': (100, 255, 100),
        'Normal': (100, 200, 255),
        'Hard': (255, 200, 100),
        'Expert': (255, 150, 100),
        'Master': (255, 100, 100),
        'Extreme': (255, 50, 150),
        'Insane': (200, 50, 255),
        'Demon': (150, 0, 200),
        'God': (255, 215, 0),
    }
    return colors.get(difficulty, (100, 200, 255))


def scan_beatmaps(folder='games/rhythm/beatmaps'):
    """Scan folder for beatmap bundles"""
    beatmaps = []
    
    if not os.path.exists(folder):
        os.makedirs(folder)
        return beatmaps
    
    # Look for subfolders containing beatmap.json
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            beatmap_file = os.path.join(item_path, 'beatmap.json')
            if os.path.exists(beatmap_file):
                beatmap = load_beatmap(beatmap_file)
                if beatmap:
                    beatmap['filepath'] = beatmap_file
                    beatmap['folder'] = item_path
                    
                    # --- FIX / PATH CONSTRUCTION LOGIC ---
                    # Construct the full, absolute path to the song file
                    # This ensures the game can locate the audio file relative to the beatmap folder.
                    if beatmap['song_file']:
                        beatmap['song_path'] = os.path.join(item_path, beatmap['song_file'])
                    # If 'song_file' is empty, 'song_path' remains unset or can be explicitly set to None
                    # for safety, though the check above handles the primary need.
                    # -------------------------------------
                        
                    beatmaps.append(beatmap)
    
    return beatmaps