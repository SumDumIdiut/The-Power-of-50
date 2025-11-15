import pygame
import sys
import math

class Textbox:
    def __init__(self, screen):
        self.display_screen = screen
        screen_width, screen_height = screen.get_size()
        
        # Fixed game dimensions (1920x1080)
        self.width = 1920
        self.height = 1080
        
        # Create a surface at fixed resolution
        self.screen = pygame.Surface((self.width, self.height))
        
        # Calculate scale to fit display (maintain aspect ratio)
        scale_x = screen_width / self.width
        scale_y = screen_height / self.height
        self.scale = min(scale_x, scale_y)
        
        # Calculate offset to center the game
        self.offset_x = (screen_width - self.width * self.scale) // 2
        self.offset_y = (screen_height - self.height * self.scale) // 2
        
        self.font = pygame.font.Font(None, 72)  # Scaled up for 1920x1080
        self.title_font = pygame.font.Font(None, 90)  # Scaled up for 1920x1080
        self.clock = pygame.time.Clock()
        
        # Dialogue sequences
        self.dialogues = [
            {"speaker": "Hero", "text": "I've been searching for the ancient artifact for weeks now."},
            {"speaker": "Wizard", "text": "The artifact you seek lies deep within the Crystal Caverns."},
            {"speaker": "Hero", "text": "Crystal Caverns? That sounds dangerous. What should I expect?"},
            {"speaker": "Wizard", "text": "Beware of the shadow creatures that guard the entrance."},
            {"speaker": "Hero", "text": "EXP is gay"},
        ]
        
        self.current_dialogue = 0
        self.displayed_text = ""
        self.full_text = ""
        self.char_index = 0
        self.text_speed = 2  # Characters per frame
        self.box_alpha = 0
        self.fading_in = True
        
        # Hero animation (scaled for 1920x1080)
        self.hero_y_offset = 0
        self.hero_animation_time = 0
        self.hero_base_y = 300
        
    def draw_hero_sprite(self):
        """Draw the hero sprite (snake-like robot with eyes)"""
        is_hero_speaking = self.dialogues[self.current_dialogue]["speaker"] == "Hero"
        
        if is_hero_speaking:
            self.hero_animation_time += 0.15
            self.hero_y_offset = math.sin(self.hero_animation_time) * 30
        else:
            self.hero_y_offset = 0
            self.hero_animation_time = 0
        
        hero_x = 300  # Scaled for 1920x1080
        hero_y = self.hero_base_y + self.hero_y_offset
        
        # Draw body (scaled)
        segment_size = 60
        num_segments = 4
        for i in range(num_segments):
            y_pos = hero_y + (i * segment_size)
            green_val = max(50, 200 - (i * 30))  # Prevent negative values
            pygame.draw.rect(self.screen, (0, green_val, 0), (hero_x, y_pos, 80, segment_size))
            pygame.draw.rect(self.screen, (0, max(0, green_val - 50), 0), (hero_x, y_pos, 80, segment_size), 6)
            pygame.draw.circle(self.screen, (150, 150, 150), (hero_x + 20, int(y_pos + 20)), 6)
            pygame.draw.circle(self.screen, (150, 150, 150), (hero_x + 60, int(y_pos + 20)), 6)
        
        # Head
        head_rect = pygame.Rect(hero_x - 10, int(hero_y - 20), 100, 80)
        pygame.draw.rect(self.screen, (0, 220, 0), head_rect, border_radius=20)
        pygame.draw.rect(self.screen, (0, 170, 0), head_rect, 6, border_radius=20)
        
        # Eyes
        eye_y = int(hero_y + 10)
        for x_offset in (20, 60):
            pygame.draw.circle(self.screen, (255, 255, 255), (hero_x + x_offset, eye_y), 16)
            pygame.draw.circle(self.screen, (0, 0, 255), (hero_x + x_offset, eye_y), 10)
            pygame.draw.circle(self.screen, (0, 0, 0), (hero_x + x_offset, eye_y), 6)
        
        # Antenna
        pygame.draw.line(self.screen, (200, 200, 0), (hero_x + 40, int(hero_y - 20)), (hero_x + 40, int(hero_y - 50)), 6)
        pygame.draw.circle(self.screen, (255, 0, 0), (hero_x + 40, int(hero_y - 50)), 10)
        
        # Glow effect
        if is_hero_speaking:
            glow_surface = pygame.Surface((160, 320), pygame.SRCALPHA)
            glow_alpha = int(abs(math.sin(self.hero_animation_time * 2)) * 50)
            pygame.draw.circle(glow_surface, (0, 255, 0, glow_alpha), (80, 160), 120)
            self.screen.blit(glow_surface, (hero_x - 40, int(hero_y - 40)))
        
        # Return head position for mask
        return (hero_x + 40, int(hero_y))

    def draw_wizard_sprite(self):
        """Draw the wizard sprite (scaled for 1920x1080)"""
        is_wizard_speaking = self.dialogues[self.current_dialogue]["speaker"] == "Wizard"
        
        wizard_x = 1500  # Scaled for 1920x1080
        wizard_y = 300
        
        if is_wizard_speaking:
            wizard_y += math.sin(pygame.time.get_ticks() * 0.003) * 16
        
        wizard_y = int(wizard_y)
        
        # Robe (scaled)
        robe_points = [(wizard_x + 40, wizard_y + 80), (wizard_x, wizard_y + 240), (wizard_x + 80, wizard_y + 240)]
        pygame.draw.polygon(self.screen, (60, 0, 120), robe_points)
        pygame.draw.polygon(self.screen, (100, 0, 200), robe_points, 6)
        
        # Head
        pygame.draw.circle(self.screen, (220, 180, 140), (wizard_x + 40, wizard_y + 50), 30)
        
        # Hat
        hat_points = [(wizard_x + 40, wizard_y - 40), (wizard_x + 10, wizard_y + 20), (wizard_x + 70, wizard_y + 20)]
        pygame.draw.polygon(self.screen, (60, 0, 120), hat_points)
        pygame.draw.polygon(self.screen, (100, 0, 200), hat_points, 4)
        pygame.draw.circle(self.screen, (255, 215, 0), (wizard_x + 36, wizard_y), 6)
        
        # Beard
        pygame.draw.polygon(self.screen, (200, 200, 200), [(wizard_x + 40, wizard_y + 60), (wizard_x + 20, wizard_y + 90), (wizard_x + 60, wizard_y + 90)])
        
        # Eyes
        for eye_x in (wizard_x + 30, wizard_x + 50):
            pygame.draw.circle(self.screen, (255, 255, 255), (eye_x, wizard_y + 44), 6)
            pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, wizard_y + 44), 4)
        
        # Staff
        pygame.draw.line(self.screen, (139, 69, 19), (wizard_x + 70, wizard_y + 100), (wizard_x + 90, wizard_y + 220), 8)
        
        # Magic orb
        if is_wizard_speaking:
            orb_glow = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100)
            pygame.draw.circle(self.screen, (100 + orb_glow, 100, 255), (wizard_x + 90, wizard_y + 90), 16)
        else:
            pygame.draw.circle(self.screen, (150, 100, 255), (wizard_x + 90, wizard_y + 90), 16)
        
        # Return head position for mask
        return (wizard_x + 40, wizard_y + 20)

    def draw_speaker_mask(self, hero_head, wizard_head):
        """Draw spotlight mask around current speaker (scaled for 1920x1080)"""
        speaker = self.dialogues[self.current_dialogue]["speaker"]
        
        if speaker == "Hero":
            center = (hero_head[0], hero_head[1])
            color = (0, 255, 100, 100)
        else:
            center = (wizard_head[0], wizard_head[1])
            color = (150, 100, 255, 100)
        
        mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 150))
        pygame.draw.circle(mask_surface, (0, 0, 0, 0), center, 160)  # Scaled radius
        pygame.draw.circle(mask_surface, color, center, 160, 8)  # Scaled border
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
        # Scaled for 1920x1080
        box_surface = pygame.Surface((1600, 400), pygame.SRCALPHA)
        box_surface.set_alpha(self.box_alpha)
        pygame.draw.rect(box_surface, (30, 30, 60, 220), (0, 0, 1600, 400), border_radius=20)
        pygame.draw.rect(box_surface, (100, 100, 200, 255), (0, 0, 1600, 400), 6, border_radius=20)
        self.screen.blit(box_surface, (160, 600))
        
        if self.box_alpha >= 255:
            dialogue = self.dialogues[self.current_dialogue]
            speaker_color = (100, 255, 100) if dialogue["speaker"] == "Hero" else (200, 150, 255)
            speaker_text = self.title_font.render(dialogue["speaker"], True, speaker_color)
            self.screen.blit(speaker_text, (200, 630))
            
            lines = self.wrap_text(self.displayed_text, 1500)
            y_offset = 730
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (200, y_offset))
                y_offset += 80
            
            if self.char_index >= len(self.full_text):
                indicator_font = pygame.font.Font(None, 48)
                msg = "Press SPACE to continue..." if self.current_dialogue < len(self.dialogues) - 1 else "Press ESC to quit"
                indicator = indicator_font.render(msg, True, (200, 200, 200))
                self.screen.blit(indicator, (1200, 920))

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
                                running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            if self.fading_in and self.box_alpha < 255:
                self.box_alpha += 5
                if self.box_alpha >= 255:
                    self.box_alpha = 255
                    self.fading_in = False
            
            if not self.fading_in:
                self.update_text()
            
            # Draw gradient background (scaled for 1920x1080)
            self.screen.fill((20, 20, 40))
            for i in range(self.height):
                color = (min(255, 20 + i // 36), min(255, 20 + i // 54), min(255, 40 + i // 27))
                pygame.draw.line(self.screen, color, (0, i), (self.width, i))
            
            # Draw ground
            pygame.draw.rect(self.screen, (40, 60, 40), (0, 540, self.width, 540))
            
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