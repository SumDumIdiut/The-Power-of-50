"""
Snake Game - Collect 50 apples
"""
import pygame
import sys
import random
import os

# Sprite file names (in assets folder)
SNAKE_HEAD_SPRITE = 'snake_head.png'
SNAKE_BODY_SPRITE = 'snake_body.png'
SNAKE_TAIL_SPRITE = 'snake_tail.png'
WALL_SPRITE = 'wall.png'
APPLE_SPRITE = 'apple.png'


class SnakeGame:
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
        
        # Fixed grid size (number of tiles)
        self.grid_tiles_x = 64  # More tiles for smaller size
        self.grid_tiles_y = 36  # More tiles for smaller size
        
        # Calculate tile size
        self.tile_width = self.width // self.grid_tiles_x
        self.tile_height = self.height // self.grid_tiles_y
        self.snake_size = self.tile_width
        
        # Start at grid-aligned position (center of grid)
        start_x = (self.grid_tiles_x // 2) * self.tile_width
        start_y = (self.grid_tiles_y // 2) * self.tile_height
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)  # Buffer for next move
        self.walls = []  # List of wall positions
        self.wall_segments = []  # Track connected wall segments
        self.apple_pos = self.generate_apple_pos()
        self.score = 0
        self.font = pygame.font.SysFont('segoeui', 28, bold=True)
        self.game_over = False
        self.won = False
        self.clock = pygame.time.Clock()
        
        # Pixel art font data
        self.pixel_font = {
            '0': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
            '1': [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[1,1,1]],
            '2': [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
            '3': [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
            '4': [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
            '5': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
            '6': [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
            '7': [[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
            '8': [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
            '9': [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]],
            'x': [[1,0,1],[1,0,1],[0,1,0],[1,0,1],[1,0,1]],
        }
        
        # Load and scale sprites (after pygame display is initialized)
        self.snake_head_sprite = None
        self.snake_body_sprite = None
        self.snake_tail_sprite = None
        self.wall_sprite = None
        self.apple_sprite = None
        
        assets_path = os.path.join(os.path.dirname(__file__), 'assets')
        
        try:
            head_path = os.path.join(assets_path, SNAKE_HEAD_SPRITE)
            if os.path.exists(head_path):
                head_img = pygame.image.load(head_path).convert_alpha()
                self.snake_head_sprite = pygame.transform.scale(head_img, (self.tile_width, self.tile_height))
        except Exception as e:
            pass  # Fallback to pygame drawing
        
        try:
            body_path = os.path.join(assets_path, SNAKE_BODY_SPRITE)
            if os.path.exists(body_path):
                body_img = pygame.image.load(body_path).convert_alpha()
                self.snake_body_sprite = pygame.transform.scale(body_img, (self.tile_width, self.tile_height))
        except Exception as e:
            pass  # Fallback to pygame drawing
        
        try:
            tail_path = os.path.join(assets_path, SNAKE_TAIL_SPRITE)
            if os.path.exists(tail_path):
                tail_img = pygame.image.load(tail_path).convert_alpha()
                self.snake_tail_sprite = pygame.transform.scale(tail_img, (self.tile_width, self.tile_height))
        except Exception as e:
            pass  # Fallback to pygame drawing
        
        try:
            wall_path = os.path.join(assets_path, WALL_SPRITE)
            if os.path.exists(wall_path):
                wall_img = pygame.image.load(wall_path).convert_alpha()
                self.wall_sprite = pygame.transform.scale(wall_img, (self.tile_width, self.tile_height))
        except Exception as e:
            pass  # Fallback to pygame drawing
        
        try:
            apple_path = os.path.join(assets_path, APPLE_SPRITE)
            if os.path.exists(apple_path):
                apple_img = pygame.image.load(apple_path).convert_alpha()
                self.apple_sprite = pygame.transform.scale(apple_img, (self.tile_width, self.tile_height))
        except Exception as e:
            pass  # Fallback to pygame drawing
    
    def generate_apple_pos(self):
        while True:
            x = random.randint(0, self.grid_tiles_x - 1) * self.tile_width
            y = random.randint(0, self.grid_tiles_y - 1) * self.tile_height
            pos = (x, y)
            if pos not in self.snake and pos not in self.walls:
                return pos
    
    def spawn_wall_block(self):
        """Spawn a wall block after collecting an apple"""
        # 50% chance to extend existing wall, 50% chance to start new wall
        if self.wall_segments and random.random() < 0.5:
            # Extend an existing wall segment
            segment = random.choice(self.wall_segments)
            last_block = segment[-1]
            
            # Try to add adjacent block (can turn corners)
            directions = [(0, self.tile_height), (0, -self.tile_height), 
                         (self.tile_width, 0), (-self.tile_width, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_pos = (last_block[0] + dx, last_block[1] + dy)
                # Check if position is valid
                if (0 <= new_pos[0] < self.width and 
                    0 <= new_pos[1] < self.height and
                    new_pos not in self.walls and 
                    new_pos not in self.snake and
                    new_pos != self.apple_pos):
                    self.walls.append(new_pos)
                    segment.append(new_pos)
                    return
        
        # Start a new wall segment
        attempts = 0
        while attempts < 50:
            x = random.randint(0, self.grid_tiles_x - 1) * self.tile_width
            y = random.randint(0, self.grid_tiles_y - 1) * self.tile_height
            pos = (x, y)
            
            if (pos not in self.snake and 
                pos not in self.walls and 
                pos != self.apple_pos):
                self.walls.append(pos)
                self.wall_segments.append([pos])
                return
            attempts += 1
    
    def draw_apple(self):
        ax = self.apple_pos[0]
        ay = self.apple_pos[1]
        
        if self.apple_sprite:
            # Use sprite if available
            self.screen.blit(self.apple_sprite, (ax, ay))
        else:
            # Fallback to pygame drawing
            radius = min(self.tile_width, self.tile_height) // 2
            pygame.draw.circle(self.screen, (255, 0, 0), 
                             (ax + self.tile_width // 2, 
                              ay + self.tile_height // 2), 
                             radius)
            pygame.draw.circle(self.screen, (255, 100, 100), 
                             (ax + self.tile_width // 2 - 3, 
                              ay + self.tile_height // 2 - 3), 
                             3)
            pygame.draw.rect(self.screen, (0, 150, 0), 
                            (ax + self.tile_width // 2 - 2, 
                             ay, 4, 5))
    
    def draw_pixel_char(self, char, x, y, pixel_size=3, color=(255, 255, 255)):
        if char not in self.pixel_font:
            return x
        
        pattern = self.pixel_font[char]
        for row_idx, row in enumerate(pattern):
            for col_idx, pixel in enumerate(row):
                if pixel:
                    pygame.draw.rect(self.screen, color,
                                   (x + col_idx * pixel_size, 
                                    y + row_idx * pixel_size,
                                    pixel_size, pixel_size))
        return x + len(pattern[0]) * pixel_size + pixel_size
    
    def draw_apple_sprite(self, x, y, size=12):
        """Draw a small apple sprite for the score display"""
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Apple body (red circle)
        pygame.draw.circle(self.screen, (255, 50, 50), (center_x, center_y), size // 2)
        
        # Highlight (lighter red)
        pygame.draw.circle(self.screen, (255, 120, 120), 
                         (center_x - size // 6, center_y - size // 6), size // 5)
        
        # Stem (brown/green)
        stem_width = max(2, size // 6)
        stem_height = max(3, size // 3)
        pygame.draw.rect(self.screen, (100, 180, 100), 
                        (center_x - stem_width // 2, y, stem_width, stem_height))
        
        # Leaf (green)
        leaf_points = [
            (center_x + stem_width // 2, y + stem_height // 2),
            (center_x + stem_width // 2 + size // 4, y),
            (center_x + stem_width // 2 + size // 3, y + stem_height // 2)
        ]
        pygame.draw.polygon(self.screen, (50, 200, 50), leaf_points)
    
    def draw_score(self):
        """Draw score with apple sprites: [apple] x / 50"""
        x_pos = 15
        y_pos = 15
        
        # Draw apple sprite (smaller)
        self.draw_apple_sprite(x_pos, y_pos, size=24)
        x_pos += 32
        
        # Draw score number
        score_str = str(self.score)
        for char in score_str:
            x_pos = self.draw_pixel_char(char, x_pos, y_pos + 4, pixel_size=4, color=(255, 255, 255))
        
        x_pos += 4
        
        # Draw "/"
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (x_pos + 2, y_pos + 4), (x_pos + 8, y_pos + 20), 3)
        x_pos += 14
        
        # Draw "50"
        for char in "50":
            x_pos = self.draw_pixel_char(char, x_pos, y_pos + 4, pixel_size=4, color=(255, 200, 100))
    
    def run(self):
        running = True
        move_timer = 0
        move_delay = 5  # Frames between moves (lower = faster) - INCREASED SPEED
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
                    if not self.game_over and not self.won:
                        # Buffer input - check against current direction to prevent 180° turns
                        if event.key == pygame.K_UP and self.direction != (0, 1):
                            self.next_direction = (0, -1)
                        elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                            self.next_direction = (0, 1)
                        elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                            self.next_direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                            self.next_direction = (1, 0)
                    elif self.game_over or self.won:
                        if event.key == pygame.K_RETURN:
                            if self.game_over:
                                return 'restart'
                            else:
                                return 'won'
            
            if not self.game_over and not self.won:
                move_timer += 1
                if move_timer >= move_delay:
                    move_timer = 0
                    
                    # Apply buffered direction at the moment of movement
                    self.direction = self.next_direction
                    
                    head_x, head_y = self.snake[0]
                    new_head = (head_x + self.direction[0] * self.tile_width,
                              head_y + self.direction[1] * self.tile_height)
                    
                    if (new_head[0] < 0 or new_head[0] >= self.width or
                        new_head[1] < 0 or new_head[1] >= self.height or
                        new_head in self.snake or new_head in self.walls):
                        self.game_over = True
                    else:
                        self.snake.insert(0, new_head)
                        
                        # Check if snake head is on same tile as apple
                        head_tile_x = new_head[0] // self.tile_width
                        head_tile_y = new_head[1] // self.tile_height
                        apple_tile_x = self.apple_pos[0] // self.tile_width
                        apple_tile_y = self.apple_pos[1] // self.tile_height
                        
                        if head_tile_x == apple_tile_x and head_tile_y == apple_tile_y:
                            self.score += 1
                            if self.score >= 50:
                                self.won = True
                            else:
                                # Add 3 walls after eating apple (MORE WALLS)
                                for _ in range(3):
                                    self.spawn_wall_block()
                                self.apple_pos = self.generate_apple_pos()
                        else:
                            self.snake.pop()
            
            self.screen.fill((15, 20, 35))
            
            # Draw subtle grid
            grid_color = (25, 30, 45)
            for x in range(0, self.width, self.tile_width):
                pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height))
            for y in range(0, self.height, self.tile_height):
                pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y))
            
            # Draw walls
            for wall_pos in self.walls:
                if self.wall_sprite:
                    # Use sprite if available
                    self.screen.blit(self.wall_sprite, wall_pos)
                else:
                    # Fallback to pygame drawing
                    # Dark gray wall with stone texture
                    pygame.draw.rect(self.screen, (60, 60, 70), 
                                   (wall_pos[0], wall_pos[1], self.tile_width, self.tile_height))
                    # Border for definition
                    pygame.draw.rect(self.screen, (80, 80, 90), 
                                   (wall_pos[0], wall_pos[1], self.tile_width, self.tile_height), 2)
                    # Inner shadow for depth
                    pygame.draw.rect(self.screen, (40, 40, 50), 
                                   (wall_pos[0] + 2, wall_pos[1] + 2, self.tile_width - 4, self.tile_height - 4), 1)
            
            # Draw snake on grid - connected segments
            for i, segment in enumerate(self.snake):
                is_head = (i == 0)
                is_tail = (i == len(self.snake) - 1)
                
                # Determine which sprite/color to use
                if is_head and self.snake_head_sprite:
                    # Use head sprite
                    self.screen.blit(self.snake_head_sprite, segment)
                elif is_tail and self.snake_tail_sprite:
                    # Use tail sprite
                    self.screen.blit(self.snake_tail_sprite, segment)
                elif not is_head and not is_tail and self.snake_body_sprite:
                    # Use body sprite
                    self.screen.blit(self.snake_body_sprite, segment)
                else:
                    # Fallback to pygame drawing
                    if is_head:
                        # Bright head
                        color = (80, 255, 80)
                        inner_color = (120, 255, 120)
                    else:
                        # Darker body - gradient from head to tail
                        fade = max(0.3, 1.0 - (i * 0.05))
                        color = (int(50 * fade), int(180 * fade), int(50 * fade))
                        inner_color = (int(70 * fade), int(200 * fade), int(70 * fade))
                    
                    # Draw connected segment with no gaps
                    pygame.draw.rect(self.screen, color, 
                                   (segment[0], segment[1], self.tile_width, self.tile_height))
                    
                    # Inner highlight for depth
                    pygame.draw.rect(self.screen, inner_color, 
                                   (segment[0] + 2, segment[1] + 2, self.tile_width - 4, self.tile_height - 4))
            
            self.draw_apple()
            self.draw_score()
            
            if self.game_over:
                text = self.font.render('GAME OVER - Press ENTER', True, (255, 50, 50))
                text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text, text_rect)
            elif self.won:
                text = self.font.render('YOU WIN! - Press ENTER', True, (100, 255, 100))
                text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text, text_rect)
            
            # Scale and blit to display (centered with black bars if needed)
            self.display_screen.fill((0, 0, 0))  # Black bars
            scaled_surface = pygame.transform.scale(
                self.screen,
                (int(self.width * self.scale), int(self.height * self.scale))
            )
            self.display_screen.blit(scaled_surface, (self.offset_x, self.offset_y))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return 'menu'


def run(screen):
    """Entry point for the game"""
    game = SnakeGame(screen)
    return game.run()
