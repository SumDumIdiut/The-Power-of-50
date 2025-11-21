"""
Rhythm Game - Taiko no Tatsujin style
Hit 50 notes to win!
"""
import pygame
import math
import random
import os
import sys

# Import beatmap loader for custom maps
try:
    from games.rhythm import beatmap_loader
except ImportError:
    try:
        import beatmap_loader
    except ImportError:
        beatmap_loader = None

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
DRUM_OUTER_CIRCLE_SPRITE = 'drum_outer_circle.png'
NOTE_DON_SPRITE = 'note_don.png'
NOTE_KA_SPRITE = 'note_ka.png'
HIT_EFFECT_SPRITE = 'hit_effect.png'
STAR_SPRITE = 'star.png'
EMPTY_STAR_SPRITE = 'empty_star.png'
RANK_S_PLUS_SPRITE = 'rank_s_plus.png'
RANK_S_SPRITE = 'rank_s.png'
RANK_A_SPRITE = 'rank_a.png'
RANK_B_SPRITE = 'rank_b.png'
RANK_C_SPRITE = 'rank_c.png'
RANK_D_SPRITE = 'rank_d.png'
RANK_F_SPRITE = 'rank_f.png'
# Difficulty bars for song selector
BAR_BEGINNER_SPRITE = 'bar_beginner.png'
BAR_EASY_SPRITE = 'bar_easy.png'
BAR_NORMAL_SPRITE = 'bar_normal.png'
BAR_HARD_SPRITE = 'bar_hard.png'
BAR_EXPERT_SPRITE = 'bar_expert.png'
BAR_MASTER_SPRITE = 'bar_master.png'
BAR_EXTREME_SPRITE = 'bar_extreme.png'
BAR_INSANE_SPRITE = 'bar_insane.png'
BAR_DEMON_SPRITE = 'bar_demon.png'
BAR_GOD_SPRITE = 'bar_god.png'
BAR_SELECTED_SPRITE = 'bar_selected.png'  # Highlighted bar
# Backgrounds
SONG_SELECT_BG_SPRITE = 'song_select_bg.png'
GAMEPLAY_BG_SPRITE = 'gameplay_bg.png'
WOOD_PLANK_SPRITE = 'wood_plank.png'  # For track
# UI elements
STATS_BG_SPRITE = 'stats_bg.png'  # Top bar background
VICTORY_BG_SPRITE = 'victory_bg.png'

# Load all game assets at module level
ASSETS = None

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_sprite(sprite_name, size=None):
    """Load a sprite with fallback to None if not found"""
    try:
        # Look directly in games/rhythm/assets folder
        assets_folder = os.path.join("games", "rhythm", "assets")
        full_path = os.path.join(assets_folder, sprite_name)
        
        if os.path.exists(full_path):
            image = pygame.image.load(full_path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            return image
    except Exception as e:
        print(f"Could not load sprite {sprite_name}: {e}")
    return None

def init_assets():
    """Initialize assets (call after pygame.init())"""
    global ASSETS
    if ASSETS is None:
        ASSETS = {}
        
        # Cover art for songs (300x300 large, 70x70 small)
        cover_sprites = [
            COVER_1_SPRITE, COVER_2_SPRITE, COVER_3_SPRITE, COVER_4_SPRITE, COVER_5_SPRITE,
            COVER_6_SPRITE, COVER_7_SPRITE, COVER_8_SPRITE, COVER_9_SPRITE, COVER_10_SPRITE
        ]
        
        for i, sprite_name in enumerate(cover_sprites, 1):
            ASSETS[f'cover_{i}'] = load_sprite(sprite_name, (300, 300))
            ASSETS[f'cover_small_{i}'] = load_sprite(sprite_name, (70, 70))
        
        # Drum and notes
        ASSETS['drum'] = load_sprite(DRUM_SPRITE, (280, 280))
        ASSETS['drum_outer_circle'] = load_sprite(DRUM_OUTER_CIRCLE_SPRITE, (400, 400))
        ASSETS['note_don'] = load_sprite(NOTE_DON_SPRITE, (70, 70))
        ASSETS['note_ka'] = load_sprite(NOTE_KA_SPRITE, (70, 70))
        
        # Effects
        ASSETS['hit_effect'] = load_sprite(HIT_EFFECT_SPRITE, (150, 150))
        ASSETS['star'] = load_sprite(STAR_SPRITE, (40, 40))
        ASSETS['empty_star'] = load_sprite(EMPTY_STAR_SPRITE, (40, 40))
        
        # Rank sprites
        ASSETS['rank_s_plus'] = load_sprite(RANK_S_PLUS_SPRITE, (150, 150))
        ASSETS['rank_s'] = load_sprite(RANK_S_SPRITE, (150, 150))
        ASSETS['rank_a'] = load_sprite(RANK_A_SPRITE, (150, 150))
        ASSETS['rank_b'] = load_sprite(RANK_B_SPRITE, (150, 150))
        ASSETS['rank_c'] = load_sprite(RANK_C_SPRITE, (150, 150))
        ASSETS['rank_d'] = load_sprite(RANK_D_SPRITE, (150, 150))
        ASSETS['rank_f'] = load_sprite(RANK_F_SPRITE, (150, 150))
        
        # Difficulty bars (will be stretched to fit)
        ASSETS['bar_beginner'] = load_sprite(BAR_BEGINNER_SPRITE)
        ASSETS['bar_easy'] = load_sprite(BAR_EASY_SPRITE)
        ASSETS['bar_normal'] = load_sprite(BAR_NORMAL_SPRITE)
        ASSETS['bar_hard'] = load_sprite(BAR_HARD_SPRITE)
        ASSETS['bar_expert'] = load_sprite(BAR_EXPERT_SPRITE)
        ASSETS['bar_master'] = load_sprite(BAR_MASTER_SPRITE)
        ASSETS['bar_extreme'] = load_sprite(BAR_EXTREME_SPRITE)
        ASSETS['bar_insane'] = load_sprite(BAR_INSANE_SPRITE)
        ASSETS['bar_demon'] = load_sprite(BAR_DEMON_SPRITE)
        ASSETS['bar_god'] = load_sprite(BAR_GOD_SPRITE)
        ASSETS['bar_selected'] = load_sprite(BAR_SELECTED_SPRITE)
        
        # Backgrounds
        ASSETS['song_select_bg'] = load_sprite(SONG_SELECT_BG_SPRITE)
        ASSETS['gameplay_bg'] = load_sprite(GAMEPLAY_BG_SPRITE)
        ASSETS['wood_plank'] = load_sprite(WOOD_PLANK_SPRITE)
        ASSETS['victory_bg'] = load_sprite(VICTORY_BG_SPRITE)
        
        # UI elements
        ASSETS['stats_bg'] = load_sprite(STATS_BG_SPRITE)
    
    return ASSETS

# Colors (Authentic Taiko style - Lighter)
BG_COLOR = (255, 245, 235)  # Very light cream background
TRACK_COLOR = (120, 90, 70)  # Lighter brown track
DON_COLOR = (255, 80, 80)  # Bright red for don (space)
KA_COLOR = (100, 180, 255)  # Bright blue for ka (up arrow)
HIT_CIRCLE_COLOR = (255, 255, 255)  # White hit circle
PERFECT_COLOR = (255, 215, 0)  # Gold
GOOD_COLOR = (100, 255, 100)  # Green
OK_COLOR = (255, 200, 100)  # Orange
MISS_COLOR = (255, 50, 50)  # Red
TEXT_COLOR = (60, 30, 10)  # Dark brown
DRUM_RED = (220, 60, 60)  # Drum red
DRUM_BORDER = (100, 40, 40)  # Dark red border


class Note:
    def __init__(self, note_type, spawn_time, y_pos=360):
        self.type = note_type  # 'don' (space) or 'ka' (up)
        self.spawn_time = spawn_time
        self.x = 1200  # Start from right
        self.y = y_pos  # Will be set to match drum position
        self.size = 70
        self.hit = False
        self.missed = False
        self.pulse = 0  # For animation
        
    def update(self, current_time, scroll_speed):
        # Move from right to left
        time_diff = current_time - self.spawn_time
        self.x = 1200 - (time_diff * scroll_speed)
        
        # Pulse animation
        self.pulse = (math.sin(current_time * 5) + 1) * 0.5
    
    def draw(self, screen):
        if self.hit or self.missed:
            return
        
        # Animated size
        pulse_size = self.size + int(self.pulse * 5)
        
        # Try to use sprite, fallback to drawing
        sprite_key = 'note_don' if self.type == 'don' else 'note_ka'
        if ASSETS and ASSETS.get(sprite_key):
            sprite = ASSETS[sprite_key]
            scaled_sprite = pygame.transform.scale(sprite, (pulse_size, pulse_size))
            sprite_rect = scaled_sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(scaled_sprite, sprite_rect)
        else:
            # Fallback to drawing
            color = DON_COLOR if self.type == 'don' else KA_COLOR
            
            # Outer glow
            for i in range(3):
                alpha_surf = pygame.Surface((pulse_size + 20, pulse_size + 20), pygame.SRCALPHA)
                pygame.draw.circle(alpha_surf, (*color, 50 - i * 15), (pulse_size // 2 + 10, pulse_size // 2 + 10), pulse_size // 2 + 10 - i * 3)
                screen.blit(alpha_surf, (int(self.x) - pulse_size // 2 - 10, int(self.y) - pulse_size // 2 - 10))
            
            # Main circle
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), pulse_size // 2)
            
            # White border
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), pulse_size // 2, 5)
            
            # Inner design for ka notes (rim hit)
            if self.type == 'ka':
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), pulse_size // 3)
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), pulse_size // 3, 3)
            else:
                # Don notes have a simple center dot
                pygame.draw.circle(screen, (255, 200, 200), (int(self.x), int(self.y)), pulse_size // 5)

class RhythmGame:
    def __init__(self, screen, difficulty='Normal', song_stars=3, custom_beatmap=None):
        self.display_screen = screen
        screen_width, screen_height = screen.get_size()
        
        self.width = 1280
        self.height = 720
        self.screen = pygame.Surface((self.width, self.height))
        
        scale_x = screen_width / self.width
        scale_y = screen_height / self.height
        self.scale = min(scale_x, scale_y)
        
        self.offset_x = int((screen_width - self.width * self.scale) // 2)
        self.offset_y = int((screen_height - self.height * self.scale) // 2)
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('segoeui', 48, bold=True)
        self.small_font = pygame.font.SysFont('segoeui', 32)
        
        # Custom beatmap data
        self.custom_beatmap = custom_beatmap
        
        # Difficulty settings - Expanded to 10 levels
        self.difficulty = difficulty
        self.song_stars = song_stars  # Total stars for this song (1-10)
        self.difficulty_settings = {
            'Beginner': {'bpm': 60, 'scroll_speed': 250, 'interval': 1.5, 'complexity': 1},
            'Easy': {'bpm': 90, 'scroll_speed': 300, 'interval': 1.1, 'complexity': 1},
            'Normal': {'bpm': 120, 'scroll_speed': 350, 'interval': 0.8, 'complexity': 2},
            'Hard': {'bpm': 150, 'scroll_speed': 400, 'interval': 0.65, 'complexity': 3},
            'Expert': {'bpm': 180, 'scroll_speed': 450, 'interval': 0.5, 'complexity': 4},
            'Master': {'bpm': 210, 'scroll_speed': 520, 'interval': 0.4, 'complexity': 5},
            'Extreme': {'bpm': 240, 'scroll_speed': 580, 'interval': 0.33, 'complexity': 6},
            'Insane': {'bpm': 270, 'scroll_speed': 650, 'interval': 0.28, 'complexity': 7},
            'Demon': {'bpm': 300, 'scroll_speed': 720, 'interval': 0.24, 'complexity': 8},
            'God': {'bpm': 350, 'scroll_speed': 800, 'interval': 0.2, 'complexity': 9},
        }
        
        settings = self.difficulty_settings[difficulty]
        self.bpm = settings['bpm']
        self.complexity = settings['complexity']
        
        # Game state
        self.notes = []
        self.hits = 0
        self.misses = 0
        self.combo = 0
        self.max_combo = 0
        self.goal = 50
        self.score = 0
        self.stars_earned = 0  # Stars earned this run
        
        # Taiko elements - Bigger and centered
        self.hit_circle_x = 280
        self.hit_circle_y = self.height // 2  # Centered vertically
        self.hit_circle_size = 140  # Bigger drum
        self.scroll_speed = settings['scroll_speed']
        
        # Timing windows (in pixels from hit circle)
        self.perfect_window = 25
        self.good_window = 50
        self.ok_window = 80
        self.miss_window = 120
        
        # Beat system
        self.time = 0
        self.note_spawn_interval = settings['interval']
        self.last_spawn = 0
        
        # Hit feedback
        self.hit_feedback = None
        self.hit_feedback_timer = 0
        self.hit_feedback_scale = 1.0
        
        # Drum animation
        self.drum_hit_timer = 0
        self.drum_hit_type = None
        
        # Combo animation
        self.combo_scale = 1.0
        
        # Background animation
        self.bg_scroll = 0
        
        # Load custom beatmap music if available
        if self.custom_beatmap and 'song_path' in self.custom_beatmap:
            try:
                pygame.mixer.music.load(self.custom_beatmap['song_path'])
                print(f"Loaded custom song: {self.custom_beatmap['song_path']}")
            except Exception as e:
                print(f"Failed to load custom song: {e}")
        
        # Generate note pattern based on difficulty OR load from custom beatmap
        if self.custom_beatmap and 'notes' in self.custom_beatmap:
            self._load_custom_notes()
        else:
            self._generate_notes()

    
    def _generate_notes(self):
        """Generate 50 notes in a rhythmic pattern based on difficulty"""
        current_time = 2.0  # Start after 2 seconds
        
        # Different patterns for different difficulties (1-9)
        if self.complexity == 1:  # Beginner/Easy
            patterns = [
                ['don', 'don', 'don', 'don'],
                ['ka', 'ka', 'ka', 'ka'],
                ['don', 'don', 'ka', 'ka'],
            ]
        elif self.complexity == 2:  # Normal
            patterns = [
                ['don', 'don', 'ka', 'don'],
                ['don', 'ka', 'don', 'ka'],
                ['don', 'don', 'don', 'ka'],
                ['ka', 'ka', 'don', 'don'],
            ]
        elif self.complexity == 3:  # Hard
            patterns = [
                ['don', 'ka', 'don', 'ka', 'don'],
                ['don', 'don', 'ka', 'ka', 'don'],
                ['ka', 'don', 'ka', 'don', 'ka'],
                ['don', 'don', 'don', 'ka', 'ka'],
            ]
        elif self.complexity == 4:  # Expert
            patterns = [
                ['don', 'ka', 'don', 'ka', 'don', 'ka'],
                ['don', 'don', 'ka', 'don', 'ka', 'ka'],
                ['ka', 'ka', 'don', 'don', 'ka', 'don'],
                ['don', 'ka', 'ka', 'don', 'don', 'ka'],
            ]
        elif self.complexity == 5:  # Master
            patterns = [
                ['don', 'ka', 'don', 'ka', 'don', 'ka', 'don'],
                ['don', 'don', 'ka', 'ka', 'don', 'ka', 'don'],
                ['ka', 'don', 'ka', 'don', 'ka', 'don', 'ka'],
                ['don', 'ka', 'ka', 'don', 'don', 'ka', 'ka'],
            ]
        elif self.complexity == 6:  # Extreme
            patterns = [
                ['don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka'],
                ['ka', 'ka', 'don', 'don', 'ka', 'ka', 'don', 'don'],
                ['don', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'ka'],
                ['ka', 'don', 'don', 'ka', 'ka', 'don', 'ka', 'don'],
            ]
        elif self.complexity == 7:  # Insane
            patterns = [
                ['don', 'ka', 'ka', 'don', 'ka', 'don', 'don', 'ka', 'ka'],
                ['ka', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka'],
                ['don', 'don', 'ka', 'ka', 'don', 'don', 'ka', 'ka', 'don'],
                ['ka', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'don', 'ka'],
            ]
        elif self.complexity == 8:  # Demon
            patterns = [
                ['don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka'],
                ['ka', 'don', 'don', 'ka', 'ka', 'don', 'ka', 'don', 'ka', 'don'],
                ['don', 'don', 'ka', 'don', 'ka', 'ka', 'don', 'ka', 'don', 'ka'],
                ['ka', 'ka', 'don', 'ka', 'don', 'don', 'ka', 'don', 'ka', 'ka'],
            ]
        else:  # God (complexity 9)
            patterns = [
                ['don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'don'],
                ['ka', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'don', 'ka'],
                ['don', 'don', 'ka', 'ka', 'don', 'ka', 'don', 'ka', 'ka', 'don', 'don'],
                ['ka', 'ka', 'don', 'ka', 'don', 'don', 'ka', 'don', 'ka', 'ka', 'don'],
                ['don', 'ka', 'ka', 'don', 'don', 'ka', 'don', 'ka', 'don', 'ka', 'ka'],
            ]
        
        pattern_index = 0
        note_in_pattern = 0
        
        for i in range(self.goal):
            current_pattern = patterns[pattern_index]
            note_type = current_pattern[note_in_pattern]
            
            self.notes.append(Note(note_type, current_time, self.hit_circle_y))
            
            note_in_pattern += 1
            if note_in_pattern >= len(current_pattern):
                note_in_pattern = 0
                pattern_index = (pattern_index + 1) % len(patterns)
            
            # Vary timing based on difficulty
            if self.complexity <= 2:
                # Easy/Normal: longer pauses
                if i % 8 == 7:
                    current_time += self.note_spawn_interval * 1.5
                else:
                    current_time += self.note_spawn_interval
            elif self.complexity == 3:
                # Hard: some pauses
                if i % 12 == 11:
                    current_time += self.note_spawn_interval * 1.3
                else:
                    current_time += self.note_spawn_interval
            else:
                # Expert/God: minimal pauses, more consistent
                if i % 16 == 15:
                    current_time += self.note_spawn_interval * 1.2
                else:
                    current_time += self.note_spawn_interval
    
    def _load_custom_notes(self):
            """Load notes from custom beatmap"""
            for note_data in self.custom_beatmap['notes']:
                note_type = note_data['type']
                # Add 2 second offset like generated notes
                spawn_time = note_data['time'] + 2.0 
                self.notes.append(Note(note_type, spawn_time, self.hit_circle_y))
            
            # --- FIX: Ensure notes are strictly sorted by spawn time ---
            # This fixes issues where the notes array in the JSON might not be
            # perfectly chronological, which can break game logic.
            self.notes.sort(key=lambda note: note.spawn_time)
            # -----------------------------------------------------------
            
            # Update goal to match number of notes
            self.goal = len(self.notes)
            print(f"Loaded {self.goal} notes from custom beatmap")

    def _check_hit(self, note_type):
        """Check if player hit a note"""
        # Find the closest note of the correct type near the hit circle
        closest_note = None
        closest_dist = float('inf')
        
        for note in self.notes:
            if note.type == note_type and not note.hit and not note.missed:
                dist = abs(note.x - self.hit_circle_x)
                if dist < self.miss_window and dist < closest_dist:
                    closest_dist = dist
                    closest_note = note
        
        if closest_note:
            closest_note.hit = True
            self.hits += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            
            # Drum hit animation
            self.drum_hit_timer = 15
            self.drum_hit_type = note_type
            
            # Combo animation
            self.combo_scale = 1.5
            
            # Determine hit quality and score
            if closest_dist < self.perfect_window:
                self.hit_feedback = 'Perfect!'
                self.hit_feedback_timer = 35
                self.hit_feedback_scale = 1.5
                self.score += 300
            elif closest_dist < self.good_window:
                self.hit_feedback = 'Good!'
                self.hit_feedback_timer = 30
                self.hit_feedback_scale = 1.3
                self.score += 200
            elif closest_dist < self.ok_window:
                self.hit_feedback = 'OK'
                self.hit_feedback_timer = 25
                self.hit_feedback_scale = 1.1
                self.score += 100
            else:
                self.hit_feedback = 'OK'
                self.hit_feedback_timer = 20
                self.hit_feedback_scale = 1.0
                self.score += 50
            
            return True
        else:
            # Mistimed input - no note nearby
            # Break combo and subtract score
            if self.combo > 0:
                self.combo = 0
                self.combo_scale = 1.0
                self.score = max(0, self.score - 100)  # Subtract 100 points
                
                # Show miss feedback
                self.hit_feedback = 'Miss!'
                self.hit_feedback_timer = 25
                self.hit_feedback_scale = 1.2
                
                # Drum hit animation (but with wrong color)
                self.drum_hit_timer = 10
                self.drum_hit_type = 'miss'
        
        return False
    
    def run(self):
        running = True
        
        # Start custom song if available
        if self.custom_beatmap and 'song_path' in self.custom_beatmap:
            try:
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Failed to play custom song: {e}")
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.time += dt
            
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
                    
                    # Space for don (red notes - center hit)
                    if event.key == pygame.K_SPACE:
                        self._check_hit('don')
                    
                    # Up arrow for ka (blue notes - rim hit)
                    if event.key == pygame.K_UP:
                        self._check_hit('ka')
            
            # Update animations
            if self.hit_feedback_timer > 0:
                self.hit_feedback_timer -= 1
                self.hit_feedback_scale = max(1.0, self.hit_feedback_scale - 0.02)
            
            if self.drum_hit_timer > 0:
                self.drum_hit_timer -= 1
            
            if self.combo_scale > 1.0:
                self.combo_scale -= 0.03
            
            # Background scroll
            self.bg_scroll += dt * 20
            if self.bg_scroll > 100:
                self.bg_scroll = 0
            
            # Update notes
            for note in self.notes:
                note.update(self.time, self.scroll_speed)
                
                # Check if note was missed
                if not note.hit and not note.missed and note.x < self.hit_circle_x - self.miss_window:
                    note.missed = True
                    self.misses += 1
                    self.combo = 0
                    self.combo_scale = 1.0
            
            # Check win condition
            if self.hits + self.misses >= self.goal:
                return self._show_victory()
            
            # Draw (Authentic Taiko style)
            self._draw_background()
            
            # Draw track (note lane)
            self._draw_track()
            
            # Draw hit circle (left side) - BEFORE notes so notes appear on top
            self._draw_hit_circle()
            
            # Draw notes - AFTER drum so they appear on top
            for note in self.notes:
                note.draw(self.screen)
            
            # Draw hit feedback with animation
            if self.hit_feedback_timer > 0:
                feedback_font = pygame.font.SysFont('segoeui', int(72 * self.hit_feedback_scale), bold=True)
                
                if 'Perfect' in self.hit_feedback:
                    color = PERFECT_COLOR
                    outline_color = (200, 150, 0)
                elif 'Good' in self.hit_feedback:
                    color = GOOD_COLOR
                    outline_color = (50, 200, 50)
                elif 'Miss' in self.hit_feedback:
                    color = MISS_COLOR
                    outline_color = (150, 0, 0)
                else:
                    color = OK_COLOR
                    outline_color = (200, 150, 50)
                
                # Draw outline
                for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                    outline_text = feedback_font.render(self.hit_feedback, True, outline_color)
                    outline_rect = outline_text.get_rect(center=(self.width // 2 + dx, 150 + dy))
                    self.screen.blit(outline_text, outline_rect)
                
                # Draw main text
                feedback_text = feedback_font.render(self.hit_feedback, True, color)
                feedback_rect = feedback_text.get_rect(center=(self.width // 2, 150))
                self.screen.blit(feedback_text, feedback_rect)
            
            # Draw UI (score, combo, etc.)
            self._draw_ui()
            
            # Scale and display
            self.display_screen.fill((0, 0, 0))
            scaled_surface = pygame.transform.scale(self.screen, (int(self.width * self.scale), int(self.height * self.scale)))
            self.display_screen.blit(scaled_surface, (self.offset_x, self.offset_y))
            pygame.display.flip()
        
        return 'menu'

    def _draw_background(self):
        """Draw animated background"""
        # Try to use gameplay background sprite
        if ASSETS and ASSETS.get('gameplay_bg'):
            gameplay_bg = pygame.transform.scale(ASSETS['gameplay_bg'], (self.width, self.height))
            self.screen.blit(gameplay_bg, (0, 0))
        else:
            # Fallback to drawn background
            self.screen.fill(BG_COLOR)
            
            # Animated wave pattern
            for i in range(0, self.width + 100, 100):
                x = i - self.bg_scroll
                wave_y = 100 + math.sin((x + self.time * 50) * 0.01) * 30
                pygame.draw.circle(self.screen, (255, 220, 180), (int(x), int(wave_y)), 40, 3)
                
                wave_y2 = self.height - 100 + math.cos((x + self.time * 50) * 0.01) * 30
                pygame.draw.circle(self.screen, (255, 220, 180), (int(x), int(wave_y2)), 40, 3)
    
    def _draw_track(self):
        """Draw the note track - Lighter and bigger"""
        track_y = self.hit_circle_y
        track_height = 200  # Bigger track
        
        # Try to use wood plank sprite
        if ASSETS and ASSETS.get('wood_plank'):
            wood_plank = pygame.transform.scale(ASSETS['wood_plank'], (self.width, track_height))
            self.screen.blit(wood_plank, (0, track_y - track_height // 2))
        else:
            # Fallback to drawn track
            # Main track (lighter color)
            pygame.draw.rect(self.screen, TRACK_COLOR, (0, track_y - track_height // 2, self.width, track_height))
            
            # Track borders (lighter)
            pygame.draw.rect(self.screen, (90, 70, 50), (0, track_y - track_height // 2, self.width, track_height), 6)
            
            # Center line (lighter)
            pygame.draw.line(self.screen, (150, 120, 90), (0, track_y), (self.width, track_y), 4)
            
            # Decorative lines (lighter)
            pygame.draw.line(self.screen, (140, 110, 80), (0, track_y - 70), (self.width, track_y - 70), 2)
            pygame.draw.line(self.screen, (140, 110, 80), (0, track_y + 70), (self.width, track_y + 70), 2)
    
    def _draw_hit_circle(self):
        """Draw the hit circle (Taiko drum) with animation"""
        # Hit animation
        hit_scale = 1.0
        if self.drum_hit_timer > 0:
            hit_scale = 1.0 + (self.drum_hit_timer / 15.0) * 0.2
        
        size = int(self.hit_circle_size * hit_scale)
        
        # Try to use drum sprite, fallback to drawing
        if ASSETS and ASSETS.get('drum'):
            drum_sprite = ASSETS['drum']
            scaled_drum = pygame.transform.scale(drum_sprite, (size * 2, size * 2))
            
            # Apply color tint for hit effects
            if self.drum_hit_timer > 0:
                tinted_drum = scaled_drum.copy()
                if self.drum_hit_type == 'don':
                    tinted_drum.fill((255, 100, 100, 100), special_flags=pygame.BLEND_RGBA_ADD)
                elif self.drum_hit_type == 'ka':
                    tinted_drum.fill((100, 150, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
                elif self.drum_hit_type == 'miss':
                    tinted_drum.fill((50, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)
                drum_rect = tinted_drum.get_rect(center=(self.hit_circle_x, self.hit_circle_y))
                self.screen.blit(tinted_drum, drum_rect)
            else:
                drum_rect = scaled_drum.get_rect(center=(self.hit_circle_x, self.hit_circle_y))
                self.screen.blit(scaled_drum, drum_rect)
        else:
            # Fallback to drawing
            # Outer drum ring (wood)
            pygame.draw.circle(self.screen, (139, 90, 60), (self.hit_circle_x, self.hit_circle_y), size + 15)
            pygame.draw.circle(self.screen, (100, 60, 40), (self.hit_circle_x, self.hit_circle_y), size + 15, 6)
            
            # Main drum face
            if self.drum_hit_timer > 0 and self.drum_hit_type == 'don':
                pygame.draw.circle(self.screen, (255, 120, 120), (self.hit_circle_x, self.hit_circle_y), size)
            elif self.drum_hit_timer > 0 and self.drum_hit_type == 'ka':
                pygame.draw.circle(self.screen, (150, 200, 255), (self.hit_circle_x, self.hit_circle_y), size)
            elif self.drum_hit_timer > 0 and self.drum_hit_type == 'miss':
                pygame.draw.circle(self.screen, (100, 100, 100), (self.hit_circle_x, self.hit_circle_y), size)
            else:
                pygame.draw.circle(self.screen, DRUM_RED, (self.hit_circle_x, self.hit_circle_y), size)
            
            # Drum border
            pygame.draw.circle(self.screen, DRUM_BORDER, (self.hit_circle_x, self.hit_circle_y), size, 8)
            
            # Inner white circle
            pygame.draw.circle(self.screen, HIT_CIRCLE_COLOR, (self.hit_circle_x, self.hit_circle_y), size - 25)
            pygame.draw.circle(self.screen, (220, 220, 220), (self.hit_circle_x, self.hit_circle_y), size - 25, 5)
            
            # Center target
            pygame.draw.circle(self.screen, DRUM_RED, (self.hit_circle_x, self.hit_circle_y), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (self.hit_circle_x, self.hit_circle_y), 20, 3)
            pygame.draw.circle(self.screen, DRUM_RED, (self.hit_circle_x, self.hit_circle_y), 8)
    
    def _draw_ui(self):
        """Draw UI elements (Taiko style)"""
        # Top bar background
        if ASSETS and ASSETS.get('stats_bg'):
            stats_bg = pygame.transform.scale(ASSETS['stats_bg'], (self.width, 120))
            self.screen.blit(stats_bg, (0, 0))
        else:
            pygame.draw.rect(self.screen, (200, 150, 100), (0, 0, self.width, 120))
            pygame.draw.rect(self.screen, (150, 100, 70), (0, 0, self.width, 120), 4)
        
        # Difficulty indicator (top left)
        diff_colors = {
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
        diff_color = diff_colors.get(self.difficulty, TEXT_COLOR)
        diff_text = self.small_font.render(f'{self.difficulty} - {self.bpm} BPM', True, diff_color)
        self.screen.blit(diff_text, (30, 20))
        
        # Score (below difficulty)
        score_text = self.font.render(f'Score: {self.score}', True, TEXT_COLOR)
        self.screen.blit(score_text, (30, 60))
        
        # Combo (top center) with animation
        if self.combo > 0:
            combo_font = pygame.font.SysFont('segoeui', int(56 * self.combo_scale), bold=True)
            combo_text = combo_font.render(f'{self.combo} COMBO!', True, PERFECT_COLOR)
            combo_rect = combo_text.get_rect(center=(self.width // 2, 60))
            
            # Outline
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline = combo_font.render(f'{self.combo} COMBO!', True, (200, 150, 0))
                outline_rect = outline.get_rect(center=(self.width // 2 + dx, 60 + dy))
                self.screen.blit(outline, outline_rect)
            
            self.screen.blit(combo_text, combo_rect)
        
        # Streak counter (top right) - replaces progress
        streak_text = self.font.render(f'Streak: {self.combo}', True, TEXT_COLOR)
        streak_rect = streak_text.get_rect(topright=(self.width - 30, 20))
        self.screen.blit(streak_text, streak_rect)
        
        # Accuracy with Rank
        total = self.hits + self.misses
        if total > 0:
            accuracy = (self.hits / total) * 100
            rank, rank_color = self._get_rank(accuracy)
            
            # Accuracy text
            acc_text = self.small_font.render(f'Accuracy: {accuracy:.1f}%', True, TEXT_COLOR)
            acc_rect = acc_text.get_rect(topright=(self.width - 30, 65))
            self.screen.blit(acc_text, acc_rect)
            
            # Rank next to accuracy
            rank_font = pygame.font.SysFont('segoeui', 36, bold=True)
            rank_text = rank_font.render(rank, True, rank_color)
            rank_rect = rank_text.get_rect(topright=(self.width - 30, 90))
            self.screen.blit(rank_text, rank_rect)
        

    
    def _get_rank(self, accuracy):
        """Calculate rank based on accuracy (F to S+)"""
        if accuracy >= 99.0:
            return 'S+', (255, 215, 0)  # Gold
        elif accuracy >= 95.0:
            return 'S', (255, 215, 0)  # Gold
        elif accuracy >= 90.0:
            return 'A', (100, 255, 100)  # Green
        elif accuracy >= 80.0:
            return 'B', (100, 200, 255)  # Blue
        elif accuracy >= 70.0:
            return 'C', (255, 200, 100)  # Orange
        elif accuracy >= 60.0:
            return 'D', (255, 150, 100)  # Light red
        else:
            return 'F', (255, 50, 50)  # Red
    
    def _calculate_stars_earned(self, accuracy):
        """Calculate stars earned based on accuracy"""
        if accuracy >= 99.0:
            return 5  # S+
        elif accuracy >= 95.0:
            return 5  # S
        elif accuracy >= 90.0:
            return 4  # A
        elif accuracy >= 80.0:
            return 3  # B
        elif accuracy >= 70.0:
            return 2  # C
        elif accuracy >= 60.0:
            return 1  # D
        else:
            return 0  # F
    
    def _show_victory(self):
        """Show victory screen with ranking (osu! style)"""
        victory_font = pygame.font.SysFont('segoeui', 80, bold=True)
        rank_font = pygame.font.SysFont('segoeui', 150, bold=True)
        
        # Calculate final stats
        total = self.hits + self.misses
        accuracy = (self.hits / total) * 100 if total > 0 else 0
        rank, rank_color = self._get_rank(accuracy)
        self.stars_earned = self._calculate_stars_earned(accuracy)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        return 'menu'
            
            # Victory background
            if ASSETS and ASSETS.get('victory_bg'):
                victory_bg = pygame.transform.scale(ASSETS['victory_bg'], (self.width, self.height))
                self.screen.blit(victory_bg, (0, 0))
            else:
                self._draw_background()
            
            # Victory banner
            banner_rect = pygame.Rect(0, self.height // 2 - 200, self.width, 400)
            if ASSETS and ASSETS.get('stats_bg'):
                stats_bg = pygame.transform.scale(ASSETS['stats_bg'], (self.width, 400))
                self.screen.blit(stats_bg, (0, self.height // 2 - 200))
            else:
                pygame.draw.rect(self.screen, (255, 220, 180), banner_rect)
                pygame.draw.rect(self.screen, (200, 150, 100), banner_rect, 8)
            
            # Rank (large, centered) - Shifted up
            rank_y = self.height // 2 - 130
            rank_sprite_key = f'rank_{rank.lower().replace("+", "_plus")}'
            if ASSETS and ASSETS.get(rank_sprite_key):
                rank_sprite = ASSETS[rank_sprite_key]
                rank_rect = rank_sprite.get_rect(center=(self.width // 2, rank_y))
                self.screen.blit(rank_sprite, rank_rect)
            else:
                # Fallback to text
                rank_text = rank_font.render(rank, True, rank_color)
                rank_rect = rank_text.get_rect(center=(self.width // 2, rank_y))
                
                # Outline for rank
                for dx, dy in [(-4, -4), (-4, 4), (4, -4), (4, 4)]:
                    outline = rank_font.render(rank, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, rank_y + dy))
                    self.screen.blit(outline, outline_rect)
                
                self.screen.blit(rank_text, rank_rect)
            
            # Stats - Shifted up and tighter spacing
            stats = [
                f'Score: {self.score}',
                f'Accuracy: {accuracy:.1f}%',
                f'Max Combo: {self.max_combo}',
            ]
            
            y = self.height // 2 - 30  # Start higher
            for stat in stats:
                stat_text = self.font.render(stat, True, TEXT_COLOR)
                stat_rect = stat_text.get_rect(center=(self.width // 2, y))
                self.screen.blit(stat_text, stat_rect)
                y += 50  # Tighter spacing
            
            # Stars earned - Show based on song's star rating (1-10)
            # Align stars on the bottom edge of the banner
            banner_bottom = self.height // 2 + 200
            stars_y = banner_bottom - 30  # Shifted up more from bottom edge
            star_size = 40
            star_spacing = 45
            total_stars = self.song_stars  # Use song's star rating
            start_x = self.width // 2 - (total_stars * star_spacing) // 2
            
            for i in range(total_stars):
                star_x = start_x + i * star_spacing
                
                # Try to use star sprites
                if i < self.stars_earned:
                    # Earned star
                    if ASSETS and ASSETS.get('star'):
                        star_sprite = ASSETS['star']
                        star_rect = star_sprite.get_rect(center=(star_x, stars_y))
                        self.screen.blit(star_sprite, star_rect)
                    else:
                        # Fallback to drawing filled star
                        star_points = []
                        for j in range(10):
                            angle = (j * 36 - 90) * math.pi / 180
                            radius = 20 if j % 2 == 0 else 8
                            px = star_x + radius * math.cos(angle)
                            py = stars_y + radius * math.sin(angle)
                            star_points.append((px, py))
                        pygame.draw.polygon(self.screen, (255, 215, 0), star_points)
                        pygame.draw.polygon(self.screen, (200, 150, 0), star_points, 2)
                else:
                    # Unearned star
                    if ASSETS and ASSETS.get('empty_star'):
                        empty_star_sprite = ASSETS['empty_star']
                        star_rect = empty_star_sprite.get_rect(center=(star_x, stars_y))
                        self.screen.blit(empty_star_sprite, star_rect)
                    else:
                        # Fallback to drawing outline star
                        star_points = []
                        for j in range(10):
                            angle = (j * 36 - 90) * math.pi / 180
                            radius = 20 if j % 2 == 0 else 8
                            px = star_x + radius * math.cos(angle)
                            py = stars_y + radius * math.sin(angle)
                            star_points.append((px, py))
                        pygame.draw.polygon(self.screen, (150, 150, 150), star_points, 3)
            
            # Scale and display
            self.display_screen.fill((0, 0, 0))
            scaled_surface = pygame.transform.scale(self.screen, (int(self.width * self.scale), int(self.height * self.scale)))
            self.display_screen.blit(scaled_surface, (self.offset_x, self.offset_y))
            pygame.display.flip()
            self.clock.tick(60)

def _show_song_select(screen, total_stars=0):
    """Show song selection screen (osu! style)"""
    width = 1280
    height = 720
    surface = pygame.Surface((width, height))
    
    screen_width, screen_height = screen.get_size()
    scale_x = screen_width / width
    scale_y = screen_height / height
    scale = min(scale_x, scale_y)
    
    offset_x = int((screen_width - width * scale) // 2)
    offset_y = int((screen_height - height * scale) // 2)
    
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont('segoeui', 48, bold=True)
    song_font = pygame.font.SysFont('segoeui', 36, bold=True)
    artist_font = pygame.font.SysFont('segoeui', 24)
    diff_font = pygame.font.SysFont('segoeui', 20, bold=True)
    stars_counter_font = pygame.font.SysFont('segoeui', 32, bold=True)
    
    # Song list with difficulties (default songs)
    songs = [
        {
            'name': 'Beginner Beat',
            'artist': 'Taiko Master',
            'difficulty': 'Beginner',
            'bpm': 60,
            'stars': 1,
            'color': (150, 255, 150),
            'custom': False
        },
        {
            'name': 'Easy Rhythm',
            'artist': 'Drum Hero',
            'difficulty': 'Easy',
            'bpm': 90,
            'stars': 2,
            'color': (100, 255, 100),
            'custom': False
        },
        {
            'name': 'Normal Flow',
            'artist': 'Beat Maker',
            'difficulty': 'Normal',
            'bpm': 120,
            'stars': 3,
            'color': (100, 200, 255),
            'custom': False
        },
        {
            'name': 'Hard Strike',
            'artist': 'Rhythm King',
            'difficulty': 'Hard',
            'bpm': 150,
            'stars': 4,
            'color': (255, 200, 100),
            'custom': False
        },
        {
            'name': 'Expert Combo',
            'artist': 'Pro Drummer',
            'difficulty': 'Expert',
            'bpm': 180,
            'stars': 5,
            'color': (255, 150, 100),
            'custom': False
        },
        {
            'name': 'Master Blitz',
            'artist': 'Elite Player',
            'difficulty': 'Master',
            'bpm': 210,
            'stars': 6,
            'color': (255, 100, 100),
            'custom': False
        },
        {
            'name': 'Extreme Rush',
            'artist': 'Speed Demon',
            'difficulty': 'Extreme',
            'bpm': 240,
            'stars': 7,
            'color': (255, 50, 150),
            'custom': False
        },
        {
            'name': 'Insane Chaos',
            'artist': 'Mad Drummer',
            'difficulty': 'Insane',
            'bpm': 270,
            'stars': 8,
            'color': (200, 50, 255),
            'custom': False
        },
        {
            'name': 'Demon Storm',
            'artist': 'Dark Master',
            'difficulty': 'Demon',
            'bpm': 300,
            'stars': 9,
            'color': (150, 0, 200),
            'custom': False
        },
        {
            'name': 'God Mode',
            'artist': 'Divine Rhythm',
            'difficulty': 'God',
            'bpm': 350,
            'stars': 10,
            'color': (255, 215, 0),
            'custom': False
        },
    ]
    
    # Load custom beatmaps if available
    if beatmap_loader:
        try:
            custom_beatmaps = beatmap_loader.scan_beatmaps()
            for beatmap in custom_beatmaps:
                songs.append({
                    'name': beatmap['name'],
                    'artist': beatmap['artist'],
                    'difficulty': beatmap['difficulty'],
                    'bpm': beatmap['bpm'],
                    'stars': beatmap['stars'],
                    'color': beatmap['color'],
                    'custom': True,
                    'beatmap_data': beatmap  # Store full beatmap data
                })
            if custom_beatmaps:
                print(f"Loaded {len(custom_beatmaps)} custom beatmap(s)")
        except Exception as e:
            print(f"Failed to load custom beatmaps: {e}")
    
    selected = 2  # Default to Normal
    bg_scroll = 0
    scroll_offset = 0  # For scrolling menu
    target_scroll = 0
    
    while True:
        dt = clock.tick(60) / 1000.0
        bg_scroll += dt * 20
        if bg_scroll > 100:
            bg_scroll = 0
        
        # Smooth scroll animation
        scroll_offset += (target_scroll - scroll_offset) * 0.15
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(songs)
                    # Update scroll to keep selected item visible (show 8 at a time)
                    if selected < 3:
                        target_scroll = 0
                    elif selected >= len(songs) - 3:
                        target_scroll = max(0, len(songs) - 8)
                    else:
                        target_scroll = selected - 3
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(songs)
                    # Update scroll to keep selected item visible (show 8 at a time)
                    if selected < 3:
                        target_scroll = 0
                    elif selected >= len(songs) - 3:
                        target_scroll = max(0, len(songs) - 8)
                    else:
                        target_scroll = selected - 3
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # If it's a custom map, return the full beatmap dict
                    if songs[selected].get('custom'):
                        return songs[selected]['beatmap_data']
                    else:
                        # Otherwise return None and treat it as a default (non-map) song
                        return None

        
        # Draw background
        if ASSETS and ASSETS.get('song_select_bg'):
            song_select_bg = pygame.transform.scale(ASSETS['song_select_bg'], (width, height))
            surface.blit(song_select_bg, (0, 0))
        else:
            # Fallback to dark osu! style
            surface.fill((30, 30, 40))
            
            # Decorative triangles (osu! style)
            for i in range(5):
                tri_x = random.randint(0, width)
                tri_y = random.randint(0, height)
                tri_size = random.randint(50, 150)
                tri_alpha = 20
                tri_surf = pygame.Surface((tri_size, tri_size), pygame.SRCALPHA)
                pygame.draw.polygon(tri_surf, (100, 100, 150, tri_alpha), 
                                  [(0, tri_size), (tri_size // 2, 0), (tri_size, tri_size)])
                surface.blit(tri_surf, (tri_x, tri_y))
        
        # Title (top left, osu! style)
        title_text = title_font.render('SONG SELECT', True, (255, 255, 255))
        title_rect = title_text.get_rect(topleft=(30, 20))
        surface.blit(title_text, title_rect)
        
        # Total stars counter (top right)
        max_stars = 50  # 10 songs × 5 stars each
        stars_text = stars_counter_font.render(f'Stars: {total_stars}/{max_stars}', True, (255, 215, 0))
        stars_rect = stars_text.get_rect(topright=(width - 30, 25))
        surface.blit(stars_text, stars_rect)
        
        # Draw star icon next to counter
        star_x = width - 30 - stars_rect.width - 50
        star_y = 35
        star_size = 20
        star_points = []
        for j in range(10):
            angle = (j * 36 - 90) * math.pi / 180
            radius = star_size if j % 2 == 0 else star_size * 0.4
            px = star_x + radius * math.cos(angle)
            py = star_y + radius * math.sin(angle)
            star_points.append((px, py))
        pygame.draw.polygon(surface, (255, 215, 0), star_points)
        pygame.draw.polygon(surface, (200, 150, 0), star_points, 2)
        
        # Total stars counter (top right)
        max_stars = sum(song['stars'] for song in songs)  # 50 total
        stars_text = stars_counter_font.render(f'Stars: {total_stars}/{max_stars}', True, (255, 215, 0))
        stars_rect = stars_text.get_rect(topright=(width - 30, 25))
        surface.blit(stars_text, stars_rect)
        
        # Draw star icon next to counter
        star_size = 20
        star_x = stars_rect.left - 30
        star_y = 35
        star_points = []
        for j in range(10):
            angle = (j * 36 - 90) * math.pi / 180
            radius = star_size if j % 2 == 0 else star_size * 0.4
            px = star_x + radius * math.cos(angle)
            py = star_y + radius * math.sin(angle)
            star_points.append((px, py))
        pygame.draw.polygon(surface, (255, 215, 0), star_points)
        pygame.draw.polygon(surface, (200, 150, 0), star_points, 2)
        
        # Song list (RIGHT SIDE, osu! style vertical bars)
        list_x = 450  # Start from middle-right
        list_width = width - list_x - 20
        bar_height = 70
        
        # Only show 8 songs at a time
        visible_start = int(scroll_offset)
        visible_end = min(visible_start + 8, len(songs))
        
        for idx in range(visible_start, visible_end):
            song = songs[idx]
            is_selected = (idx == selected)
            
            # Calculate position
            visible_idx = idx - visible_start
            y = 80 + visible_idx * bar_height
            
            # Bar background (osu! style colored bars)
            if is_selected:
                # Selected - full width, bright
                bar_rect = pygame.Rect(list_x - 30, y, list_width + 30, bar_height - 5)
                bar_color = song['color']
                text_color = (255, 255, 255)
                # Animated pulse
                pulse = math.sin(pygame.time.get_ticks() * 0.005) * 2
                bar_rect.x += int(pulse)
                
                # Try to use selected bar sprite
                if ASSETS and ASSETS.get('bar_selected'):
                    bar_sprite = pygame.transform.scale(ASSETS['bar_selected'], (bar_rect.width, bar_rect.height))
                    surface.blit(bar_sprite, bar_rect)
                else:
                    pygame.draw.rect(surface, bar_color, bar_rect)
                    border_rect = pygame.Rect(bar_rect.x, bar_rect.y, 5, bar_rect.height)
                    pygame.draw.rect(surface, (255, 255, 255), border_rect)
            else:
                # Not selected - shorter, darker
                bar_rect = pygame.Rect(list_x, y, list_width, bar_height - 5)
                bar_color = tuple(int(c * 0.6) for c in song['color'])
                text_color = (180, 180, 180)
                
                # Try to use difficulty-specific bar sprite
                diff_lower = song['difficulty'].lower()
                bar_key = f'bar_{diff_lower}'
                if ASSETS and ASSETS.get(bar_key):
                    bar_sprite = pygame.transform.scale(ASSETS[bar_key], (bar_rect.width, bar_rect.height))
                    surface.blit(bar_sprite, bar_rect)
                else:
                    pygame.draw.rect(surface, bar_color, bar_rect)
                    border_rect = pygame.Rect(bar_rect.x, bar_rect.y, 5, bar_rect.height)
                    pygame.draw.rect(surface, (255, 255, 255), border_rect)
            
            # Song name (bold, left aligned)
            name_font = pygame.font.SysFont('segoeui', 28, bold=True)
            name_text = name_font.render(song['name'], True, text_color)
            name_rect = name_text.get_rect(midleft=(bar_rect.x + 15, y + 20))
            surface.blit(name_text, name_rect)
            
            # Artist name (smaller, below song name)
            artist_small_font = pygame.font.SysFont('segoeui', 18)
            artist_text = artist_small_font.render(song['artist'], True, text_color)
            artist_rect = artist_text.get_rect(midleft=(bar_rect.x + 15, y + 45))
            surface.blit(artist_text, artist_rect)
            
            # Stars (right side) - Draw custom star shape
            if is_selected:
                star_x = bar_rect.right - 50
                star_y = y + 32
                star_size = 12
                
                # Draw star shape
                star_points = []
                for i in range(10):
                    angle = (i * 36 - 90) * math.pi / 180
                    radius = star_size if i % 2 == 0 else star_size * 0.4
                    px = star_x + radius * math.cos(angle)
                    py = star_y + radius * math.sin(angle)
                    star_points.append((px, py))
                
                pygame.draw.polygon(surface, (255, 215, 0), star_points)
                pygame.draw.polygon(surface, (200, 150, 0), star_points, 2)
                
                # Number
                stars_font = pygame.font.SysFont('segoeui', 24, bold=True)
                stars_text = stars_font.render(f"{song['stars']}", True, (255, 215, 0))
                stars_rect = stars_text.get_rect(midleft=(star_x + 20, y + 32))
                surface.blit(stars_text, stars_rect)
        
        # Selected song large display (LEFT SIDE)
        if 0 <= selected < len(songs):
            selected_song = songs[selected]
            
            # Large circular cover art (osu! style)
            circle_x = 220
            circle_y = 360
            circle_radius = 180
            
            # Try to use cover art sprite
            cover_key = f'cover_{selected + 1}'
            if ASSETS and ASSETS.get(cover_key):
                cover_sprite = ASSETS[cover_key]
                # Create circular mask
                circle_surf = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surf, (255, 255, 255), (circle_radius, circle_radius), circle_radius)
                
                # Scale and mask cover art
                scaled_cover = pygame.transform.scale(cover_sprite, (circle_radius * 2, circle_radius * 2))
                circle_surf.blit(scaled_cover, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                
                cover_rect = circle_surf.get_rect(center=(circle_x, circle_y))
                surface.blit(circle_surf, cover_rect)
            else:
                # Fallback to gradient circle
                for r in range(circle_radius, 0, -2):
                    progress = 1 - (r / circle_radius)
                    color = tuple(int(c * (0.4 + progress * 0.6)) for c in selected_song['color'])
                    pygame.draw.circle(surface, color, (circle_x, circle_y), r)
            
            # White border
            pygame.draw.circle(surface, (255, 255, 255), (circle_x, circle_y), circle_radius, 6)
            pygame.draw.circle(surface, (200, 200, 200), (circle_x, circle_y), circle_radius - 10, 3)
            
            # Song name in center of circle
            circle_font = pygame.font.SysFont('segoeui', 36, bold=True)
            # Split long names
            name_words = selected_song['name'].split()
            if len(name_words) > 2:
                line1 = ' '.join(name_words[:2])
                line2 = ' '.join(name_words[2:])
                name1_text = circle_font.render(line1, True, (255, 255, 255))
                name2_text = circle_font.render(line2, True, (255, 255, 255))
                name1_rect = name1_text.get_rect(center=(circle_x, circle_y - 15))
                name2_rect = name2_text.get_rect(center=(circle_x, circle_y + 15))
                surface.blit(name1_text, name1_rect)
                surface.blit(name2_text, name2_rect)
            else:
                name_text = circle_font.render(selected_song['name'], True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(circle_x, circle_y))
                surface.blit(name_text, name_rect)
            
            # Info below circle
            info_y = circle_y + circle_radius + 40
            
            # Artist
            artist_large_font = pygame.font.SysFont('segoeui', 24)
            artist_large_text = artist_large_font.render(selected_song['artist'], True, (200, 200, 200))
            artist_large_rect = artist_large_text.get_rect(center=(circle_x, info_y))
            surface.blit(artist_large_text, artist_large_rect)
            
            # Difficulty
            diff_large_font = pygame.font.SysFont('segoeui', 28, bold=True)
            diff_large_text = diff_large_font.render(f"{selected_song['difficulty']} - {selected_song['bpm']} BPM", True, selected_song['color'])
            diff_large_rect = diff_large_text.get_rect(center=(circle_x, info_y + 35))
            surface.blit(diff_large_text, diff_large_rect)
        
        # Scale and display
        screen.fill((0, 0, 0))
        scaled_surface = pygame.transform.scale(surface, (int(width * scale), int(height * scale)))
        screen.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()


def _show_main_menu(screen):
    """Show main menu before difficulty selection"""
    width = 1280
    height = 720
    surface = pygame.Surface((width, height))
    
    screen_width, screen_height = screen.get_size()
    scale_x = screen_width / width
    scale_y = screen_height / height
    scale = min(scale_x, scale_y)
    
    offset_x = int((screen_width - width * scale) // 2)
    offset_y = int((screen_height - height * scale) // 2)
    
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont('segoeui', 96, bold=True)
    subtitle_font = pygame.font.SysFont('segoeui', 48, bold=True)
    button_font = pygame.font.SysFont('segoeui', 42, bold=True)
    
    bg_scroll = 0
    pulse_time = 0
    
    while True:
        dt = clock.tick(60) / 1000.0
        bg_scroll += dt * 20
        if bg_scroll > 100:
            bg_scroll = 0
        
        pulse_time += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return True
        
        # Draw background
        surface.fill(BG_COLOR)
        
        # Animated wave pattern
        for i in range(0, width + 100, 100):
            x = i - bg_scroll
            wave_y = 100 + math.sin((x + bg_scroll * 2.5) * 0.01) * 30
            pygame.draw.circle(surface, (255, 220, 180), (int(x), int(wave_y)), 40, 3)
            
            wave_y2 = height - 100 + math.cos((x + bg_scroll * 2.5) * 0.01) * 30
            pygame.draw.circle(surface, (255, 220, 180), (int(x), int(wave_y2)), 40, 3)
        
        # Title
        title_text = title_font.render('TAIKO RHYTHM', True, PERFECT_COLOR)
        title_rect = title_text.get_rect(center=(width // 2, 180))
        
        # Outline
        for dx, dy in [(-4, -4), (-4, 4), (4, -4), (4, 4)]:
            outline = title_font.render('TAIKO RHYTHM', True, (200, 150, 0))
            outline_rect = outline.get_rect(center=(width // 2 + dx, 180 + dy))
            surface.blit(outline, outline_rect)
        
        surface.blit(title_text, title_rect)
        
        # Animated drum visual (scaled down)
        drum_y = 360
        drum_size = 100
        
        # Outer drum ring
        pygame.draw.circle(surface, (139, 90, 60), (width // 2, drum_y), drum_size + 15)
        pygame.draw.circle(surface, (100, 60, 40), (width // 2, drum_y), drum_size + 15, 6)
        
        # Main drum face
        pygame.draw.circle(surface, DRUM_RED, (width // 2, drum_y), drum_size)
        pygame.draw.circle(surface, DRUM_BORDER, (width // 2, drum_y), drum_size, 8)
        
        # Inner white circle
        pygame.draw.circle(surface, HIT_CIRCLE_COLOR, (width // 2, drum_y), drum_size - 25)
        pygame.draw.circle(surface, (220, 220, 220), (width // 2, drum_y), drum_size - 25, 5)
        
        # Center target
        pygame.draw.circle(surface, DRUM_RED, (width // 2, drum_y), 20)
        pygame.draw.circle(surface, (255, 255, 255), (width // 2, drum_y), 20, 3)
        pygame.draw.circle(surface, DRUM_RED, (width // 2, drum_y), 8)
        
        # Pulsing start button
        pulse = math.sin(pulse_time * 3) * 0.1 + 1.0
        button_text = button_font.render('PRESS ENTER TO START', True, PERFECT_COLOR)
        button_rect = button_text.get_rect(center=(width // 2, 570))
        
        # Scale button
        scaled_button = pygame.transform.scale(
            button_text,
            (int(button_rect.width * pulse), int(button_rect.height * pulse))
        )
        scaled_rect = scaled_button.get_rect(center=(width // 2, 570))
        surface.blit(scaled_button, scaled_rect)
        
        # Scale and display
        screen.fill((0, 0, 0))
        scaled_surface = pygame.transform.scale(surface, (int(width * scale), int(height * scale)))
        screen.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()


def run(screen):
    """Run the rhythm game with song selection"""
    # Initialize assets
    pygame.mixer.music.stop()
    init_assets()
    
    # Go straight to song selection (osu! style)
    total_stars = 0  # TODO: Load from save file
    
    while True:
        result = _show_song_select(screen, total_stars)
        
        if result is None:
            return 'menu'
        
        selected_beatmap = result
        game = RhythmGame(screen, custom_beatmap=selected_beatmap)

        result = game.run()

        # ALWAYS stop the music after leaving a song
        pygame.mixer.music.stop()
        
        if result == 'quit':
            return 'quit'
        
        # Add stars earned to total
        total_stars += game.stars_earned