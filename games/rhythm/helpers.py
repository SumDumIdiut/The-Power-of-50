"""
Helper functions for the rhythm game
"""
import pygame
import os
import sys

# Sprite file names (in assets folder)
COVER_1_SPRITE = 'cover_1.png'
COVER_2_SPRITE = 'cover_2.png'
COVER_3_SPRITE = 'cover_3.png'
COVER_4_SPRITE = 'cover_4.png'
COVER_5_SPRITE = 'cover_5.png'
COVER_6_SPRITE = 'cover_6.png'
COVER_7_SPRITE = 'cover_7.png'
COVER_8_SPRITE = 'cover_8.png'
COVER_9_SPRITE = 'cover_9.png'
COVER_10_SPRITE = 'cover_10.png'
DRUM_SPRITE = 'drum.png'
NOTE_DON_SPRITE = 'note_don.png'
NOTE_KA_SPRITE = 'note_ka.png'
HIT_EFFECT_SPRITE = 'hit_effect.png'
BACKGROUND_SPRITE = 'background.png'
STAR_SPRITE = 'star.png'


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def load_sprite(sprite_name, size=None):
    """Load a sprite with fallback to None if not found"""
    try:
        assets_folder = os.path.join("games", "rhythm", "assets")
        full_path = resource_path(os.path.join(assets_folder, sprite_name))
        
        if os.path.exists(full_path):
            image = pygame.image.load(full_path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            return image
    except Exception as e:
        print(f"Could not load sprite {sprite_name}: {e}")
    
    return None


def load_assets():
    """Load all game assets with fallback to None"""
    assets = {}
    
    # Cover art for songs (300x300 large, 70x70 small)
    cover_sprites = [
        COVER_1_SPRITE, COVER_2_SPRITE, COVER_3_SPRITE, COVER_4_SPRITE, COVER_5_SPRITE,
        COVER_6_SPRITE, COVER_7_SPRITE, COVER_8_SPRITE, COVER_9_SPRITE, COVER_10_SPRITE
    ]
    
    for i, sprite_name in enumerate(cover_sprites, 1):
        assets[f'cover_{i}'] = load_sprite(sprite_name, (300, 300))
        assets[f'cover_small_{i}'] = load_sprite(sprite_name, (70, 70))
    
    # UI elements
    assets['drum'] = load_sprite(DRUM_SPRITE, (280, 280))
    assets['note_don'] = load_sprite(NOTE_DON_SPRITE, (70, 70))
    assets['note_ka'] = load_sprite(NOTE_KA_SPRITE, (70, 70))
    assets['hit_effect'] = load_sprite(HIT_EFFECT_SPRITE, (150, 150))
    assets['background'] = load_sprite(BACKGROUND_SPRITE)
    assets['star'] = load_sprite(STAR_SPRITE, (40, 40))
    
    return assets
