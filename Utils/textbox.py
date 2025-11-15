import pygame
import sys
import math

class Textbox:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = 800, 600
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 40)
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
        
        # Hero animation
        self.hero_y_offset = 0
        self.hero_animation_time = 0
        self.hero_base_y = 150
        
    def draw_hero_sprite(self):
        """Draw the hero sprite (snake-like robot with eyes)"""
        is_hero_speaking = self.dialogues[self.current_dialogue]["speaker"] == "Hero"
        
        if is_hero_speaking:
            self.hero_animation_time += 0.15
            self.hero_y_offset = math.sin(self.hero_animation_time) * 15
        else:
            self.hero_y_offset = 0
            self.hero_animation_time = 0
        
        hero_x = 150
        hero_y = self.hero_base_y + self.hero_y_offset
        
        # Draw body
        segment_size = 30
        num_segments = 4
        for i in range(num_segments):
            y_pos = hero_y + (i * segment_size)
            green_val = max(50, 200 - (i * 30))  # Prevent negative values
            pygame.draw.rect(self.screen, (0, green_val, 0), (hero_x, y_pos, 40, segment_size))
            pygame.draw.rect(self.screen, (0, max(0, green_val - 50), 0), (hero_x, y_pos, 40, segment_size), 3)
            pygame.draw.circle(self.screen, (150, 150, 150), (hero_x + 10, int(y_pos + 10)), 3)
            pygame.draw.circle(self.screen, (150, 150, 150), (hero_x + 30, int(y_pos + 10)), 3)
        
        # Head
        head_rect = pygame.Rect(hero_x - 5, int(hero_y - 10), 50, 40)
        pygame.draw.rect(self.screen, (0, 220, 0), head_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 170, 0), head_rect, 3, border_radius=10)
        
        # Eyes
        eye_y = int(hero_y + 5)
        for x_offset in (10, 30):
            pygame.draw.circle(self.screen, (255, 255, 255), (hero_x + x_offset, eye_y), 8)
            pygame.draw.circle(self.screen, (0, 0, 255), (hero_x + x_offset, eye_y), 5)
            pygame.draw.circle(self.screen, (0, 0, 0), (hero_x + x_offset, eye_y), 3)
        
        # Antenna
        pygame.draw.line(self.screen, (200, 200, 0), (hero_x + 20, int(hero_y - 10)), (hero_x + 20, int(hero_y - 25)), 3)
        pygame.draw.circle(self.screen, (255, 0, 0), (hero_x + 20, int(hero_y - 25)), 5)
        
        # Glow effect
        if is_hero_speaking:
            glow_surface = pygame.Surface((80, 160), pygame.SRCALPHA)
            glow_alpha = int(abs(math.sin(self.hero_animation_time * 2)) * 50)
            pygame.draw.circle(glow_surface, (0, 255, 0, glow_alpha), (40, 80), 60)
            self.screen.blit(glow_surface, (hero_x - 20, int(hero_y - 20)))
        
        # Return head position for mask
        return (hero_x + 20, int(hero_y))

    def draw_wizard_sprite(self):
        """Draw the wizard sprite"""
        is_wizard_speaking = self.dialogues[self.current_dialogue]["speaker"] == "Wizard"
        
        wizard_x = 600
        wizard_y = 150
        
        if is_wizard_speaking:
            wizard_y += math.sin(pygame.time.get_ticks() * 0.003) * 8
        
        wizard_y = int(wizard_y)
        
        # Robe
        robe_points = [(wizard_x + 20, wizard_y + 40), (wizard_x, wizard_y + 120), (wizard_x + 40, wizard_y + 120)]
        pygame.draw.polygon(self.screen, (60, 0, 120), robe_points)
        pygame.draw.polygon(self.screen, (100, 0, 200), robe_points, 3)
        
        # Head
        pygame.draw.circle(self.screen, (220, 180, 140), (wizard_x + 20, wizard_y + 25), 15)
        
        # Hat
        hat_points = [(wizard_x + 20, wizard_y - 20), (wizard_x + 5, wizard_y + 10), (wizard_x + 35, wizard_y + 10)]
        pygame.draw.polygon(self.screen, (60, 0, 120), hat_points)
        pygame.draw.polygon(self.screen, (100, 0, 200), hat_points, 2)
        pygame.draw.circle(self.screen, (255, 215, 0), (wizard_x + 18, wizard_y), 3)
        
        # Beard
        pygame.draw.polygon(self.screen, (200, 200, 200), [(wizard_x + 20, wizard_y + 30), (wizard_x + 10, wizard_y + 45), (wizard_x + 30, wizard_y + 45)])
        
        # Eyes
        for eye_x in (wizard_x + 15, wizard_x + 25):
            pygame.draw.circle(self.screen, (255, 255, 255), (eye_x, wizard_y + 22), 3)
            pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, wizard_y + 22), 2)
        
        # Staff
        pygame.draw.line(self.screen, (139, 69, 19), (wizard_x + 35, wizard_y + 50), (wizard_x + 45, wizard_y + 110), 4)
        
        # Magic orb
        if is_wizard_speaking:
            orb_glow = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100)
            pygame.draw.circle(self.screen, (100 + orb_glow, 100, 255), (wizard_x + 45, wizard_y + 45), 8)
        else:
            pygame.draw.circle(self.screen, (150, 100, 255), (wizard_x + 45, wizard_y + 45), 8)
        
        # Return head position for mask
        return (wizard_x + 20, wizard_y + 10)

    def draw_speaker_mask(self, hero_head, wizard_head):
        """Draw spotlight mask around current speaker"""
        speaker = self.dialogues[self.current_dialogue]["speaker"]
        
        if speaker == "Hero":
            center = (hero_head[0], hero_head[1])
            color = (0, 255, 100, 100)
        else:
            center = (wizard_head[0], wizard_head[1])
            color = (150, 100, 255, 100)
        
        mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 150))
        pygame.draw.circle(mask_surface, (0, 0, 0, 0), center, 80)
        pygame.draw.circle(mask_surface, color, center, 80, 4)
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
        box_surface = pygame.Surface((700, 200), pygame.SRCALPHA)
        box_surface.set_alpha(self.box_alpha)
        pygame.draw.rect(box_surface, (30, 30, 60, 220), (0, 0, 700, 200))
        pygame.draw.rect(box_surface, (100, 100, 200, 255), (0, 0, 700, 200), 3)
        self.screen.blit(box_surface, (50, 350))
        
        if self.box_alpha >= 255:
            dialogue = self.dialogues[self.current_dialogue]
            speaker_color = (100, 255, 100) if dialogue["speaker"] == "Hero" else (200, 150, 255)
            speaker_text = self.title_font.render(dialogue["speaker"], True, speaker_color)
            self.screen.blit(speaker_text, (70, 365))
            
            lines = self.wrap_text(self.displayed_text, 650)
            y_offset = 410
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (70, y_offset))
                y_offset += 35
            
            if self.char_index >= len(self.full_text):
                indicator_font = pygame.font.Font(None, 24)
                msg = "Press SPACE to continue..." if self.current_dialogue < len(self.dialogues) - 1 else "Press ESC to quit"
                indicator = indicator_font.render(msg, True, (200, 200, 200))
                self.screen.blit(indicator, (520, 520))

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
            
            # Draw gradient background
            self.screen.fill((20, 20, 40))
            for i in range(600):
                color = (min(255, 20 + i // 20), min(255, 20 + i // 30), min(255, 40 + i // 15))
                pygame.draw.line(self.screen, color, (0, i), (800, i))
            
            # Draw ground
            pygame.draw.rect(self.screen, (40, 60, 40), (0, 300, 800, 300))
            
            hero_head = self.draw_hero_sprite()
            wizard_head = self.draw_wizard_sprite()
            
            # Draw dynamic mask for current speaker
            self.draw_speaker_mask(hero_head, wizard_head)
            
            self.draw_dialogue_box()
            
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