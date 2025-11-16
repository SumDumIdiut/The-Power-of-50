import pygame
import sys
import math

class Textbox:
    def __init__(self, screen):
        self.display_screen = screen
        screen_width, screen_height = screen.get_size()
        
        # Fixed game dimensions
        self.width = 1280
        self.height = 720
        
        # Create a surface at fixed resolution
        self.screen = pygame.Surface((self.width, self.height))
        
        # Calculate scale to fit display (maintain aspect ratio)
        scale_x = screen_width / self.width
        scale_y = screen_height / self.height
        self.scale = min(scale_x, scale_y)
        
        # Calculate offset to center the game
        self.offset_x = int((screen_width - self.width * self.scale) // 2)
        self.offset_y = int((screen_height - self.height * self.scale) // 2)
        
        # Use a nicer system font
        self.font = pygame.font.SysFont('segoeui', 36, bold=False)  # Segoe UI for modern look
        self.title_font = pygame.font.SysFont('segoeui', 48, bold=True)
        self.clock = pygame.time.Clock()
        
        # Dialogue sequences - load from file
        self.dialogues = self.load_dialogues_from_file("dialogues.txt")
        
        self.current_dialogue = 0
        self.displayed_text = ""
        self.full_text = ""
        self.char_index = 0
        self.text_speed = 2  # Characters per frame
        self.box_alpha = 0
        self.fading_in = True
        
        # Hero animation (scaled for 1280x720)
        self.hero_y_offset = 0
        self.hero_animation_time = 0
        self.hero_base_y = 200
    
    def load_dialogues_from_file(self, filename):
        """Load dialogues from a text file. Format: Speaker: Text"""
        dialogues = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        speaker, text = line.split(':', 1)
                        dialogues.append({
                            "speaker": speaker.strip(),
                            "text": text.strip()
                        })
        except FileNotFoundError:
            print(f"Dialogue file '{filename}' not found. Starting in input mode.")
        except Exception as e:
            print(f"Error loading dialogues: {e}")
        return dialogues
        
    def draw_hero_sprite(self):
        """Draw the hero sprite (snake-like robot with eyes)"""
        is_hero_speaking = (self.dialogues and 
                           self.dialogues[self.current_dialogue]["speaker"] == "Hero")
        
        if is_hero_speaking:
            self.hero_animation_time += 0.15
            self.hero_y_offset = math.sin(self.hero_animation_time) * 30
        else:
            self.hero_y_offset = 0
            self.hero_animation_time = 0
        
        hero_x = 200  # Scaled for 1280x720
        hero_y = self.hero_base_y + self.hero_y_offset
        
        # Draw body (scaled)
        segment_size = 40
        num_segments = 4
        for i in range(num_segments):
            y_pos = hero_y + (i * segment_size)
            green_val = max(50, 200 - (i * 30))  # Prevent negative values
            pygame.draw.rect(self.screen, (0, green_val, 0), (hero_x, y_pos, 53, segment_size))
            pygame.draw.rect(self.screen, (0, max(0, green_val - 50), 0), (hero_x, y_pos, 53, segment_size), 4)
            pygame.draw.circle(self.screen, (150, 150, 150), (hero_x + 13, int(y_pos + 13)), 4)
            pygame.draw.circle(self.screen, (150, 150, 150), (hero_x + 40, int(y_pos + 13)), 4)
        
        # Head
        head_rect = pygame.Rect(hero_x - 7, int(hero_y - 13), 67, 53)
        pygame.draw.rect(self.screen, (0, 220, 0), head_rect, border_radius=13)
        pygame.draw.rect(self.screen, (0, 170, 0), head_rect, 4, border_radius=13)
        
        # Eyes
        eye_y = int(hero_y + 7)
        for x_offset in (13, 40):
            pygame.draw.circle(self.screen, (255, 255, 255), (hero_x + x_offset, eye_y), 11)
            pygame.draw.circle(self.screen, (0, 0, 255), (hero_x + x_offset, eye_y), 7)
            pygame.draw.circle(self.screen, (0, 0, 0), (hero_x + x_offset, eye_y), 4)
        
        # Antenna
        pygame.draw.line(self.screen, (200, 200, 0), (hero_x + 27, int(hero_y - 13)), (hero_x + 27, int(hero_y - 33)), 4)
        pygame.draw.circle(self.screen, (255, 0, 0), (hero_x + 27, int(hero_y - 33)), 7)
        
        # Glow effect
        if is_hero_speaking:
            glow_surface = pygame.Surface((107, 213), pygame.SRCALPHA)
            glow_alpha = int(abs(math.sin(self.hero_animation_time * 2)) * 50)
            pygame.draw.circle(glow_surface, (0, 255, 0, glow_alpha), (53, 107), 80)
            self.screen.blit(glow_surface, (hero_x - 27, int(hero_y - 27)))
        
        # Return head position for mask
        return (hero_x + 27, int(hero_y))

    def draw_wizard_sprite(self):
        """Draw the wizard sprite (scaled for 1280x720)"""
        is_wizard_speaking = (self.dialogues and 
                             self.dialogues[self.current_dialogue]["speaker"] == "Wizard")
        
        wizard_x = 1000  # Scaled for 1280x720
        wizard_y = 200
        
        if is_wizard_speaking:
            wizard_y += math.sin(pygame.time.get_ticks() * 0.003) * 11
        
        wizard_y = int(wizard_y)
        
        # Robe (scaled)
        robe_points = [(wizard_x + 27, wizard_y + 53), (wizard_x, wizard_y + 160), (wizard_x + 53, wizard_y + 160)]
        pygame.draw.polygon(self.screen, (60, 0, 120), robe_points)
        pygame.draw.polygon(self.screen, (100, 0, 200), robe_points, 4)
        
        # Head
        pygame.draw.circle(self.screen, (220, 180, 140), (wizard_x + 27, wizard_y + 33), 20)
        
        # Hat
        hat_points = [(wizard_x + 27, wizard_y - 27), (wizard_x + 7, wizard_y + 13), (wizard_x + 47, wizard_y + 13)]
        pygame.draw.polygon(self.screen, (60, 0, 120), hat_points)
        pygame.draw.polygon(self.screen, (100, 0, 200), hat_points, 3)
        pygame.draw.circle(self.screen, (255, 215, 0), (wizard_x + 24, wizard_y), 4)
        
        # Beard
        pygame.draw.polygon(self.screen, (200, 200, 200), [(wizard_x + 27, wizard_y + 40), (wizard_x + 13, wizard_y + 60), (wizard_x + 40, wizard_y + 60)])
        
        # Eyes
        for eye_x in (wizard_x + 20, wizard_x + 33):
            pygame.draw.circle(self.screen, (255, 255, 255), (eye_x, wizard_y + 29), 4)
            pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, wizard_y + 29), 3)
        
        # Staff
        pygame.draw.line(self.screen, (139, 69, 19), (wizard_x + 47, wizard_y + 67), (wizard_x + 60, wizard_y + 147), 5)
        
        # Magic orb
        if is_wizard_speaking:
            orb_glow = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100)
            pygame.draw.circle(self.screen, (100 + orb_glow, 100, 255), (wizard_x + 60, wizard_y + 60), 11)
        else:
            pygame.draw.circle(self.screen, (150, 100, 255), (wizard_x + 60, wizard_y + 60), 11)
        
        # Return head position for mask
        return (wizard_x + 27, wizard_y + 13)

    def draw_speaker_mask(self, hero_head, wizard_head):
        """Draw spotlight mask around current speaker (scaled for 1280x720)"""
        # Determine current speaker
        if self.dialogues and self.current_dialogue < len(self.dialogues):
            speaker = self.dialogues[self.current_dialogue]["speaker"]
        else:
            speaker = "Hero"  # Default
        
        if speaker == "Hero":
            center = (hero_head[0], hero_head[1])
            color = (0, 255, 100, 100)
        else:
            center = (wizard_head[0], wizard_head[1])
            color = (150, 100, 255, 100)
        
        mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 150))
        pygame.draw.circle(mask_surface, (0, 0, 0, 0), center, 107)  # Scaled radius
        pygame.draw.circle(mask_surface, color, center, 107, 5)  # Scaled border
        self.screen.blit(mask_surface, (0, 0))

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    def draw_dialogue_box(self):
        # Scaled for 1280x720
        box_surface = pygame.Surface((1067, 267), pygame.SRCALPHA)
        box_surface.set_alpha(self.box_alpha)
        pygame.draw.rect(box_surface, (30, 30, 60, 220), (0, 0, 1067, 267), border_radius=13)
        pygame.draw.rect(box_surface, (100, 100, 200, 255), (0, 0, 1067, 267), 4, border_radius=13)
        self.screen.blit(box_surface, (107, 400))
        
        if self.box_alpha >= 255 and self.dialogues:
            # Playback mode
            dialogue = self.dialogues[self.current_dialogue]
            speaker_color = (100, 255, 100) if dialogue["speaker"] == "Hero" else (200, 150, 255)
            speaker_text = self.title_font.render(dialogue["speaker"], True, speaker_color)
            self.screen.blit(speaker_text, (133, 420))
            
            lines = self.wrap_text(self.displayed_text, 1000)
            y_offset = 487
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (133, y_offset))
                y_offset += 53

    def update_text(self):
        if self.char_index < len(self.full_text):
            self.char_index += self.text_speed
            self.displayed_text = self.full_text[:self.char_index]

    def next_dialogue(self):
        if self.current_dialogue < len(self.dialogues) - 1:
            self.current_dialogue += 1
            self.full_text = self.dialogues[self.current_dialogue]["text"]
            self.displayed_text = ""
            self.char_index = 0
        else:
            return 'quit'
        return None

    def run(self):
        if self.dialogues:
            self.full_text = self.dialogues[self.current_dialogue]["text"]
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.char_index < len(self.full_text):
                            self.char_index = len(self.full_text)
                            self.displayed_text = self.full_text
                        else:
                            result = self.next_dialogue()
                            if result == 'quit':
                                return 'menu'
                    elif event.key == pygame.K_ESCAPE:
                        return 'menu'
            
            if self.fading_in and self.box_alpha < 255:
                self.box_alpha += 5
                if self.box_alpha >= 255:
                    self.box_alpha = 255
                    self.fading_in = False
            
            if not self.fading_in:
                self.update_text()
            
            # Draw gradient background (scaled for 1280x720)
            self.screen.fill((20, 20, 40))
            for i in range(self.height):
                color = (min(255, 20 + i // 24), min(255, 20 + i // 36), min(255, 40 + i // 18))
                pygame.draw.line(self.screen, color, (0, i), (self.width, i))
            
            # Draw ground
            pygame.draw.rect(self.screen, (40, 60, 40), (0, 360, self.width, 360))
            
            hero_head = self.draw_hero_sprite()
            wizard_head = self.draw_wizard_sprite()
            
            # Draw dynamic mask for current speaker
            self.draw_speaker_mask(hero_head, wizard_head)
            
            self.draw_dialogue_box()
            
            # Scale and blit to display (centered with black bars if needed)
            self.display_screen.fill((0, 0, 0))  # Black bars
            scaled_surface = pygame.transform.scale(
                self.screen,
                (int(self.width * self.scale), int(self.height * self.scale))
            )
            self.display_screen.blit(scaled_surface, (self.offset_x, self.offset_y))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return 'quit'

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Textbox with Character Mask')
    textbox = Textbox(screen)
    textbox.run()
    pygame.quit()
    sys.exit()