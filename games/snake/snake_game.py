"""
Snake Game - Collect 50 apples
"""
import pygame
import sys
import random


class SnakeGame:
    def __init__(self, screen):
        self.screen = screen
        screen_width, screen_height = screen.get_size()
        
        # Fixed grid size (number of tiles)
        self.grid_tiles_x = 26  # Fixed number of tiles horizontally
        self.grid_tiles_y = 20  # Fixed number of tiles vertically
        
        # Calculate tile size to fill screen completely (non-square tiles OK)
        self.tile_width = screen_width // self.grid_tiles_x
        self.tile_height = screen_height // self.grid_tiles_y
        self.snake_size = self.tile_width  # Use for collision (use width as base)
        
        # Grid fills entire screen
        self.grid_width = self.grid_tiles_x * self.tile_width
        self.grid_height = self.grid_tiles_y * self.tile_height
        
        # No offset - fills screen
        self.offset_x = 0
        self.offset_y = 0
        
        # Use grid dimensions for gameplay
        self.width = self.grid_width
        self.height = self.grid_height
        
        # Start at grid-aligned position (center of grid)
        start_x = (self.width // 2 // self.snake_size) * self.snake_size
        start_y = (self.height // 2 // self.snake_size) * self.snake_size
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)  # Buffer for next move
        self.walls = []  # List of wall positions
        self.wall_segments = []  # Track connected wall segments
        self.apple_pos = self.generate_apple_pos()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
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
        
        # Draw apple sprite
        self.draw_apple_sprite(x_pos, y_pos, size=16)
        x_pos += 25
        
        # Draw score number (BIGGER UI)
        score_str = str(self.score)
        for char in score_str:
            x_pos = self.draw_pixel_char(char, x_pos, y_pos + 2, pixel_size=6, color=(255, 255, 255))
        
        x_pos += 5
        
        # Draw "/"
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (x_pos + 3, y_pos + 2), (x_pos + 12, y_pos + 28), 4)
        x_pos += 20
        
        # Draw "50"
        for char in "50":
            x_pos = self.draw_pixel_char(char, x_pos, y_pos + 2, pixel_size=6, color=(255, 200, 100))
    
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
                            return 'menu'
            
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
                        
                        if new_head == self.apple_pos:
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
                # Head is bright green, body/tail darker
                if i == 0:
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
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return 'menu'


def run(screen):
    """Entry point for the game"""
    game = SnakeGame(screen)
    return game.run()
