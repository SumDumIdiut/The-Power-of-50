import pygame
import sys
import math
import random

class PortalAnimation:
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
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('segoeui', 36, bold=True)  # Scaled for 1280x720
        
        # Portal properties (scaled for 1280x720)
        self.portal_pos = (640, 360)  # Center of 1280x720
        self.portal_width = 160  # Oval width
        self.portal_height = 240  # Oval height
        self.rotation_angle = 0
        self.portal_active = True
        self.portal_closing = False
        self.portal_close_progress = 0
        
        # Particles for portal effect
        self.portal_particles = []
        
        # Colors
        self.portal_color = (150, 50, 255)  # Purple
        
        # Cubes
        self.cubes = []
        self.dragging_cube = None
        self.mouse_pos = (0, 0)
        
    def create_portal_particles(self, num_particles=3):
        """Create swirling particles around the portal"""
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            distance_x = random.uniform(self.portal_width * 0.5, self.portal_width * 0.7)
            distance_y = random.uniform(self.portal_height * 0.5, self.portal_height * 0.7)
            speed = random.uniform(0.03, 0.06)
            size = random.randint(2, 4)
            self.portal_particles.append({
                'angle': angle,
                'distance_x': distance_x,
                'distance_y': distance_y,
                'speed': speed,
                'size': size
            })
    
    def update_particles(self):
        """Update particle positions"""
        for particle in self.portal_particles:
            particle['angle'] += particle['speed']
            # Calculate position on oval
            x = self.portal_pos[0] + math.cos(particle['angle']) * particle['distance_x']
            y = self.portal_pos[1] + math.sin(particle['angle']) * particle['distance_y']
            particle['pos'] = (int(x), int(y))
    
    def spawn_cube(self, pos):
        """Spawn a new cube at the given position"""
        self.cubes.append({
            'pos': list(pos),
            'size': 53,  # Scaled for 1280x720
            'angle': 0,
            'being_pulled': False,
            'spiral_angle': 0,
            'spiral_distance': 0
        })
    
    def update_cubes(self):
        """Update cube physics and portal interaction"""
        for cube in self.cubes[:]:
            if cube == self.dragging_cube:
                continue
            
            # Calculate distance to portal
            dx = self.portal_pos[0] - cube['pos'][0]
            dy = self.portal_pos[1] - cube['pos'][1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if cube is close enough to be pulled (scaled)
            pull_threshold = 200  # Scaled for 1280x720
            if distance < pull_threshold and self.portal_active:
                cube['being_pulled'] = True
                
                # Start closing portal when cube gets close enough
                if distance < 107 and not self.portal_closing:
                    self.portal_closing = True
                
                # Calculate pull force (stronger when closer)
                pull_strength = 1.0 - (distance / pull_threshold)
                
                # Move cube in spiral toward portal
                if not cube.get('spiral_initialized'):
                    cube['spiral_angle'] = math.atan2(dy, dx)
                    cube['spiral_distance'] = distance
                    cube['spiral_initialized'] = True
                
                # Spiral motion (scaled)
                cube['spiral_angle'] += 0.15 * (1 + pull_strength)
                cube['spiral_distance'] -= 6 * pull_strength  # Scaled speed
                
                # Update position
                cube['pos'][0] = self.portal_pos[0] - math.cos(cube['spiral_angle']) * cube['spiral_distance']
                cube['pos'][1] = self.portal_pos[1] - math.sin(cube['spiral_angle']) * cube['spiral_distance']
                
                # Shrink cube (scaled)
                cube['size'] -= 1.6 * pull_strength
                cube['angle'] += 8 * pull_strength
                
                # Remove cube when it reaches the center (scaled)
                if cube['spiral_distance'] < 10 or cube['size'] < 6:
                    self.cubes.remove(cube)
            else:
                cube['being_pulled'] = False
    
    def draw_portal(self):
        """Draw an animated oval portal with TV/eye closing effect"""
        if not self.portal_active:
            return
        
        # Apply closing animation - vertical collapse with horizontal stretch (squish effect)
        if self.portal_closing:
            # Height collapses to create horizontal line (like eye closing)
            height = self.portal_height * (1 - self.portal_close_progress)
            # Width stretches slightly as it closes (squish effect)
            width = self.portal_width * (1 + self.portal_close_progress * 0.3)
        else:
            width = self.portal_width
            height = self.portal_height
        
        if height < 2:
            self.portal_active = False
            return
        
        # Draw outer glow layers (scaled)
        for i in range(5, 0, -1):
            glow_width = width + i * 16  # Scaled
            glow_height = height + i * 16  # Scaled
            alpha_color = tuple(int(c * (i / 5) * 0.4) for c in self.portal_color)
            rect = pygame.Rect(
                self.portal_pos[0] - glow_width // 2,
                self.portal_pos[1] - glow_height // 2,
                glow_width,
                glow_height
            )
            pygame.draw.ellipse(self.screen, alpha_color, rect, 6)  # Scaled border
        
        # Draw filled portal interior (dark purple/black)
        inner_rect = pygame.Rect(
            self.portal_pos[0] - width // 2,
            self.portal_pos[1] - height // 2,
            width,
            height
        )
        pygame.draw.ellipse(self.screen, (30, 10, 50), inner_rect)
        
        # Draw main portal oval border (scaled)
        pygame.draw.ellipse(self.screen, self.portal_color, inner_rect, 12)  # Scaled border
        
        # Draw inner swirl effect (only if portal is still open enough)
        if height > 40:  # Scaled threshold
            num_lines = 12
            for i in range(num_lines):
                angle = self.rotation_angle + (i * 2 * math.pi / num_lines)
                start_x = self.portal_pos[0] + math.cos(angle) * (width * 0.2)
                start_y = self.portal_pos[1] + math.sin(angle) * (height * 0.2)
                end_x = self.portal_pos[0] + math.cos(angle) * (width * 0.45)
                end_y = self.portal_pos[1] + math.sin(angle) * (height * 0.45)
                pygame.draw.line(self.screen, self.portal_color, (start_x, start_y), (end_x, end_y), 4)  # Scaled line width
        
        # Draw center glow (only if portal is still open enough)
        if height > 20:  # Scaled threshold
            center_size = min(width, height) * 0.15
            pygame.draw.ellipse(self.screen, (200, 150, 255), 
                              pygame.Rect(self.portal_pos[0] - center_size // 2,
                                        self.portal_pos[1] - center_size // 2,
                                        center_size, center_size))
    
    def draw_particles(self):
        """Draw all particles with fade out during closing"""
        # Don't draw particles if portal is fully closed
        if not self.portal_active:
            return
        
        for particle in self.portal_particles:
            if 'pos' in particle:
                # Fade out particles when portal is closing
                if self.portal_closing:
                    alpha = 1.0 - self.portal_close_progress
                    if alpha <= 0:
                        continue
                    color = tuple(int(c * alpha) for c in self.portal_color)
                else:
                    color = self.portal_color
                
                # Scaled particle size
                pygame.draw.circle(self.screen, color, 
                                 particle['pos'], particle['size'] * 2)
    
    def draw_cubes(self):
        """Draw all cubes with fade out when very close to center"""
        for cube in self.cubes:
            # Create rotated square
            size = cube['size']
            angle = cube['angle']
            cx, cy = cube['pos']
            
            # Calculate distance to portal center for fade effect
            dx = self.portal_pos[0] - cx
            dy = self.portal_pos[1] - cy
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Fade out cube when very close to center (scaled)
            if distance < 40:  # Scaled threshold
                alpha = distance / 40.0
                if alpha < 0.1:
                    continue  # Don't draw if too faded
            else:
                alpha = 1.0
            
            # Calculate corners of rotated square
            corners = []
            for i in range(4):
                corner_angle = angle + (i * math.pi / 2)
                x = cx + math.cos(corner_angle) * size / math.sqrt(2)
                y = cy + math.sin(corner_angle) * size / math.sqrt(2)
                corners.append((x, y))
            
            # Draw cube with gradient effect and alpha
            if cube['being_pulled']:
                color = tuple(int(c * alpha) for c in (100, 200, 255))  # Lighter when being pulled
                border_color = tuple(int(c * alpha) for c in (255, 255, 255))
            else:
                color = tuple(int(c * alpha) for c in (50, 150, 200))  # Normal blue
                border_color = tuple(int(c * alpha) for c in (255, 255, 255))
            
            pygame.draw.polygon(self.screen, color, corners)
            pygame.draw.polygon(self.screen, border_color, corners, 4)  # Scaled border
    
    def close_portal(self):
        """Start portal closing animation"""
        if self.portal_active and not self.portal_closing:
            self.portal_closing = True
    
    def run(self):
        # Initialize particles
        for _ in range(40):
            self.create_portal_particles()
        
        while True:
            display_mouse_pos = pygame.mouse.get_pos()
            # Scale mouse coordinates to game coordinates
            self.mouse_pos = (
                int((display_mouse_pos[0] - self.offset_x) / self.scale),
                int((display_mouse_pos[1] - self.offset_y) / self.scale)
            )
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        return 'menu'
                    elif event.key == pygame.K_c:
                        self.close_portal()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Only allow spawning/dragging if portal is active
                        if self.portal_active and not self.portal_closing:
                            # Check if clicking on existing cube
                            clicked_cube = None
                            for cube in self.cubes:
                                dx = cube['pos'][0] - self.mouse_pos[0]
                                dy = cube['pos'][1] - self.mouse_pos[1]
                                if abs(dx) < cube['size'] and abs(dy) < cube['size']:
                                    clicked_cube = cube
                                    break
                            
                            if clicked_cube:
                                self.dragging_cube = clicked_cube
                            else:
                                # Spawn new cube
                                self.spawn_cube(self.mouse_pos)
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_cube = None
            
            # Update dragging
            if self.dragging_cube:
                self.dragging_cube['pos'] = list(self.mouse_pos)
                self.dragging_cube['being_pulled'] = False
                self.dragging_cube['spiral_initialized'] = False
            
            # Update
            self.rotation_angle += 0.04
            self.update_particles()
            self.update_cubes()
            
            # Update portal closing
            if self.portal_closing:
                self.portal_close_progress += 0.03
                if self.portal_close_progress >= 1.0:
                    self.portal_close_progress = 1.0
                    self.portal_active = False
                    # Clear all cubes when portal is fully closed
                    self.cubes.clear()
            
            # Draw
            self.screen.fill((10, 10, 30))  # Dark background
            
            # Draw portal
            self.draw_portal()
            
            # Draw particles
            self.draw_particles()
            
            # Draw cubes
            self.draw_cubes()
            
            # Draw title
            title_text = self.font.render('PORTAL ANIMATION', True, (255, 255, 255))
            self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 60))
            
            # Draw instructions
            inst_font = pygame.font.Font(None, 48)
            inst_text = inst_font.render('Click to spawn cubes | Press C to close portal | ESC to exit', True, (200, 200, 200))
            self.screen.blit(inst_text, (self.width // 2 - inst_text.get_width() // 2, self.height - 80))
            
            # Scale and blit to display (centered with black bars if needed)
            self.display_screen.fill((0, 0, 0))  # Black bars
            scaled_surface = pygame.transform.scale(
                self.screen,
                (int(self.width * self.scale), int(self.height * self.scale))
            )
            self.display_screen.blit(scaled_surface, (self.offset_x, self.offset_y))
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS for smooth animation


def run(screen):
    """Entry point for the game"""
    animation = PortalAnimation(screen)
    return animation.run()
