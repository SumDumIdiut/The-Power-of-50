"""
Rhythm Game Map Maker
Create custom beatmaps for songs
"""
import pygame
import json
import os
from tkinter import Tk, filedialog, simpledialog, messagebox
import sys

# Colors
BG_COLOR = (40, 40, 50)
TRACK_COLOR = (60, 60, 70)
DON_COLOR = (255, 80, 80)
KA_COLOR = (100, 180, 255)
GRID_COLOR = (80, 80, 90)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 70, 80)
BUTTON_HOVER = (90, 90, 100)

class Note:
    def __init__(self, note_type, time):
        self.type = note_type  # 'don' or 'ka'
        self.time = time  # Time in seconds
        
    def to_dict(self):
        return {'type': self.type, 'time': self.time}
    
    @staticmethod
    def from_dict(data):
        return Note(data['type'], data['time'])


class MapMaker:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.width = 1600
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Rhythm Game Map Maker')
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('segoeui', 24)
        self.small_font = pygame.font.SysFont('segoeui', 18)
        self.title_font = pygame.font.SysFont('segoeui', 32, bold=True)
        
        # Map data
        self.notes = []
        self.song_path = None
        self.song_name = ""
        self.artist = ""
        self.difficulty = "Normal"
        self.bpm = 120
        self.stars = 3
        
        # Playback
        self.playing = False
        self.current_time = 0
        self.song_length = 0
        
        # View
        self.scroll_offset = 0  # Horizontal scroll in seconds
        self.pixels_per_second = 100
        self.track_y = 400
        self.track_height = 200
        
        # UI state
        self.delete_mode = False
        self.snap_mode = True  # Snap to beat by default
        self.show_help = True
        
        # Difficulty options with BPM
        self.difficulties = [
            ('Beginner', 1, 60), ('Easy', 2, 90), ('Normal', 3, 120), ('Hard', 4, 150), ('Expert', 5, 180),
            ('Master', 6, 210), ('Extreme', 7, 240), ('Insane', 8, 270), ('Demon', 9, 300), ('God', 10, 350)
        ]
        self.difficulty_index = 2  # Default to Normal
    
    def import_song(self):
        """Import a song file"""
        root = Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Select Song File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                pygame.mixer.music.load(file_path)
                self.song_path = file_path
                
                # Get song length
                sound = pygame.mixer.Sound(file_path)
                self.song_length = sound.get_length()
                
                print(f"Loaded song: {file_path} ({self.song_length:.2f}s)")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load song: {e}")
                return False
        return False
    
    def set_difficulty(self):
        """Set difficulty before mapping"""
        root = Tk()
        root.withdraw()
        
        # Show difficulty selection dialog
        diff_names = [f"{name} ({stars} stars, {bpm} BPM)" for name, stars, bpm in self.difficulties]
        selected = simpledialog.askstring(
            "Select Difficulty",
            f"Enter difficulty number (0-9):\n" + "\n".join(f"{i}: {diff_names[i]}" for i in range(len(diff_names)))
        )
        
        if selected and selected.isdigit():
            idx = int(selected)
            if 0 <= idx < len(self.difficulties):
                self.difficulty_index = idx
                self.difficulty, self.stars, self.bpm = self.difficulties[idx]
                print(f"Set difficulty to {self.difficulty} ({self.stars} stars, {self.bpm} BPM)")
    
    def set_bpm(self):
        """Set BPM for grid lines"""
        root = Tk()
        root.withdraw()
        
        bpm_str = simpledialog.askstring("Set BPM", f"Enter BPM (current: {self.bpm}):")
        if bpm_str and bpm_str.isdigit():
            self.bpm = int(bpm_str)
            print(f"Set BPM to {self.bpm}")
    
    def snap_to_beat(self, time):
        """Snap time to nearest beat"""
        if self.bpm <= 0:
            return time
        
        beat_duration = 60.0 / self.bpm
        nearest_beat = round(time / beat_duration)
        return nearest_beat * beat_duration
    
    def add_note(self, note_type, time):
        """Add a note at the specified time"""
        # Snap to beat if enabled
        if self.snap_mode:
            time = self.snap_to_beat(time)
        
        # Check if note already exists at this time
        for note in self.notes:
            if abs(note.time - time) < 0.05:  # Within 50ms
                return
        
        self.notes.append(Note(note_type, time))
        self.notes.sort(key=lambda n: n.time)
        print(f"Added {note_type} note at {time:.2f}s")
    
    def delete_note(self, time):
        """Delete note at the specified time"""
        for note in self.notes[:]:
            if abs(note.time - time) < 0.1:  # Within 100ms
                self.notes.remove(note)
                print(f"Deleted {note.type} note at {note.time:.2f}s")
                return
    
    def export_map(self):
        """Export the beatmap as a bundled folder"""
        if not self.notes:
            messagebox.showwarning("Warning", "No notes to export!")
            return
        
        if not self.song_path:
            messagebox.showwarning("Warning", "No song imported! Import a song first.")
            return
        
        root = Tk()
        root.withdraw()
        
        # Get song name and artist
        self.song_name = simpledialog.askstring("Song Name", "Enter song name:")
        if not self.song_name:
            return
        
        self.artist = simpledialog.askstring("Artist", "Enter artist name:")
        if not self.artist:
            return
        
        # Create folder name
        folder_name = f"{self.song_name.replace(' ', '_')}_{self.difficulty}"
        beatmaps_folder = os.path.join("games", "rhythm", "beatmaps")
        
        # Create beatmaps folder if it doesn't exist
        if not os.path.exists(beatmaps_folder):
            os.makedirs(beatmaps_folder)
        
        # Create song folder
        song_folder = os.path.join(beatmaps_folder, folder_name)
        if not os.path.exists(song_folder):
            os.makedirs(song_folder)
        
        # Copy song file to folder
        import shutil
        song_filename = os.path.basename(self.song_path)
        song_dest = os.path.join(song_folder, song_filename)
        shutil.copy2(self.song_path, song_dest)
        
        # Create beatmap data
        beatmap = {
            'song_name': self.song_name,
            'artist': self.artist,
            'difficulty': self.difficulty,
            'stars': self.stars,
            'bpm': self.bpm,
            'song_file': song_filename,
            'notes': [note.to_dict() for note in self.notes]
        }
        
        # Save beatmap.json in the folder
        beatmap_path = os.path.join(song_folder, 'beatmap.json')
        with open(beatmap_path, 'w') as f:
            json.dump(beatmap, f, indent=2)
        
        messagebox.showinfo("Success", f"Beatmap exported to:\n{song_folder}\n\nSong and beatmap bundled together!")
        print(f"Exported beatmap bundle: {song_folder}")
    
    def load_map(self):
        """Load an existing beatmap bundle"""
        root = Tk()
        root.withdraw()
        
        # Select beatmap.json file
        file_path = filedialog.askopenfilename(
            title="Load Beatmap (select beatmap.json)",
            initialdir="games/rhythm/beatmaps",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    beatmap = json.load(f)
                
                self.song_name = beatmap['song_name']
                self.artist = beatmap['artist']
                self.difficulty = beatmap['difficulty']
                self.stars = beatmap['stars']
                self.bpm = beatmap['bpm']
                self.notes = [Note.from_dict(n) for n in beatmap['notes']]
                
                # Load the song file from the same folder
                folder = os.path.dirname(file_path)
                song_file = beatmap.get('song_file', '')
                if song_file:
                    song_path = os.path.join(folder, song_file)
                    if os.path.exists(song_path):
                        pygame.mixer.music.load(song_path)
                        self.song_path = song_path
                        sound = pygame.mixer.Sound(song_path)
                        self.song_length = sound.get_length()
                
                print(f"Loaded beatmap: {self.song_name} by {self.artist}")
                messagebox.showinfo("Success", f"Loaded: {self.song_name} - {self.difficulty}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load beatmap: {e}")
    
    def time_to_x(self, time):
        """Convert time to screen x position"""
        return int((time - self.scroll_offset) * self.pixels_per_second) + 100
    
    def x_to_time(self, x):
        """Convert screen x position to time"""
        return ((x - 100) / self.pixels_per_second) + self.scroll_offset
    
    def draw_grid(self):
        """Draw BPM grid lines"""
        if self.bpm <= 0:
            return
        
        beat_duration = 60.0 / self.bpm
        
        # Draw vertical lines for each beat
        start_beat = int(self.scroll_offset / beat_duration)
        end_beat = int((self.scroll_offset + self.width / self.pixels_per_second) / beat_duration) + 1
        
        for beat in range(start_beat, end_beat):
            time = beat * beat_duration
            x = self.time_to_x(time)
            
            if 0 <= x <= self.width:
                # Every 4th beat is brighter
                color = (100, 100, 110) if beat % 4 == 0 else GRID_COLOR
                width = 2 if beat % 4 == 0 else 1
                pygame.draw.line(self.screen, color, (x, self.track_y - self.track_height // 2),
                               (x, self.track_y + self.track_height // 2), width)
    
    def draw_track(self):
        """Draw the note track"""
        track_rect = pygame.Rect(0, self.track_y - self.track_height // 2, self.width, self.track_height)
        pygame.draw.rect(self.screen, TRACK_COLOR, track_rect)
        pygame.draw.rect(self.screen, (100, 100, 110), track_rect, 2)
        
        # Center line
        pygame.draw.line(self.screen, (120, 120, 130), (0, self.track_y), (self.width, self.track_y), 2)
    
    def draw_notes(self):
        """Draw all notes"""
        for note in self.notes:
            x = self.time_to_x(note.time)
            
            if -50 <= x <= self.width + 50:
                color = DON_COLOR if note.type == 'don' else KA_COLOR
                pygame.draw.circle(self.screen, color, (x, self.track_y), 20)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, self.track_y), 20, 3)
    
    def draw_playhead(self):
        """Draw current time indicator"""
        x = self.time_to_x(self.current_time)
        pygame.draw.line(self.screen, (255, 255, 0), (x, 0), (x, self.height), 3)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Top bar
        pygame.draw.rect(self.screen, (30, 30, 40), (0, 0, self.width, 80))
        
        # Title
        title = self.title_font.render('Rhythm Game Map Maker', True, TEXT_COLOR)
        self.screen.blit(title, (20, 20))
        
        # Info
        info_y = 60
        if self.song_path:
            song_text = self.small_font.render(f"Song: {os.path.basename(self.song_path)}", True, TEXT_COLOR)
            self.screen.blit(song_text, (20, info_y))
        
        # Draw difficulty text with custom star
        diff_text = self.small_font.render(f"Difficulty: {self.difficulty} ({self.stars} stars) | BPM: {self.bpm}", True, TEXT_COLOR)
        self.screen.blit(diff_text, (400, info_y))
        
        time_text = self.small_font.render(f"Time: {self.current_time:.2f}s / {self.song_length:.2f}s", True, TEXT_COLOR)
        self.screen.blit(time_text, (800, info_y))
        
        notes_text = self.small_font.render(f"Notes: {len(self.notes)}", True, TEXT_COLOR)
        self.screen.blit(notes_text, (1100, info_y))
        
        # Mode indicators
        mode_x = 1250
        if self.delete_mode:
            mode_text = self.font.render('DELETE', True, (255, 100, 100))
            self.screen.blit(mode_text, (mode_x, 25))
        
        if self.snap_mode:
            snap_text = self.small_font.render('SNAP: ON', True, (100, 255, 100))
            self.screen.blit(snap_text, (mode_x, 55))
        else:
            snap_text = self.small_font.render('SNAP: OFF', True, (150, 150, 150))
            self.screen.blit(snap_text, (mode_x, 55))
        
        # Bottom help
        if self.show_help:
            help_y = self.height - 180
            pygame.draw.rect(self.screen, (30, 30, 40), (0, help_y, self.width, 180))
            
            help_texts = [
                "Controls:",
                "I - Import Song | D - Set Difficulty | B - Set BPM | L - Load Map | E - Export Map",
                "SPACE - Play/Pause | LEFT/RIGHT - Scroll | UP/DOWN - Zoom",
                "LEFT CLICK - Place Red (Don) | RIGHT CLICK - Place Blue (Ka)",
                "2 - Toggle Delete Mode | S - Toggle Snap to Beat | H - Toggle Help | ESC - Quit"
            ]
            
            for i, text in enumerate(help_texts):
                help_surf = self.small_font.render(text, True, TEXT_COLOR)
                self.screen.blit(help_surf, (20, help_y + 10 + i * 30))
    
    def run(self):
        """Main loop"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            # Update playback
            if self.playing and self.song_path:
                if not pygame.mixer.music.get_busy():
                    self.playing = False
                else:
                    self.current_time = pygame.mixer.music.get_pos() / 1000.0 + self.scroll_offset
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_i:
                        self.import_song()
                    elif event.key == pygame.K_d:
                        self.set_difficulty()
                    elif event.key == pygame.K_b:
                        self.set_bpm()
                    elif event.key == pygame.K_e:
                        self.export_map()
                    elif event.key == pygame.K_l:
                        self.load_map()
                    elif event.key == pygame.K_SPACE:
                        if self.song_path:
                            if self.playing:
                                pygame.mixer.music.pause()
                                self.playing = False
                            else:
                                pygame.mixer.music.play(start=self.scroll_offset)
                                self.playing = True
                    elif event.key == pygame.K_2:
                        self.delete_mode = not self.delete_mode
                    elif event.key == pygame.K_s:
                        self.snap_mode = not self.snap_mode
                        snap_text = 'ON' if self.snap_mode else 'OFF'
                        print(f"Snap mode: {snap_text}")
                    elif event.key == pygame.K_h:
                        self.show_help = not self.show_help
                    elif event.key == pygame.K_LEFT:
                        self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.scroll_offset = min(self.song_length - 5, self.scroll_offset + 1)
                    elif event.key == pygame.K_UP:
                        self.pixels_per_second = min(300, self.pixels_per_second + 20)
                    elif event.key == pygame.K_DOWN:
                        self.pixels_per_second = max(50, self.pixels_per_second - 20)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    
                    # Check if click is on track
                    if self.track_y - self.track_height // 2 <= mouse_y <= self.track_y + self.track_height // 2:
                        click_time = self.x_to_time(mouse_x)
                        
                        # Allow placing notes even without song loaded, or within song length
                        if click_time >= 0 and (self.song_length == 0 or click_time <= self.song_length):
                            if self.delete_mode:
                                self.delete_note(click_time)
                            else:
                                if event.button == 1:  # Left click - Don (red)
                                    self.add_note('don', click_time)
                                elif event.button == 3:  # Right click - Ka (blue)
                                    self.add_note('ka', click_time)
            
            # Draw
            self.screen.fill(BG_COLOR)
            self.draw_track()
            self.draw_grid()
            self.draw_notes()
            self.draw_playhead()
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()


if __name__ == '__main__':
    maker = MapMaker()
    maker.run()
