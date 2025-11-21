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

# Import helper functions
try:
    from games.rhythm import helpers
except ImportError:
    try:
        import helpers
    except ImportError:
        helpers = None
        
# Constants (using globals for simple access)
ASSETS = {}
WIDTH = 1600
HEIGHT = 900
FPS = 60

# Colors
BACKGROUND_COLOR = (40, 40, 50)
TRACK_COLOR = (60, 60, 70)
HIT_CIRCLE_COLOR = (80, 80, 90)
PERFECT_COLOR = (255, 215, 0)
GOOD_COLOR = (150, 255, 150)
MISS_COLOR = (255, 100, 100)
TEXT_COLOR = (255, 255, 255)
MENU_BG_COLOR = (20, 20, 25)
MENU_HIGHLIGHT_COLOR = (50, 50, 60)
MENU_SELECTED_COLOR = (80, 80, 100)

# Game parameters
NOTE_SPEED = 1200.0  # Pixels per second
HIT_WINDOW_PERFECT = 0.05  # +/- seconds for perfect hit
HIT_WINDOW_GOOD = 0.15    # +/- seconds for good hit


# --- Asset Loading ---
# We assume helpers.py contains init_assets and load_sprite, 
# and that the sprite constants are available from helpers.

def init_assets():
    """Initializes and loads all game assets"""
    global ASSETS
    if helpers:
        ASSETS = helpers.load_assets()
    else:
        # Minimal fallback for testing without helpers
        ASSETS = {
            'font_medium': pygame.font.SysFont('segoeui', 36),
            'font_small': pygame.font.SysFont('segoeui', 24)
        }
        print("Warning: helpers.py not found. Using fallback fonts.")

# --- Game Objects ---

class Note:
    """Represents a beat note (Don or Ka)"""
    def __init__(self, note_type, spawn_time, hit_y):
        self.type = note_type  # 'don' or 'ka'
        self.spawn_time = spawn_time  # Absolute time (s) when note should be hit
        self.hit_y = hit_y
        self.hit = False
        self.x = 0  # Current x position
        
        # Calculate visual properties
        self.size = 60
        if note_type == 'don':
            self.sprite = ASSETS.get('note_don')
            self.color = (255, 80, 80) # Fallback color
        else: # 'ka'
            self.sprite = ASSETS.get('note_ka')
            self.color = (100, 180, 255) # Fallback color

        if not self.sprite:
            # Create a simple surface if sprite failed to load
            self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.surface, self.color, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.surface, TEXT_COLOR, (self.size//2, self.size//2), self.size//2, 3)
            self.text = ASSETS.get('font_small', pygame.font.SysFont('segoeui', 24)).render(note_type[0].upper(), True, TEXT_COLOR)
            self.text_rect = self.text.get_rect(center=(self.size//2, self.size//2))
            self.surface.blit(self.text, self.text_rect)
            self.sprite = self.surface

    def update(self, current_time, dt):
        """Update note position based on game time"""
        # Time remaining until hit: spawn_time - current_time
        time_to_hit = self.spawn_time - current_time
        
        # Distance to travel: time_to_hit * NOTE_SPEED
        # The hit circle is at x=200, so position = 200 + (time_to_hit * NOTE_SPEED)
        self.x = 200 + (time_to_hit * NOTE_SPEED)
        
    def draw(self, surface):
        """Draw the note"""
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), self.hit_y))
            surface.blit(self.sprite, rect)
        else:
            # Fallback drawing
            pygame.draw.circle(surface, self.color, (int(self.x), self.hit_y), self.size // 2)

    def is_off_screen(self):
        """Check if note has passed the miss boundary (hit circle)"""
        # Check if the right edge of the note has passed the hit circle center (x=200)
        return self.x < 200 - (self.size // 2)


class HitEffect:
    """Represents a visual effect for a successful hit"""
    def __init__(self, x, y, hit_type):
        self.x = x
        self.y = y
        self.hit_type = hit_type # 'Perfect', 'Good', 'Miss'
        self.duration = 0.5 # Duration in seconds
        self.timer = 0
        
        if self.hit_type == 'Perfect':
            self.color = PERFECT_COLOR
            self.text = 'PERFECT!'
        elif self.hit_type == 'Good':
            self.color = GOOD_COLOR
            self.text = 'GOOD'
        else:
            self.color = MISS_COLOR
            self.text = 'MISS'
            
        self.font = ASSETS.get('font_medium', pygame.font.SysFont('segoeui', 36))
        self.text_surf = self.font.render(self.text, True, self.color)
        self.radius = 10
        self.max_radius = 50
        
    def update(self, dt):
        """Update effect timer and properties"""
        self.timer += dt
        
        # Scale the radius over time
        progress = self.timer / self.duration
        self.radius = 10 + (self.max_radius - 10) * progress
        
        # Fade out the alpha
        alpha = max(0, 255 * (1 - progress * 1.5))
        self.text_surf.set_alpha(alpha)
        
        return self.timer < self.duration

    def draw(self, surface):
        """Draw the effect"""
        # Draw text
        text_rect = self.text_surf.get_rect(center=(self.x, self.y - 40))
        surface.blit(self.text_surf, text_rect)
        
        # Draw expanding circle (only for hits)
        if self.hit_type != 'Miss':
            color = self.color + (int(255 * (1 - self.timer / self.duration)),)
            pygame.draw.circle(surface, color, (self.x, self.y), int(self.radius), 4)

# --- Game State ---

class RhythmGame:
    def __init__(self, custom_beatmap=None):
        # Game state
        self.playing = False
        self.start_time = 0.0 # Absolute time game started (or resumed)
        self.current_time = 0.0 # Time elapsed in song (s)
        self.game_time = 0.0 # Total time elapsed in game loop
        self.song_length = 0.0
        self.notes = []
        self.effects = []
        
        # Score
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = {'Perfect': 0, 'Good': 0, 'Miss': 0}
        self.goal = 0 # Total number of notes
        self.note_index = 0 # Index of the next note to check for hit/miss
        
        # Visuals
        self.hit_circle_x = 200
        self.hit_circle_y = HEIGHT // 2
        self.track_height = 200
        
        # Custom map loading
        self.custom_beatmap = custom_beatmap
        if self.custom_beatmap:
            self.song_length = self._get_song_length()
            self._load_custom_notes()
            self._load_song()
        else:
            self._generate_random_notes()
            self._load_song(default=True)
        
        # Fonts
        self.font_large = ASSETS.get('font_large', pygame.font.SysFont('segoeui', 48, bold=True))
        self.font_medium = ASSETS.get('font_medium', pygame.font.SysFont('segoeui', 36))
        self.font_small = ASSETS.get('font_small', pygame.font.SysFont('segoeui', 24))
        
        print(f"Game initialized with {self.goal} notes.")

    def _get_song_length(self):
        """Attempt to get the song length from the loaded file"""
        if self.custom_beatmap and self.custom_beatmap.get('song_path'):
            try:
                sound = pygame.mixer.Sound(self.custom_beatmap['song_path'])
                return sound.get_length()
            except pygame.error as e:
                print(f"Failed to get song length: {e}")
                return 60.0 # Default to 60s if file fails
        return 60.0 # Default length

    def _load_song(self, default=False):
        """Loads the song file"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        song_path = None
        if self.custom_beatmap and self.custom_beatmap.get('song_path'):
            song_path = self.custom_beatmap['song_path']
        elif default:
            # Fallback for default built-in song if needed
            # For this context, we will skip the default song and rely on custom maps
            # In a full game, you'd load a default track here.
            print("No custom map provided. Default music loading skipped.")
            return

        if song_path:
            try:
                pygame.mixer.music.load(song_path)
                print(f"Loaded song: {os.path.basename(song_path)}")
            except pygame.error as e:
                print(f"Failed to load music file at {song_path}: {e}")
                self.custom_beatmap = None # Disable custom map if music fails

    def _load_custom_notes(self):
        """Load notes from custom beatmap"""
        for note_data in self.custom_beatmap['notes']:
            note_type = note_data['type']
            # Add 2 second offset (time it takes to travel from spawn to hit circle)
            spawn_time = note_data['time'] + 2.0 
            self.notes.append(Note(note_type, spawn_time, self.hit_circle_y))
        
        # --- FIX: Ensure notes are strictly sorted by spawn time ---
        # This is CRITICAL. If the notes are not perfectly chronological, 
        # the game logic breaks, resulting in notes of the same type being 
        # processed/drawn together, ignoring the alternating pattern.
        self.notes.sort(key=lambda note: note.spawn_time)
        # -----------------------------------------------------------
        
        # Update goal to match number of notes
        self.goal = len(self.notes)
        print(f"Loaded {self.goal} notes from custom beatmap")
        
    def _generate_random_notes(self):
        """Generate a random sequence of notes (fallback)"""
        note_types = ['don', 'ka']
        current_time = 3.0 # Start notes after 3 seconds
        self.song_length = 60.0
        self.notes = []

        while current_time < self.song_length + 2.0: # Generate notes up to end of song + 2s travel time
            note_type = random.choice(note_types)
            self.notes.append(Note(note_type, current_time, self.hit_circle_y))
            # Place notes every 0.5 to 1.5 seconds randomly
            current_time += random.uniform(0.5, 1.5)

        self.goal = len(self.notes)

    def start_game(self):
        """Starts the game playback"""
        if self.custom_beatmap and self.custom_beatmap.get('song_path'):
            try:
                pygame.mixer.music.play()
                self.playing = True
                self.start_time = pygame.time.get_ticks() / 1000.0 # Time when music started
                self.current_time = 0.0
                return True
            except pygame.error as e:
                print(f"Could not play music: {e}")
                return False
        return False
        
    def check_hit(self, hit_type):
        """Check for a hit event (Don or Ka press)"""
        if not self.playing:
            return

        # Find the next unhit note
        if self.note_index < len(self.notes):
            next_note = self.notes[self.note_index]
            
            # Check if hit type matches the note type
            if next_note.type != hit_type:
                return # Wrong note type pressed

            # Calculate time difference from perfect hit time (spawn_time)
            time_diff = abs(next_note.spawn_time - self.current_time)
            
            # Determine hit quality
            if time_diff <= HIT_WINDOW_PERFECT:
                self._apply_hit('Perfect', next_note)
            elif time_diff <= HIT_WINDOW_GOOD:
                self._apply_hit('Good', next_note)
            else:
                # Early press outside the good window (treat as no hit/wrong time)
                # It's better to let it register as a miss later if it's too early
                return
        
    def _apply_hit(self, quality, note):
        """Updates score, combo, and adds effect for a successful hit"""
        note.hit = True
        self.note_index += 1
        
        if quality == 'Perfect':
            self.score += 500
            self.hits['Perfect'] += 1
        elif quality == 'Good':
            self.score += 200
            self.hits['Good'] += 1

        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        
        self.effects.append(HitEffect(self.hit_circle_x, self.hit_circle_y, quality))

    def _check_miss(self):
        """Checks if the next note has passed the hit window without being hit"""
        if self.note_index < len(self.notes):
            next_note = self.notes[self.note_index]
            
            # Check if the note has passed the miss boundary (hit time + GOOD window)
            miss_time = next_note.spawn_time + HIT_WINDOW_GOOD
            
            if self.current_time >= miss_time:
                # Miss occurred
                self.hits['Miss'] += 1
                self.combo = 0
                self.note_index += 1
                
                # Add a 'Miss' effect at the hit circle
                self.effects.append(HitEffect(self.hit_circle_x, self.hit_circle_y, 'Miss'))

    def update(self, dt):
        """Update game logic"""
        self.game_time += dt
        
        # Update current song time
        if self.playing:
            # Get position from mixer, adjust by start offset
            try:
                music_pos = pygame.mixer.music.get_pos() / 1000.0
                self.current_time = music_pos
                
                # Check for end of song
                if music_pos >= self.song_length:
                    self.playing = False
                    pygame.mixer.music.stop()
                    return 'finished'
                    
            except pygame.error:
                # Occurs if mixer state is lost or corrupted
                self.playing = False
                return 'finished'
        
        # Update notes
        for note in self.notes:
            if not note.hit:
                note.update(self.current_time, dt)

        # Check for misses (must be done after note updates)
        if self.playing:
            self._check_miss()
            
        # Update effects
        self.effects = [effect for effect in self.effects if effect.update(dt)]
        
        return 'playing'

    def draw(self, screen):
        """Draw game elements"""
        # Draw background
        screen.fill(BACKGROUND_COLOR)
        
        # Draw track
        track_rect = pygame.Rect(0, self.hit_circle_y - self.track_height // 2, WIDTH, self.track_height)
        pygame.draw.rect(screen, TRACK_COLOR, track_rect)
        
        # Draw notes
        for note in self.notes:
            if not note.hit and note.x < WIDTH + 100:
                note.draw(screen)

        # Draw hit circle
        drum_sprite = ASSETS.get('drum')
        if drum_sprite:
            drum_rect = drum_sprite.get_rect(center=(self.hit_circle_x, self.hit_circle_y))
            screen.blit(drum_sprite, drum_rect)
        else:
            pygame.draw.circle(screen, HIT_CIRCLE_COLOR, (self.hit_circle_x, self.hit_circle_y), 80)
            pygame.draw.circle(screen, TEXT_COLOR, (self.hit_circle_x, self.hit_circle_y), 80, 5)

        # Draw effects
        for effect in self.effects:
            effect.draw(screen)

        # Draw UI
        self._draw_ui(screen)
        
    def _draw_ui(self, screen):
        """Draw score, combo, and HUD elements"""
        
        # Top bar
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, WIDTH, 80))
        
        # Score
        score_text = self.font_large.render(f"{self.score:07d}", True, PERFECT_COLOR)
        screen.blit(score_text, (50, 10))
        
        # Song Info
        if self.custom_beatmap:
            name = self.custom_beatmap.get('name', 'Unknown Song')
            artist = self.custom_beatmap.get('artist', 'Unknown Artist')
            info_text = self.font_medium.render(f"{name} - {artist}", True, TEXT_COLOR)
            screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 10))
            
            diff_text = self.font_small.render(f"Difficulty: {self.custom_beatmap.get('difficulty', 'N/A')}", True, self.custom_beatmap.get('color', TEXT_COLOR))
            screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, 45))
        
        # Combo
        if self.combo > 0:
            combo_text = self.font_large.render(f"{self.combo}", True, PERFECT_COLOR if self.combo >= 10 else GOOD_COLOR)
            combo_rect = combo_text.get_rect(center=(self.hit_circle_x, self.hit_circle_y + 120))
            screen.blit(combo_text, combo_rect)
            
            combo_label = self.font_small.render("COMBO", True, TEXT_COLOR)
            combo_label_rect = combo_label.get_rect(center=(self.hit_circle_x, self.hit_circle_y + 155))
            screen.blit(combo_label, combo_label_rect)
            
        # Time
        time_text = self.font_small.render(f"Time: {self.current_time:.1f}s / {self.song_length:.1f}s", True, TEXT_COLOR)
        screen.blit(time_text, (WIDTH - time_text.get_width() - 50, 10))


def _show_song_select(screen, total_stars):
    """Shows the song selection screen and returns the selected beatmap data"""
    clock = pygame.time.Clock()
    
    # Load beatmaps
    if beatmap_loader:
        beatmaps = beatmap_loader.scan_beatmaps()
    else:
        beatmaps = []
        
    if not beatmaps:
        font = pygame.font.SysFont('segoeui', 36)
        text = font.render("No beatmaps found. Create one with map_maker.py!", True, TEXT_COLOR)
        screen.fill(MENU_BG_COLOR)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        pygame.time.wait(2000)
        return None # Return to main menu/exit
        
    selected_index = 0
    font_large = ASSETS.get('font_large', pygame.font.SysFont('segoeui', 48, bold=True))
    font_medium = ASSETS.get('font_medium', pygame.font.SysFont('segoeui', 36))
    font_small = ASSETS.get('font_small', pygame.font.SysFont('segoeui', 24))
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(beatmaps)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(beatmaps)
                elif event.key == pygame.K_RETURN:
                    return beatmaps[selected_index]
        
        # Drawing
        screen.fill(MENU_BG_COLOR)
        
        title_text = font_large.render("Select a Song", True, PERFECT_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Display list of songs
        y_offset = 150
        for i, map_data in enumerate(beatmaps):
            is_selected = (i == selected_index)
            
            # Draw background box
            rect = pygame.Rect(WIDTH // 4, y_offset + i * 80, WIDTH // 2, 70)
            color = MENU_SELECTED_COLOR if is_selected else MENU_HIGHLIGHT_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            # Song Name
            name_text = font_medium.render(map_data['name'], True, TEXT_COLOR)
            screen.blit(name_text, (rect.x + 20, rect.y + 5))
            
            # Artist and Difficulty
            artist_diff = f"{map_data['artist']} - {map_data['difficulty']}"
            diff_text = font_small.render(artist_diff, True, map_data['color'])
            screen.blit(diff_text, (rect.x + 20, rect.y + 40))
            
            # Stars
            star_size = 20
            star_spacing = 5
            total_star_width = map_data['stars'] * (star_size + star_spacing) - star_spacing
            star_x = rect.x + rect.width - total_star_width - 10
            
            star_sprite = ASSETS.get('star')
            for j in range(map_data['stars']):
                if star_sprite:
                    star_rect = star_sprite.get_rect(topleft=(star_x + j * (star_size + star_spacing), rect.y + 25))
                    screen.blit(star_sprite, star_rect)
                else:
                    # Fallback star drawing
                    pygame.draw.circle(screen, PERFECT_COLOR, (star_x + j * (star_size + star_spacing) + star_size//2, rect.y + 35), star_size//3)

        pygame.display.flip()

    return None

def run(screen):
    """Run the rhythm game with song selection"""
    # Initialize assets
    init_assets()
    
    # Go straight to song selection (osu! style)
    
    while True:
        # result is the selected beatmap data dict or None
        result = _show_song_select(screen, 0) # total_stars is placeholder
        
        if result is None:
            return 'menu'
        
        custom_beatmap = result
        
        # Instantiate and start the game
        game = RhythmGame(custom_beatmap=custom_beatmap)
        
        # If song loading failed, return to selection
        if not game.custom_beatmap:
            print("Returning to song selection due to song load failure.")
            continue
            
        clock = pygame.time.Clock()
        game_state = 'ready'
        
        # Loop to wait for start
        while game_state == 'ready':
            dt = clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return 'menu'
                    if event.key == pygame.K_RETURN:
                        if game.start_game():
                            game_state = 'playing'
                        else:
                            # If start failed (e.g., song issue), return to select
                            game_state = 'finished'
                            
            _draw_game_ready_screen(screen, game.custom_beatmap, game.font_medium, game.font_large, game.hit_circle_x, game.hit_circle_y, dt)
        
        # Main game loop
        while game_state == 'playing':
            dt = clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return 'quit'
                if event.type == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return 'menu'
                if event.type == pygame.KEYDOWN:
                    # Hit detection keys: Z and X for Don (inner drum), C and V for Ka (outer drum)
                    if event.key == pygame.K_z or event.key == pygame.K_x:
                        game.check_hit('don')
                    elif event.key == pygame.K_c or event.key == pygame.K_v:
                        game.check_hit('ka')
                        
            # Update game state
            game_state = game.update(dt)
            
            # Drawing
            game.draw(screen)
            pygame.display.flip()
            
        # Game finished loop (show results)
        if game_state == 'finished':
            _show_results(screen, game)
            
        # Loop waits until user presses ESC or clicks close
        # After results, the outer `while True` loop will return to song selection.


def _draw_game_ready_screen(screen, beatmap, font_medium, font_large, hit_circle_x, hit_circle_y, dt):
    """Draws the screen while waiting for the user to press ENTER"""
    
    screen.fill(BACKGROUND_COLOR)
    
    # Draw track and hit circle minimally
    track_height = 200
    track_rect = pygame.Rect(0, hit_circle_y - track_height // 2, WIDTH, track_height)
    pygame.draw.rect(screen, TRACK_COLOR, track_rect)
    
    drum_sprite = ASSETS.get('drum')
    if drum_sprite:
        drum_rect = drum_sprite.get_rect(center=(hit_circle_x, hit_circle_y))
        screen.blit(drum_sprite, drum_rect)
    else:
        pygame.draw.circle(screen, HIT_CIRCLE_COLOR, (hit_circle_x, hit_circle_y), 80)
        pygame.draw.circle(screen, TEXT_COLOR, (hit_circle_x, hit_circle_y), 80, 5)

    # Display song information large and centered
    name_text = font_large.render(beatmap.get('name', 'Unknown Song'), True, PERFECT_COLOR)
    screen.blit(name_text, name_text.get_rect(center=(WIDTH // 2, 200)))
    
    artist_text = font_medium.render(f"by {beatmap.get('artist', 'Unknown Artist')}", True, TEXT_COLOR)
    screen.blit(artist_text, artist_text.get_rect(center=(WIDTH // 2, 260)))

    diff_text = font_medium.render(f"Difficulty: {beatmap.get('difficulty', 'N/A')}", True, beatmap.get('color', TEXT_COLOR))
    screen.blit(diff_text, diff_text.get_rect(center=(WIDTH // 2, 320)))

    # Draw pulsing button text
    _draw_pulsing_text(screen, font_large, "PRESS ENTER TO START", 500, dt)

    pygame.display.flip()

def _draw_pulsing_text(screen, font, text, y_pos, dt):
    """Helper function to draw text with a subtle pulsing animation"""
    global game_ready_time
    if 'game_ready_time' not in globals():
        globals()['game_ready_time'] = 0
    globals()['game_ready_time'] += dt
    
    pulse_time = globals()['game_ready_time']
    # Sine wave for pulsing scale (1.0 to 1.1)
    pulse = math.sin(pulse_time * 3) * 0.1 + 1.0
    
    button_text = font.render(text, True, PERFECT_COLOR)
    button_rect = button_text.get_rect(center=(WIDTH // 2, y_pos))
    
    # Scale button
    scaled_button = pygame.transform.scale(
        button_text,
        (int(button_rect.width * pulse), int(button_rect.height * pulse))
    )
    scaled_rect = scaled_button.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(scaled_button, scaled_rect)


def _show_results(screen, game):
    """Display the final score and stats"""
    clock = pygame.time.Clock()
    
    font_xl = ASSETS.get('font_xl', pygame.font.SysFont('segoeui', 72, bold=True))
    font_large = ASSETS.get('font_large', pygame.font.SysFont('segoeui', 48, bold=True))
    font_medium = ASSETS.get('font_medium', pygame.font.SysFont('segoeui', 36))
    
    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        screen.fill(MENU_BG_COLOR)
        
        # Title
        title_text = font_xl.render("Results", True, PERFECT_COLOR)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 100)))
        
        # Song Info
        name = game.custom_beatmap.get('name', 'Unknown Song')
        artist = game.custom_beatmap.get('artist', 'Unknown Artist')
        info_text = font_medium.render(f"{name} by {artist}", True, TEXT_COLOR)
        screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, 180)))
        
        # Final Score
        score_label = font_large.render("FINAL SCORE", True, TEXT_COLOR)
        screen.blit(score_label, score_label.get_rect(center=(WIDTH // 2, 300)))
        
        score_text = font_xl.render(f"{game.score:07d}", True, PERFECT_COLOR)
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 370)))
        
        # Hit Stats
        stats_x = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]
        stat_y = 500
        
        stats = [
            ('Perfect', PERFECT_COLOR, game.hits['Perfect']),
            ('Good', GOOD_COLOR, game.hits['Good']),
            ('Miss', MISS_COLOR, game.hits['Miss'])
        ]
        
        for i, (label, color, count) in enumerate(stats):
            label_text = font_medium.render(label, True, color)
            count_text = font_large.render(str(count), True, color)
            
            label_rect = label_text.get_rect(center=(stats_x[i], stat_y))
            count_rect = count_text.get_rect(center=(stats_x[i], stat_y + 50))
            
            screen.blit(label_text, label_rect)
            screen.blit(count_text, count_rect)
            
        # Max Combo
        combo_label = font_medium.render("Max Combo", True, TEXT_COLOR)
        combo_text = font_large.render(str(game.max_combo), True, GOOD_COLOR)
        
        screen.blit(combo_label, combo_label.get_rect(center=(WIDTH // 2, 650)))
        screen.blit(combo_text, combo_text.get_rect(center=(WIDTH // 2, 700)))
        
        # Exit instruction
        exit_text = font_small.render("Press ESC to return to song selection", True, (150, 150, 150))
        screen.blit(exit_text, exit_text.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
        
        pygame.display.flip()

# NOTE: The provided code doesn't define the full main loop initialization. 
# We assume the user runs this via a main application that calls rhythm_game.run(screen).