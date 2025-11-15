"""
Main menu system for the game
"""
import pygame
import random
import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, 50)
        self.options = [
            {'text': 'Snake Game', 'action': 'snake'},
            {'text': 'Shooter Game', 'action': 'shooter'},
            {'text': 'Tower Defense', 'action': 'tower'},
            {'text': 'Portal Animation', 'action': 'portal'},
            {'text': 'Dialogue Box', 'action': 'dialogue'},
            {'text': 'Quit', 'action': 'quit'}
        ]
        self.selected = 0
        self.camera_x = 0
        self.target_camera_x = 0
        
        # Load logo
        try:
            logo_path = resource_path(os.path.join("Assets", "Logo Test.png"))
            print(f"Attempting to load logo from: {logo_path}")
            print(f"File exists: {os.path.exists(logo_path)}")
            self.logo = pygame.image.load(logo_path)
            print(f"Logo loaded successfully: {self.logo.get_size()}")
            # Scale logo to fit screen width (larger)
            scale = self.height / 600
            logo_width = int(min(self.width * 0.8, 1200 * scale))
            aspect_ratio = self.logo.get_height() / self.logo.get_width()
            logo_height = int(logo_width * aspect_ratio)
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        except Exception as e:
            print(f"Failed to load logo: {e}")
            self.logo = None
    
    def draw_testing_station(self, x, station_type, is_selected):
        """Draw a testing station"""
        # Scale based on screen height
        scale = self.height / 600
        station_y = self.height - int(200 * scale)
        
        platform_width = int(300 * scale)
        platform_height = int(150 * scale)
        
        # Station platform
        platform_color = (80, 80, 100) if not is_selected else (100, 120, 150)
        pygame.draw.rect(self.screen, platform_color, 
                        (x - platform_width // 2, station_y, platform_width, platform_height), 
                        border_radius=int(10 * scale))
        pygame.draw.rect(self.screen, (120, 140, 180), 
                        (x - platform_width // 2, station_y, platform_width, platform_height), 
                        int(3 * scale), border_radius=int(10 * scale))
        
        # Control panel
        panel_width = int(200 * scale)
        panel_height = int(80 * scale)
        pygame.draw.rect(self.screen, (60, 60, 80), 
                        (x - panel_width // 2, station_y + int(20 * scale), panel_width, panel_height), 
                        border_radius=int(5 * scale))
        
        # Blinking lights
        import time
        blink = int(time.time() * 3) % 2
        light_colors = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]
        light_radius = int(5 * scale)
        for i, color in enumerate(light_colors):
            if blink or i == 1:
                light_x = x - int(80 * scale) + i * int(40 * scale)
                pygame.draw.circle(self.screen, color, (light_x, station_y + int(40 * scale)), light_radius)
        
        # Screen/monitor
        monitor_width = int(160 * scale)
        monitor_height = int(20 * scale)
        pygame.draw.rect(self.screen, (20, 40, 60), 
                        (x - monitor_width // 2, station_y + int(70 * scale), monitor_width, monitor_height), 
                        border_radius=int(3 * scale))
        if is_selected:
            pygame.draw.rect(self.screen, (100, 200, 255), 
                           (x - monitor_width // 2 + int(5 * scale), station_y + int(73 * scale), 
                            monitor_width - int(10 * scale), monitor_height - int(6 * scale)))
        
        # Station label
        label_font = pygame.font.Font(None, int(28 * scale))
        label_text = label_font.render(station_type, True, (200, 200, 220))
        label_rect = label_text.get_rect(center=(x, station_y + int(120 * scale)))
        self.screen.blit(label_text, label_rect)
        
        # Scientist (simple figure)
        if is_selected:
            head_radius = int(15 * scale)
            body_width = int(24 * scale)
            body_height = int(30 * scale)
            
            # Head
            pygame.draw.circle(self.screen, (255, 220, 180), (x, station_y - int(40 * scale)), head_radius)
            # Lab coat
            pygame.draw.rect(self.screen, (240, 240, 250), 
                           (x - body_width // 2, station_y - int(25 * scale), body_width, body_height))
            # Arms
            arm_thickness = int(3 * scale)
            pygame.draw.line(self.screen, (255, 220, 180), 
                           (x - body_width // 2, station_y - int(20 * scale)), 
                           (x - int(25 * scale), station_y - int(5 * scale)), arm_thickness)
            pygame.draw.line(self.screen, (255, 220, 180), 
                           (x + body_width // 2, station_y - int(20 * scale)), 
                           (x + int(25 * scale), station_y - int(5 * scale)), arm_thickness)
    
    def draw_background(self):
        # Ship interior background
        self.screen.fill((30, 35, 50))
        
        # Scale based on screen height
        scale = self.height / 600
        floor_height = int(50 * scale)
        ceiling_height = int(50 * scale)
        
        # Floor
        floor_y = self.height - floor_height
        pygame.draw.rect(self.screen, (40, 45, 60), (0, floor_y, self.width, floor_height))
        pygame.draw.line(self.screen, (60, 65, 80), (0, floor_y), (self.width, floor_y), int(2 * scale))
        
        # Ceiling
        pygame.draw.rect(self.screen, (25, 30, 45), (0, 0, self.width, ceiling_height))
        pygame.draw.line(self.screen, (50, 55, 70), (0, ceiling_height), (self.width, ceiling_height), int(2 * scale))
        
        # Ceiling lights (scaled)
        scale = self.height / 600
        light_spacing = int(150 * scale)
        light_width = int(60 * scale)
        light_height = int(20 * scale)
        beam_width = int(80 * scale)
        beam_height = int(200 * scale)
        
        num_lights = int(self.width / light_spacing) + 2
        for i in range(num_lights):
            light_x = int(100 * scale) + i * light_spacing - int(self.camera_x * 0.5) % light_spacing
            if -50 < light_x < self.width + 50:
                pygame.draw.rect(self.screen, (200, 220, 255), 
                               (light_x - light_width // 2, int(10 * scale), light_width, light_height), 
                               border_radius=int(5 * scale))
                # Light beam
                light_surf = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
                pygame.draw.polygon(light_surf, (200, 220, 255, 30), 
                                  [(beam_width // 2, 0), (0, beam_height), (beam_width, beam_height)])
                self.screen.blit(light_surf, (light_x - beam_width // 2, int(30 * scale)))
        
        # Wall panels (scaled)
        scale = self.height / 600
        panel_spacing = int(200 * scale)
        panel_width = int(180 * scale)
        ceiling_height = int(50 * scale)
        
        num_panels = int(self.width / panel_spacing) + 2
        for i in range(num_panels):
            panel_x = i * panel_spacing - int(self.camera_x * 0.3) % panel_spacing
            if -panel_spacing < panel_x < self.width + panel_spacing:
                pygame.draw.rect(self.screen, (35, 40, 55), 
                               (panel_x, ceiling_height, panel_width, self.height - ceiling_height - int(50 * scale)))
                pygame.draw.rect(self.screen, (50, 55, 70), 
                               (panel_x, ceiling_height, panel_width, self.height - ceiling_height - int(50 * scale)), 
                               int(2 * scale))
        
        # Draw testing stations (scaled spacing)
        scale = self.height / 600
        station_spacing = int(600 * scale)
        for i, option in enumerate(self.options):
            station_x = self.width // 2 + i * station_spacing - int(self.camera_x)
            if -300 < station_x < self.width + 300:
                self.draw_testing_station(station_x, option['text'], i == self.selected)
    
    def display_menu(self):
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.selected = (self.selected - 1) % len(self.options)
                        scale = self.height / 600
                        self.target_camera_x = self.selected * int(600 * scale)
                    elif event.key == pygame.K_RIGHT:
                        self.selected = (self.selected + 1) % len(self.options)
                        scale = self.height / 600
                        self.target_camera_x = self.selected * int(600 * scale)
                    elif event.key == pygame.K_RETURN:
                        return self.options[self.selected]['action']
            
            # Smooth camera movement
            self.camera_x += (self.target_camera_x - self.camera_x) * 0.1
            
            self.draw_background()
            
            # Draw logo at top
            if self.logo:
                scale = self.height / 600
                logo_y = int(120 * scale)
                logo_rect = self.logo.get_rect(center=(self.width // 2, logo_y))
                self.screen.blit(self.logo, logo_rect)
            
            # Draw instructions
            inst_font = pygame.font.Font(None, 28)
            inst_text = inst_font.render('← → Navigate  |  ENTER Select', True, (150, 170, 200))
            inst_rect = inst_text.get_rect(center=(self.width // 2, self.height - 30))
            self.screen.blit(inst_text, inst_rect)
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == '__main__':
    import sys
    import os
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import from new structure
    from games.snake.snake_game import SnakeGame
    from games.shooter.shooter_game import ShooterGame
    from games.tower_defense.tower_defense_game import TowerDefenseGame
    from Utils.portal import PortalAnimation
    from Utils.textbox import Textbox
    
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Dev Menu')
    
    while True:
        menu = MainMenu(screen)
        action = menu.display_menu()
        
        if action == 'quit':
            break
        elif action == 'snake':
            game = SnakeGame(screen)
            result = game.run()
            if result == 'quit':
                break
        elif action == 'dialogue':
            textbox = Textbox(screen)
            result = textbox.run()
            if result == 'quit':
                break
        elif action == 'portal':
            portal = PortalAnimation(screen)
            result = portal.run()
            if result == 'quit':
                break
        elif action == 'shooter':
            shooter = ShooterGame(screen)
            result = shooter.run()
            if result == 'quit':
                break
        elif action == 'tower':
            tower = TowerDefenseGame(screen)
            result = tower.run()
            if result == 'quit':
                break
    
    pygame.quit()
    sys.exit()
