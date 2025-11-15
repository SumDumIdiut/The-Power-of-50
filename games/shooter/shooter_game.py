"""
Top-down shooter - Kill 50 enemies
Optimized with chunk-based rendering and dynamic loading
Uses tilemap system for procedural level generation
"""
import pygame
import math
import random
from .wall_renderer import WallRenderer
from .tilemap import Tilemap


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 5
        self.health = 1
        self.angle = 0
        self.shoot_direction = [0, -1]
        self.fire_rate = 30
        self.damage = 5
        self.multi_shot = 1
        self.bullet_bounce = 0
        # Special weapons
        self.has_orbital = False
        self.orbital_angle = 0
        self.has_dual_gun = False
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        angle = math.atan2(self.shoot_direction[1], self.shoot_direction[0])
        points = [
            (screen_x + math.cos(angle) * self.size,
             screen_y + math.sin(angle) * self.size),
            (screen_x + math.cos(angle + 2.5) * self.size * 0.6,
             screen_y + math.sin(angle + 2.5) * self.size * 0.6),
            (screen_x + math.cos(angle - 2.5) * self.size * 0.6,
             screen_y + math.sin(angle - 2.5) * self.size * 0.6)
        ]
        pygame.draw.polygon(screen, (50, 150, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        
        # Draw dual gun indicator
        if self.has_dual_gun:
            # Second barrel
            offset_angle = angle + math.pi / 2
            offset_x = math.cos(offset_angle) * 8
            offset_y = math.sin(offset_angle) * 8
            pygame.draw.line(screen, (255, 200, 0), 
                           (screen_x + offset_x, screen_y + offset_y),
                           (screen_x + offset_x + math.cos(angle) * 15, 
                            screen_y + offset_y + math.sin(angle) * 15), 3)
    
    def move(self, keys, chunk_manager):
        new_x, new_y = self.x, self.y
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x += self.speed
        
        # Check collisions with nearby walls
        nearby_walls = chunk_manager.get_nearby_walls(self.x, self.y)
        can_move_x = True
        can_move_y = True
        
        for wall in nearby_walls:
            if wall.collides(new_x, self.y, self.size):
                can_move_x = False
            if wall.collides(self.x, new_y, self.size):
                can_move_y = False
        
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y
        
        # Clamp player to world bounds (prevent going outside map)
        world_size = chunk_manager.world_size
        self.x = max(self.size, min(self.x, world_size - self.size))
        self.y = max(self.size, min(self.y, world_size - self.size))
    
    def update_aim(self, enemies, chunk_manager):
        # Auto-aim at nearest visible enemy
        nearest = None
        min_dist = float('inf')
        
        for enemy in enemies:
            if chunk_manager.has_line_of_sight(self.x, self.y, enemy.x, enemy.y):
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy
        
        if nearest:
            dx = nearest.x - self.x
            dy = nearest.y - self.y
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                self.shoot_direction = [dx/length, dy/length]
    
    def get_fire_rate_percent(self):
        """Get fire rate as percentage (lower cooldown = higher rate)"""
        base_rate = 30
        return int((base_rate / self.fire_rate) * 100)
    
    def update_orbital(self):
        """Update orbital weapon rotation"""
        if self.has_orbital:
            self.orbital_angle += 0.1
    
    def draw_orbital(self, screen, camera_x, camera_y):
        """Draw orbital weapon"""
        if not self.has_orbital:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw 3 orbiting saws
        for i in range(3):
            angle = self.orbital_angle + (i * math.pi * 2 / 3)
            orbit_radius = 50
            saw_x = screen_x + math.cos(angle) * orbit_radius
            saw_y = screen_y + math.sin(angle) * orbit_radius
            
            # Draw spinning saw
            pygame.draw.circle(screen, (255, 200, 0), (int(saw_x), int(saw_y)), 12)
            pygame.draw.circle(screen, (255, 100, 0), (int(saw_x), int(saw_y)), 12, 2)
            
            # Draw blades
            for j in range(4):
                blade_angle = angle * 5 + (j * math.pi / 2)
                blade_x1 = saw_x + math.cos(blade_angle) * 8
                blade_y1 = saw_y + math.sin(blade_angle) * 8
                blade_x2 = saw_x + math.cos(blade_angle + math.pi) * 8
                blade_y2 = saw_y + math.sin(blade_angle + math.pi) * 8
                pygame.draw.line(screen, (255, 255, 255), (blade_x1, blade_y1), (blade_x2, blade_y2), 2)


class Bullet:
    def __init__(self, x, y, direction, damage=10, bounces=0):
        self.x = x
        self.y = y
        inaccuracy = 0.15
        dx = direction[0] + random.uniform(-inaccuracy, inaccuracy)
        dy = direction[1] + random.uniform(-inaccuracy, inaccuracy)
        length = math.sqrt(dx*dx + dy*dy)
        self.direction = [dx/length, dy/length] if length > 0 else direction
        self.speed = 10
        self.size = 5
        self.damage = damage
        self.bounces_left = bounces
        self.max_bounces = bounces
        self.lifetime = 300  # Max 5 seconds lifetime
        self.last_bounce_frame = 0
    
    def update(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.lifetime -= 1
    
    def is_expired(self):
        return self.lifetime <= 0
    
    def bounce(self, wall, current_frame):
        if self.bounces_left <= 0:
            return False
        
        # Prevent multiple bounces in same frame
        if current_frame == self.last_bounce_frame:
            return True
        
        self.last_bounce_frame = current_frame
        
        center_x = wall.x + wall.width / 2
        center_y = wall.y + wall.height / 2
        dx = self.x - center_x
        dy = self.y - center_y
        
        if abs(dx / wall.width) > abs(dy / wall.height):
            self.direction[0] *= -1
        else:
            self.direction[1] *= -1
        
        self.bounces_left -= 1
        return True
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        color = (0, 255, 255) if self.max_bounces > 0 else (255, 255, 0)
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), self.size)


class Popup:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 60
        self.alpha = 255
    
    def update(self):
        self.lifetime -= 1
        self.y -= 1.5
        self.alpha = int(255 * (self.lifetime / 60))
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        font = pygame.font.Font(None, 32)
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        
        # Draw shadow
        shadow_surf = font.render(self.text, True, (0, 0, 0))
        shadow_surf.set_alpha(self.alpha // 2)
        screen.blit(shadow_surf, (int(screen_x) - text_surf.get_width() // 2 + 2, int(screen_y) + 2))
        
        screen.blit(text_surf, (int(screen_x) - text_surf.get_width() // 2, int(screen_y)))


class Enemy:
    def __init__(self, x, y, health=50, is_boss=False, is_final=False, enemy_type='normal', boss_id=0):
        self.x = x
        self.y = y
        self.is_boss = is_boss
        self.is_final = is_final
        self.boss_id = boss_id  # Which mini-boss (1-4)
        self.enemy_type = enemy_type  # 'normal', 'fast', 'tank', 'shooter'
        
        # Set stats based on type
        if is_boss:
            self.size = 40 if is_final else 30
            self.speed = random.uniform(0.5, 1.0)
        elif enemy_type == 'fast':
            self.size = 12
            self.speed = random.uniform(3.5, 5)
        elif enemy_type == 'tank':
            self.size = 20
            self.speed = random.uniform(0.8, 1.2)
        elif enemy_type == 'shooter':
            self.size = 15
            self.speed = random.uniform(1.0, 1.5)
        else:  # normal
            self.size = 15
            self.speed = random.uniform(1.5, 3)
        
        self.health = health
        self.max_health = health
        self.shoot_cooldown = 0
        # Shooter enemies fire much more often
        if enemy_type == 'shooter':
            self.shoot_rate = 90
        elif is_final:
            self.shoot_rate = 80
        elif is_boss:
            self.shoot_rate = 100
        else:
            self.shoot_rate = 200
        self.attack_pattern = 0
        self.pattern_timer = 0
        self.minion_spawn_timer = 0
    
    def update(self, player_x, player_y, chunk_manager, has_los):
        # Bosses always move, regular enemies only move if they see player
        if not has_los and not self.is_boss:
            return
        
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            new_x = self.x + (dx / dist) * self.speed
            new_y = self.y + (dy / dist) * self.speed
            
            nearby_walls = chunk_manager.get_nearby_walls(self.x, self.y)
            can_move_x = True
            can_move_y = True
            
            for wall in nearby_walls:
                if wall.collides(new_x, self.y, self.size):
                    can_move_x = False
                if wall.collides(self.x, new_y, self.size):
                    can_move_y = False
            
            if can_move_x:
                self.x = new_x
            if can_move_y:
                self.y = new_y
        
        if self.is_boss:
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            
            # Update attack pattern timer
            self.pattern_timer += 1
            if self.pattern_timer > 300:  # Change pattern every 5 seconds
                self.attack_pattern = (self.attack_pattern + 1) % (4 if self.is_final else 3)
                self.pattern_timer = 0
    
    def push_out_of_walls(self, chunk_manager):
        """Push enemy out of walls if spawned inside"""
        nearby_walls = chunk_manager.get_nearby_walls(self.x, self.y)
        
        for wall in nearby_walls:
            if wall.collides(self.x, self.y, self.size):
                # Try pushing in 8 directions
                directions = [
                    (1, 0), (-1, 0), (0, 1), (0, -1),
                    (1, 1), (-1, 1), (1, -1), (-1, -1)
                ]
                
                for dx, dy in directions:
                    push_distance = 0
                    max_push = 200
                    
                    while push_distance < max_push:
                        push_distance += 5
                        test_x = self.x + dx * push_distance
                        test_y = self.y + dy * push_distance
                        
                        # Check if this position is clear
                        is_clear = True
                        for check_wall in nearby_walls:
                            if check_wall.collides(test_x, test_y, self.size):
                                is_clear = False
                                break
                        
                        if is_clear:
                            self.x = test_x
                            self.y = test_y
                            return
                
                # If no direction works, teleport to random open position
                self.x, self.y = chunk_manager.get_random_open_position()
    
    def can_shoot(self):
        return (self.is_boss or self.enemy_type == 'shooter') and self.shoot_cooldown == 0
    
    def shoot(self, player_x, player_y):
        self.shoot_cooldown = self.shoot_rate
        bullets = []
        
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist == 0:
            return bullets
        
        direction = [dx / dist, dy / dist]
        angle_to_player = math.atan2(direction[1], direction[0])
        
        # Shooter enemy - simple 1 bullet
        if self.enemy_type == 'shooter' and not self.is_boss:
            bullets.append(EnemyBullet(self.x, self.y, direction))
            return bullets
        
        # Mini-boss attacks - each boss has unique patterns (OPTIMIZED)
        if self.is_boss and not self.is_final:
            if self.boss_id == 1:  # Boss 1: Spread master
                if self.attack_pattern == 0:
                    for i in range(5):
                        angle_offset = (i - 2) * 0.25
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 1:
                    for i in range(6):
                        angle = (i * math.pi * 2 / 6)
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 2:
                    for i in range(8):
                        angle_offset = (i - 3.5) * 0.2
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
            
            elif self.boss_id == 2:  # Boss 2: Spiral master
                if self.attack_pattern == 0:
                    for i in range(5):
                        angle = angle_to_player + (i * math.pi * 2 / 5) + self.pattern_timer * 0.1
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 1:
                    for i in range(3):
                        angle_offset = (i - 1) * 0.4
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 2:
                    for i in range(8):
                        angle = (i * math.pi * 2 / 8) + self.pattern_timer * 0.05
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
            
            elif self.boss_id == 3:  # Boss 3: Burst master
                if self.attack_pattern == 0:
                    for i in range(10):
                        angle_offset = (i - 4.5) * 0.15
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 1:
                    for i in range(4):
                        angle_offset = (i - 1.5) * 0.5
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 2:
                    for i in range(12):
                        angle_offset = (i - 5.5) * 0.12
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
            
            elif self.boss_id == 4:  # Boss 4: Chaos master
                if self.attack_pattern == 0:
                    for i in range(10):
                        angle = (i * math.pi * 2 / 10)
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 1:
                    for i in range(6):
                        angle_offset = (i - 2.5) * 0.35
                        angle = angle_to_player + angle_offset
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
                elif self.attack_pattern == 2:
                    for i in range(12):
                        angle = (i * math.pi * 2 / 12) + self.pattern_timer * 0.08
                        bullet_dir = [math.cos(angle), math.sin(angle)]
                        bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
        
        # Final boss - intense but optimized patterns
        elif self.is_final:
            if self.attack_pattern == 0:
                for i in range(12):
                    angle_offset = (i - 5.5) * 0.15
                    angle = angle_to_player + angle_offset
                    bullet_dir = [math.cos(angle), math.sin(angle)]
                    bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
            elif self.attack_pattern == 1:
                for i in range(10):
                    angle = (i * math.pi * 2 / 10) + self.pattern_timer * 0.1
                    bullet_dir = [math.cos(angle), math.sin(angle)]
                    bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
            elif self.attack_pattern == 2:
                for i in range(16):
                    angle_offset = (i - 7.5) * 0.12
                    angle = angle_to_player + angle_offset
                    bullet_dir = [math.cos(angle), math.sin(angle)]
                    bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
            elif self.attack_pattern == 3:
                for i in range(12):
                    angle = (i * math.pi * 2 / 12)
                    bullet_dir = [math.cos(angle), math.sin(angle)]
                    bullets.append(EnemyBullet(self.x, self.y, bullet_dir))
        
        return bullets
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Boss glow effect
        if self.is_boss:
            glow_color = (200, 0, 200) if self.is_final else (150, 0, 150)
            for i in range(3):
                glow_size = self.size + (3 - i) * 8
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*glow_color, 40), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (int(screen_x - glow_size), int(screen_y - glow_size)))
        
        # Color based on type
        if self.is_final:
            color = (200, 0, 200)
            border_color = (255, 0, 255)
        elif self.is_boss:
            color = (150, 0, 150)
            border_color = (100, 0, 100)
        elif self.enemy_type == 'fast':
            color = (255, 200, 50)
            border_color = (200, 150, 0)
        elif self.enemy_type == 'tank':
            color = (100, 100, 150)
            border_color = (50, 50, 100)
        elif self.enemy_type == 'shooter':
            color = (150, 255, 150)
            border_color = (100, 200, 100)
        else:
            color = (255, 50, 50)
            border_color = (150, 0, 0)
        
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), self.size)
        pygame.draw.circle(screen, border_color, (int(screen_x), int(screen_y)), self.size, 4 if self.is_final else (3 if self.is_boss else 2))
        
        # Health bar
        bar_width = min(100, 40 + int(self.max_health / 100) * 10)
        bar_height = 14
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - self.size - 16
        
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = (0, 255, 0) if self.health > 1 else (255, 200, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)


class EnemyBullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 6
        self.size = 6
    
    def update(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        pygame.draw.circle(screen, (255, 50, 50), (int(screen_x), int(screen_y)), self.size)


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.size = 20 if item_type in ['orbital', 'dual_gun'] else 15
        self.colors = {
            'firerate': (255, 100, 255),
            'multishot': (100, 200, 255),
            'damage': (255, 150, 50),
            'bounce': (0, 255, 255),
            'speed': (100, 255, 100),
            'orbital': (255, 200, 0),
            'dual_gun': (255, 100, 100)
        }
        self.names = {
            'firerate': '+Fire Rate',
            'multishot': '+Multi-Shot',
            'damage': '+Damage',
            'bounce': '+Bounce',
            'speed': '+Speed',
            'orbital': 'ORBITAL SAW',
            'dual_gun': 'DUAL GUN'
        }
        self.descriptions = {
            'firerate': 'Shoot Faster',
            'multishot': 'More Bullets',
            'damage': 'More Damage',
            'bounce': 'Bullets Bounce',
            'speed': 'Move Faster',
            'orbital': 'Spinning Saws!',
            'dual_gun': 'Double Shots!'
        }
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        color = self.colors.get(self.type, (255, 255, 255))
        
        # Draw glow effect
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 30), (self.size * 2, self.size * 2), self.size * 2)
        screen.blit(glow_surf, (int(screen_x - self.size * 2), int(screen_y - self.size * 2)))
        
        # Draw item
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), self.size)
        pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), self.size, 2)
        
        # Draw icon based on type
        if self.type == 'firerate':
            for i in range(3):
                pygame.draw.circle(screen, (255, 255, 255), (int(screen_x - 6 + i * 6), int(screen_y)), 2)
        elif self.type == 'multishot':
            for i in range(3):
                offset = (i - 1) * 5
                pygame.draw.polygon(screen, (255, 255, 255), [
                    (screen_x + offset, screen_y - 5),
                    (screen_x + offset - 3, screen_y + 2),
                    (screen_x + offset + 3, screen_y + 2)
                ])
        elif self.type == 'damage':
            pygame.draw.line(screen, (255, 255, 255), (screen_x - 5, screen_y + 5), (screen_x + 5, screen_y - 5), 3)
        elif self.type == 'bounce':
            points = [(screen_x - 6, screen_y + 4), (screen_x, screen_y - 6), (screen_x + 6, screen_y + 4)]
            pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
        
        # Draw description text below item
        desc_font = pygame.font.Font(None, 20)
        desc = self.descriptions.get(self.type, '')
        desc_text = desc_font.render(desc, True, (255, 255, 255))
        desc_rect = desc_text.get_rect(center=(screen_x, screen_y + self.size + 12))
        
        # Draw text background
        bg_rect = desc_rect.inflate(6, 2)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (0, 0, 0, 180), bg_surf.get_rect(), border_radius=3)
        screen.blit(bg_surf, bg_rect)
        
        screen.blit(desc_text, desc_rect)


class Wall:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        has_left=False,
        has_right=False,
        has_top=False,
        has_bottom=False,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Pre-calculated neighbor data for fast collision checks
        self.has_left = has_left
        self.has_right = has_right
        self.has_top = has_top
        self.has_bottom = has_bottom
        self.center_x = x + width / 2
        self.center_y = y + height / 2

    def collides(self, x, y, size):
        # Basic bounds check
        if not (
            self.x < x + size
            and self.x + self.width > x - size
            and self.y < y + size
            and self.y + self.height > y - size
        ):
            return False

        # Check collision based on which side and if that side is exposed
        collision_margin = size + 2

        # Check left side
        if x < self.center_x and abs(x - self.x) < collision_margin:
            if not self.has_left:  # Only collide if no neighbor on left
                return True

        # Check right side
        if x > self.center_x and abs(x - (self.x + self.width)) < collision_margin:
            if not self.has_right:  # Only collide if no neighbor on right
                return True

        # Check top side
        if y < self.center_y and abs(y - self.y) < collision_margin:
            if not self.has_top:  # Only collide if no neighbor on top
                return True

        # Check bottom side
        if y > self.center_y and abs(y - (self.y + self.height)) < collision_margin:
            if not self.has_bottom:  # Only collide if no neighbor on bottom
                return True

        # No collision on sides with neighbors
        return False
    
    def is_visible(self, camera_x, camera_y, screen_width, screen_height):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        buffer = 50
        return (screen_x + self.width > -buffer and screen_x < screen_width + buffer and
                screen_y + self.height > -buffer and screen_y < screen_height + buffer)
    
    # Drawing is now handled by WallRenderer


class ChunkManager:
    def __init__(self, world_size, chunk_size=500):
        self.world_size = world_size
        self.chunk_size = chunk_size
        self.all_walls = []
        self.wall_chunks = {}
        self.loaded_chunks = set()
        self.tilemap = Tilemap(tile_size=40)
        self.rooms = []
    
    def generate_map(self):
        """Generate open dungeon layout using tilemap system"""
        tile_size = self.tilemap.tile_size
        grid_width = self.world_size // tile_size
        grid_height = self.world_size // tile_size
        
        # Start by placing tiles everywhere (all walls) - WITHOUT updating each time
        for x in range(grid_width):
            for y in range(grid_height):
                self.tilemap.place_tile(x, y, update=False)
        
        # Create large open rooms
        rooms = []
        center_x, center_y = grid_width // 2, grid_height // 2
        start_room = (center_x - 25, center_y - 25, 50, 50)  # Larger starting room
        rooms.append(start_room)
        
        # Generate 20 large rooms with minimum 6 tile spacing
        for _ in range(20):
            for attempt in range(50):
                w = random.randint(25, 45)  # Much larger rooms
                h = random.randint(25, 45)
                x = random.randint(5, grid_width - w - 5)
                y = random.randint(5, grid_height - h - 5)
                
                overlap = False
                for rx, ry, rw, rh in rooms:
                    # Minimum 6 tiles padding for 3-tile thick walls
                    if not (
                        x + w + 6 < rx
                        or x - 6 > rx + rw
                        or y + h + 6 < ry
                        or y - 6 > ry + rh
                    ):
                        overlap = True
                        break
                
                if not overlap:
                    rooms.append((x, y, w, h))
                    break
        
        # Store room positions
        self.rooms = [
            (x * tile_size, y * tile_size, w * tile_size, h * tile_size)
            for x, y, w, h in rooms
        ]
        
        # Carve out rooms (remove tiles) - WITHOUT updating each time
        # But ensure we leave at least 3 tiles of wall thickness
        for x, y, w, h in rooms:
            for rx in range(x, x + w):
                for ry in range(y, y + h):
                    if 0 <= rx < grid_width and 0 <= ry < grid_height:
                        self.tilemap.remove_tile(rx, ry, update=False)
        
        # Connect rooms with wide corridors
        for i in range(len(rooms) - 1):
            self.connect_rooms(rooms[i], rooms[i + 1], 12)  # Wider corridors
        
        # Add many extra connections for more open feel
        for _ in range(len(rooms) // 2):  # More connections
            i, j = random.randint(0, len(rooms) - 1), random.randint(
                0, len(rooms) - 1
            )
            if i != j:
                self.connect_rooms(rooms[i], rooms[j], 12)
        
        # Enforce minimum 3-tile wall thickness
        self.enforce_minimum_wall_thickness(grid_width, grid_height, 3)
        
        # NOW update tiles once at the end
        self.tilemap.update_tiles()
        
        # Convert tilemap to wall objects
        self.build_walls_from_tilemap()
    
    def enforce_minimum_wall_thickness(self, grid_width, grid_height, min_thickness):
        """Remove thin walls by expanding open spaces"""
        # Iterate multiple times to catch all thin walls
        for iteration in range(3):
            tiles_to_remove = set()
            
            # Check each wall tile
            for x in range(grid_width):
                for y in range(grid_height):
                    if not self.tilemap.has_tile(x, y):
                        continue
                    
                    # Check if this wall tile is part of a thin wall
                    # by checking if there's open space on opposite sides
                    
                    # Check horizontal thickness
                    left_open = not self.tilemap.has_tile(x - 1, y)
                    right_open = not self.tilemap.has_tile(x + 1, y)
                    
                    if left_open and right_open:
                        # Single tile thick horizontally - remove it
                        tiles_to_remove.add((x, y))
                        continue
                    
                    # Check vertical thickness
                    top_open = not self.tilemap.has_tile(x, y - 1)
                    bottom_open = not self.tilemap.has_tile(x, y + 1)
                    
                    if top_open and bottom_open:
                        # Single tile thick vertically - remove it
                        tiles_to_remove.add((x, y))
                        continue
                    
                    # Check for 2-tile thick walls (need to be at least 3)
                    if left_open:
                        # Check if only 2 tiles thick to the right
                        if (self.tilemap.has_tile(x + 1, y) and 
                            not self.tilemap.has_tile(x + 2, y)):
                            tiles_to_remove.add((x, y))
                            tiles_to_remove.add((x + 1, y))
                    
                    if top_open:
                        # Check if only 2 tiles thick downward
                        if (self.tilemap.has_tile(x, y + 1) and 
                            not self.tilemap.has_tile(x, y + 2)):
                            tiles_to_remove.add((x, y))
                            tiles_to_remove.add((x, y + 1))
            
            # Remove the thin wall tiles
            for (x, y) in tiles_to_remove:
                self.tilemap.remove_tile(x, y, update=False)
            
            if len(tiles_to_remove) == 0:
                break
    
    def connect_rooms(self, room1, room2, corridor_width):
        """Connect two rooms with L-shaped corridor"""
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2
        cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
        cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
        
        grid_width = self.world_size // self.tilemap.tile_size
        grid_height = self.world_size // self.tilemap.tile_size
        
        # Horizontal corridor (remove tiles) - WITHOUT updating each time
        for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
            for w in range(-corridor_width // 2, corridor_width // 2 + 1):
                if 0 <= cy1 + w < grid_height and 0 <= x < grid_width:
                    self.tilemap.remove_tile(x, cy1 + w, update=False)
        
        # Vertical corridor (remove tiles) - WITHOUT updating each time
        for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
            for w in range(-corridor_width // 2, corridor_width // 2 + 1):
                if 0 <= cx2 + w < grid_width and 0 <= y < grid_height:
                    self.tilemap.remove_tile(cx2 + w, y, update=False)
    
    def build_walls_from_tilemap(self):
        """Convert tilemap to merged collision rectangles for performance"""
        tile_size = self.tilemap.tile_size
        all_tiles = self.tilemap.get_all_tiles()
        visited = set()

        # Merge adjacent tiles with same neighbor pattern into larger rectangles
        for (gx, gy) in all_tiles:
            if (gx, gy) in visited:
                continue

            # Get neighbor pattern for this tile
            has_left = self.tilemap.has_tile(gx - 1, gy)
            has_right = self.tilemap.has_tile(gx + 1, gy)
            has_top = self.tilemap.has_tile(gx, gy - 1)
            has_bottom = self.tilemap.has_tile(gx, gy + 1)
            pattern = (has_left, has_right, has_top, has_bottom)

            # Try to expand horizontally first
            width = 1
            while (gx + width, gy) not in visited and self.tilemap.has_tile(
                gx + width, gy
            ):
                # Check if neighbor pattern matches
                next_left = self.tilemap.has_tile(gx + width - 1, gy)
                next_right = self.tilemap.has_tile(gx + width + 1, gy)
                next_top = self.tilemap.has_tile(gx + width, gy - 1)
                next_bottom = self.tilemap.has_tile(gx + width, gy + 1)
                next_pattern = (next_left, next_right, next_top, next_bottom)

                if next_pattern == pattern:
                    width += 1
                else:
                    break

            # Try to expand vertically
            height = 1
            can_expand_down = True
            while can_expand_down:
                # Check if entire row can be added
                for dx in range(width):
                    if (gx + dx, gy + height) in visited or not self.tilemap.has_tile(
                        gx + dx, gy + height
                    ):
                        can_expand_down = False
                        break

                    # Check neighbor pattern
                    row_left = self.tilemap.has_tile(gx + dx - 1, gy + height)
                    row_right = self.tilemap.has_tile(gx + dx + 1, gy + height)
                    row_top = self.tilemap.has_tile(gx + dx, gy + height - 1)
                    row_bottom = self.tilemap.has_tile(gx + dx, gy + height + 1)
                    row_pattern = (row_left, row_right, row_top, row_bottom)

                    if row_pattern != pattern:
                        can_expand_down = False
                        break

                if can_expand_down:
                    height += 1

            # Mark all tiles in this rectangle as visited
            for dx in range(width):
                for dy in range(height):
                    visited.add((gx + dx, gy + dy))

            # Create merged wall
            wall = Wall(
                gx * tile_size,
                gy * tile_size,
                width * tile_size,
                height * tile_size,
                has_left=has_left,
                has_right=has_right,
                has_top=has_top,
                has_bottom=has_bottom,
            )
            self.all_walls.append(wall)
    
    def load_chunks_around(self, x, y):
        """Load chunks around position"""
        chunk_x = int(x // self.chunk_size)
        chunk_y = int(y // self.chunk_size)
        
        for cx in range(chunk_x - 2, chunk_x + 3):
            for cy in range(chunk_y - 2, chunk_y + 3):
                chunk_key = (cx, cy)
                if chunk_key not in self.loaded_chunks:
                    self.load_chunk(chunk_key)
                    self.loaded_chunks.add(chunk_key)
    
    def load_chunk(self, chunk_key):
        """Load walls for a chunk"""
        cx, cy = chunk_key
        chunk_x = cx * self.chunk_size
        chunk_y = cy * self.chunk_size
        
        if chunk_key not in self.wall_chunks:
            self.wall_chunks[chunk_key] = []
        
        for wall in self.all_walls:
            if (wall.x < chunk_x + self.chunk_size and
                wall.x + wall.width > chunk_x and
                wall.y < chunk_y + self.chunk_size and
                wall.y + wall.height > chunk_y):
                if wall not in self.wall_chunks[chunk_key]:
                    self.wall_chunks[chunk_key].append(wall)
    
    def unload_distant_chunks(self, x, y):
        """Unload chunks far from position"""
        chunk_x = int(x // self.chunk_size)
        chunk_y = int(y // self.chunk_size)
        
        chunks_to_unload = []
        for chunk_key in self.loaded_chunks:
            cx, cy = chunk_key
            if abs(cx - chunk_x) > 4 or abs(cy - chunk_y) > 4:
                chunks_to_unload.append(chunk_key)
        
        for chunk_key in chunks_to_unload:
            if chunk_key in self.wall_chunks:
                del self.wall_chunks[chunk_key]
            self.loaded_chunks.remove(chunk_key)
    
    def get_visible_walls(self, camera_x, camera_y, screen_width, screen_height):
        """Get walls visible on screen"""
        visible = []
        chunk_x = int(camera_x // self.chunk_size)
        chunk_y = int(camera_y // self.chunk_size)
        
        chunks_wide = (screen_width // self.chunk_size) + 2
        chunks_tall = (screen_height // self.chunk_size) + 2
        
        seen = set()
        for cx in range(chunk_x, chunk_x + chunks_wide):
            for cy in range(chunk_y, chunk_y + chunks_tall):
                chunk_key = (cx, cy)
                if chunk_key in self.wall_chunks:
                    for wall in self.wall_chunks[chunk_key]:
                        if id(wall) not in seen and wall.is_visible(camera_x, camera_y, screen_width, screen_height):
                            visible.append(wall)
                            seen.add(id(wall))
        return visible
    
    def get_nearby_walls(self, x, y):
        """Get walls near position"""
        chunk_x = int(x // self.chunk_size)
        chunk_y = int(y // self.chunk_size)
        
        nearby = set()
        for cx in range(chunk_x - 1, chunk_x + 2):
            for cy in range(chunk_y - 1, chunk_y + 2):
                chunk_key = (cx, cy)
                if chunk_key in self.wall_chunks:
                    nearby.update(self.wall_chunks[chunk_key])
        return list(nearby)
    
    def has_line_of_sight(self, x1, y1, x2, y2):
        """Check line of sight between two points"""
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return True
        
        nearby_walls = self.get_nearby_walls((x1 + x2) / 2, (y1 + y2) / 2)
        steps = int(distance / 25)
        
        for i in range(1, steps):
            t = i / steps
            check_x = x1 + dx * t
            check_y = y1 + dy * t
            
            for wall in nearby_walls:
                if wall.collides(check_x, check_y, 3):
                    return False
        return True
    
    def get_random_open_position(self):
        """Get random position in open space"""
        tile_size = self.tilemap.tile_size
        grid_width = self.world_size // tile_size
        grid_height = self.world_size // tile_size
        
        for _ in range(100):
            grid_x = random.randint(5, grid_width - 5)
            grid_y = random.randint(5, grid_height - 5)
            
            # Check if tile is NOT a wall (not in tilemap)
            if not self.tilemap.has_tile(grid_x, grid_y):
                return (grid_x * tile_size + tile_size // 2,
                       grid_y * tile_size + tile_size // 2)
        
        return (self.world_size // 2, self.world_size // 2)


class ShooterGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # World setup
        self.world_size = 12000  # 2x bigger map (more reasonable)
        self.chunk_manager = ChunkManager(self.world_size)
        self.chunk_manager.generate_map()
        
        # Wall renderer (pass tilemap reference)
        self.wall_renderer = WallRenderer(self.chunk_manager.tilemap)
        
        # Initialize player at center
        spawn_x = self.world_size // 2
        spawn_y = self.world_size // 2
        self.player = Player(spawn_x, spawn_y)
        
        # Load initial chunks
        self.chunk_manager.load_chunks_around(spawn_x, spawn_y)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Game state
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.items = []
        self.popups = []
        self.kills = 0
        self.goal = 50
        self.shoot_cooldown = 0
        self.spawn_timer = 0
        self.boss_active = False
        self.current_boss = None
        self.frame_count = 0
    
    def spawn_enemy(self):
        """Spawn enemy off-screen or boss in room"""
        if self.boss_active:
            return
        
        base_health = 50 + (self.kills // 5) * 50
        is_mini_boss = (self.kills > 0 and self.kills % 10 == 0 and self.kills < 50)
        is_final_boss = (self.kills == 49)
        
        if is_mini_boss or is_final_boss:
            self.enemies.clear()
            self.bullets.clear()
            self.enemy_bullets.clear()
            
            # Find open room position
            if self.chunk_manager.rooms:
                room = random.choice(self.chunk_manager.rooms)
                x = room[0] + room[2] // 2
                y = room[1] + room[3] // 2
            else:
                x, y = self.world_size // 2, self.world_size // 2
            
            # Much stronger bosses
            if is_final_boss:
                health = 2500  # Final boss has 2500 HP
                boss = Enemy(x, y, health, is_boss=True, is_final=True, boss_id=0)
            else:
                boss_number = (self.kills // 10)  # 1, 2, 3, or 4
                health = base_health * 5  # Mini-bosses have 5x health
                boss = Enemy(x, y, health, is_boss=True, is_final=False, boss_id=boss_number)
            
            # Push boss out of walls if spawned inside
            boss.push_out_of_walls(self.chunk_manager)
            
            self.enemies.append(boss)
            self.current_boss = boss
            self.boss_active = True
        else:
            # Spawn varied enemy types off-screen
            for _ in range(100):
                x, y = self.chunk_manager.get_random_open_position()
                screen_x = x - self.camera_x
                screen_y = y - self.camera_y
                
                if (screen_x < -100 or screen_x > self.width + 100 or
                    screen_y < -100 or screen_y > self.height + 100):
                    # Random enemy type (tank spawns more often)
                    rand = random.random()
                    if rand < 0.3:
                        enemy_type = 'normal'
                        health = base_health
                    elif rand < 0.45:
                        enemy_type = 'fast'
                        health = int(base_health * 0.5)
                    elif rand < 0.75:  # Increased from 0.8 to 0.75 (30% spawn rate)
                        enemy_type = 'tank'
                        health = int(base_health * 2)
                    else:
                        enemy_type = 'shooter'
                        health = int(base_health * 0.7)
                    
                    enemy = Enemy(x, y, health, enemy_type=enemy_type)
                    enemy.push_out_of_walls(self.chunk_manager)
                    self.enemies.append(enemy)
                    break
    
    def run(self):
        running = True
        
        while running:
            self.frame_count += 1
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
            
            # Update camera with proper bounds
            self.camera_x = self.player.x - self.width // 2
            self.camera_y = self.player.y - self.height // 2
            
            # Clamp camera to world bounds (prevent showing void)
            max_camera_x = max(0, self.world_size - self.width)
            max_camera_y = max(0, self.world_size - self.height)
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))
            
            # Dynamic chunk loading
            self.chunk_manager.load_chunks_around(self.player.x, self.player.y)
            self.chunk_manager.unload_distant_chunks(self.player.x, self.player.y)
            
            # Update player
            self.player.move(keys, self.chunk_manager)
            self.player.update_aim(self.enemies, self.chunk_manager)
            
            # Auto-shoot
            if self.shoot_cooldown == 0:
                shots_to_fire = 2 if self.player.has_dual_gun else 1
                
                for shot in range(shots_to_fire):
                    if self.player.multi_shot == 1:
                        self.bullets.append(Bullet(self.player.x, self.player.y,
                                                  self.player.shoot_direction,
                                                  self.player.damage, self.player.bullet_bounce))
                    else:
                        spread_angle = 0.3
                        for i in range(self.player.multi_shot):
                            offset = (i - (self.player.multi_shot - 1) / 2) * spread_angle
                            angle = math.atan2(self.player.shoot_direction[1],
                                             self.player.shoot_direction[0]) + offset
                            direction = [math.cos(angle), math.sin(angle)]
                            self.bullets.append(Bullet(self.player.x, self.player.y, direction,
                                                      self.player.damage, self.player.bullet_bounce))
                
                self.shoot_cooldown = self.player.fire_rate
            
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            
            # Check boss defeat
            if self.boss_active and self.current_boss not in self.enemies:
                self.boss_active = False
                self.current_boss = None
            
            # Spawn enemies
            if not self.boss_active:
                self.spawn_timer += 1
                spawn_delay = max(60, 300 - (self.kills * 5))
                max_enemies = min(20, 10 + self.kills // 2)  # Reduced max enemies
                
                if self.spawn_timer > spawn_delay and len(self.enemies) < max_enemies:
                    self.spawn_enemy()
                    self.spawn_timer = 0
            
            # Update bullets (optimized)
            if len(self.bullets) > 100:  # Further reduced limit
                self.bullets = self.bullets[-100:]
            
            bullets_to_remove = []
            for bullet in self.bullets:
                bullet.update()
                
                # Remove expired bullets
                if bullet.is_expired():
                    bullets_to_remove.append(bullet)
                    continue
                
                # Remove out of bounds bullets
                if (bullet.x < 0 or bullet.x > self.world_size or
                    bullet.y < 0 or bullet.y > self.world_size):
                    bullets_to_remove.append(bullet)
                    continue
                
                # Check wall collisions only for nearby walls
                nearby_walls = self.chunk_manager.get_nearby_walls(bullet.x, bullet.y)
                for wall in nearby_walls:
                    if wall.collides(bullet.x, bullet.y, bullet.size):
                        if bullet.bounces_left > 0:
                            if bullet.bounce(wall, self.frame_count):
                                # Move bullet away from wall
                                bullet.x += bullet.direction[0] * bullet.speed * 2
                                bullet.y += bullet.direction[1] * bullet.speed * 2
                            break
                        else:
                            bullets_to_remove.append(bullet)
                            break
            
            # Batch remove bullets
            self.bullets = [b for b in self.bullets if b not in bullets_to_remove]
            
            # Update player orbital
            self.player.update_orbital()
            
            # Update enemies
            for enemy in self.enemies[:]:
                has_los = self.chunk_manager.has_line_of_sight(enemy.x, enemy.y,
                                                               self.player.x, self.player.y)
                enemy.update(self.player.x, self.player.y, self.chunk_manager, has_los)
                
                if enemy.can_shoot() and has_los:
                    self.enemy_bullets.extend(enemy.shoot(self.player.x, self.player.y))
                
                # Final boss spawns minions
                if enemy.is_final and len(self.enemies) < 10:
                    enemy.minion_spawn_timer += 1
                    if enemy.minion_spawn_timer > 180:  # Every 3 seconds
                        enemy.minion_spawn_timer = 0
                        # Spawn minion near boss
                        angle = random.random() * math.pi * 2
                        minion_x = enemy.x + math.cos(angle) * 100
                        minion_y = enemy.y + math.sin(angle) * 100
                        minion_type = random.choice(['fast', 'shooter', 'tank'])
                        minion = Enemy(minion_x, minion_y, 100, enemy_type=minion_type)
                        minion.push_out_of_walls(self.chunk_manager)
                        self.enemies.append(minion)
                
                # Check player collision
                dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                if dist < self.player.size + enemy.size:
                    self.player.health = 0
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                
                # Check orbital weapon collision (optimized - only check nearby enemies)
                if self.player.has_orbital:
                    player_dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                    if player_dist < 80:  # Only check if enemy is near player
                        for i in range(3):
                            angle = self.player.orbital_angle + (i * math.pi * 2 / 3)
                            orbit_radius = 50
                            saw_x = self.player.x + math.cos(angle) * orbit_radius
                            saw_y = self.player.y + math.sin(angle) * orbit_radius
                            
                            dist = math.sqrt((saw_x - enemy.x)**2 + (saw_y - enemy.y)**2)
                            if dist < 12 + enemy.size:
                                enemy.health -= 1  # Increased damage, less frequent checks
            
            # Bullet-enemy collisions (optimized)
            bullets_to_remove = set()
            enemies_to_remove = set()
            
            for bullet in self.bullets:
                if bullet in bullets_to_remove:
                    continue
                
                for enemy in self.enemies:
                    dx = bullet.x - enemy.x
                    dy = bullet.y - enemy.y
                    dist_sq = dx*dx + dy*dy
                    collision_dist = bullet.size + enemy.size
                    
                    if dist_sq < collision_dist * collision_dist:
                        enemy.health -= bullet.damage
                        
                        # Bouncing bullets bounce off enemies but with reduced lifetime
                        if bullet.bounces_left > 0:
                            dist = math.sqrt(dist_sq)
                            if dist > 0:
                                bullet.direction = [dx/dist, dy/dist]
                            bullet.bounces_left -= 1
                            bullet.lifetime = min(bullet.lifetime, 60)  # Max 1 second after enemy hit
                            bullet.x += bullet.direction[0] * bullet.speed * 2
                            bullet.y += bullet.direction[1] * bullet.speed * 2
                        else:
                            bullets_to_remove.add(bullet)
                        
                        if enemy.health <= 0:
                            enemies_to_remove.add(enemy)
                            
                            # Boss drops special items
                            if enemy.is_boss and not enemy.is_final:
                                if enemy.boss_id == 1:
                                    item_type = 'orbital'
                                elif enemy.boss_id == 2:
                                    item_type = 'dual_gun'
                                elif enemy.boss_id == 3:
                                    item_type = 'orbital'
                                else:
                                    item_type = 'dual_gun'
                            else:
                                # Normal drops
                                item_type = random.choice(['firerate', 'multishot', 'damage', 'bounce', 'speed'])
                            
                            self.items.append(Item(enemy.x, enemy.y, item_type))
                            self.kills += 1
                        break
            
            self.bullets = [b for b in self.bullets if b not in bullets_to_remove]
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove]
            
            # Update enemy bullets
            if len(self.enemy_bullets) > 100:
                self.enemy_bullets = self.enemy_bullets[-100:]
            
            enemy_bullets_to_remove = []
            for bullet in self.enemy_bullets:
                bullet.update()
                
                if (bullet.x < 0 or bullet.x > self.world_size or
                    bullet.y < 0 or bullet.y > self.world_size):
                    enemy_bullets_to_remove.append(bullet)
                    continue
                
                dx = bullet.x - self.player.x
                dy = bullet.y - self.player.y
                dist_sq = dx*dx + dy*dy
                collision_dist = bullet.size + self.player.size
                
                if dist_sq < collision_dist * collision_dist:
                    self.player.health = 0
                    enemy_bullets_to_remove.append(bullet)
                    continue
                
                nearby_walls = self.chunk_manager.get_nearby_walls(bullet.x, bullet.y)
                for wall in nearby_walls:
                    if wall.collides(bullet.x, bullet.y, bullet.size):
                        enemy_bullets_to_remove.append(bullet)
                        break
            
            for bullet in enemy_bullets_to_remove:
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
            
            # Update items
            for item in self.items[:]:
                dist = math.sqrt((item.x - self.player.x)**2 + (item.y - self.player.y)**2)
                if dist < item.size + self.player.size:
                    # Create popup
                    popup_text = item.names.get(item.type, 'Item!')
                    popup_color = item.colors.get(item.type, (255, 255, 255))
                    self.popups.append(Popup(popup_text, item.x, item.y - 20, popup_color))
                    
                    # Apply effect
                    if item.type == 'firerate':
                        self.player.fire_rate = max(5, self.player.fire_rate - 2)
                    elif item.type == 'multishot':
                        self.player.multi_shot += 1  # No limit!
                    elif item.type == 'damage':
                        self.player.damage += 2
                    elif item.type == 'bounce':
                        self.player.bullet_bounce = min(3, self.player.bullet_bounce + 1)
                    elif item.type == 'speed':
                        self.player.speed = min(12, self.player.speed + 0.5)
                    elif item.type == 'orbital':
                        self.player.has_orbital = True
                    elif item.type == 'dual_gun':
                        self.player.has_dual_gun = True
                    self.items.remove(item)
            
            # Update popups
            for popup in self.popups[:]:
                popup.update()
                if popup.lifetime <= 0:
                    self.popups.remove(popup)
            
            # Check win/lose
            if self.kills >= self.goal:
                return self.show_victory()
            if self.player.health <= 0:
                return self.show_game_over()
            
            # Draw
            self.screen.fill((20, 20, 40))
            
            # Draw grid
            grid_size = 50
            start_x = int(self.camera_x // grid_size) * grid_size
            start_y = int(self.camera_y // grid_size) * grid_size
            
            for x in range(start_x, start_x + self.width + grid_size, grid_size):
                screen_x = x - self.camera_x
                if 0 <= screen_x <= self.width:
                    pygame.draw.line(self.screen, (30, 30, 50), (screen_x, 0), (screen_x, self.height))
            
            for y in range(start_y, start_y + self.height + grid_size, grid_size):
                screen_y = y - self.camera_y
                if 0 <= screen_y <= self.height:
                    pygame.draw.line(self.screen, (30, 30, 50), (0, screen_y), (self.width, screen_y))
            
            # Draw tiles with color based on neighbor count
            self.wall_renderer.draw_tiles(
                self.screen, self.camera_x, self.camera_y, self.width, self.height
            )
            
            # Draw game objects
            self.player.draw_orbital(self.screen, self.camera_x, self.camera_y)
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
            for bullet in self.bullets:
                bullet.draw(self.screen, self.camera_x, self.camera_y)
            
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen, self.camera_x, self.camera_y)
            
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera_x, self.camera_y)
            
            for item in self.items:
                item.draw(self.screen, self.camera_x, self.camera_y)
            
            for popup in self.popups:
                popup.draw(self.screen, self.camera_x, self.camera_y)
            
            # Draw HUD
            if self.boss_active and self.current_boss:
                # Boss health bar (no text above)
                bar_width = 600
                bar_height = 30
                bar_x = (self.width - bar_width) // 2
                bar_y = 20
                
                pygame.draw.rect(self.screen, (40, 0, 40), (bar_x, bar_y, bar_width, bar_height))
                health_percent = self.current_boss.health / self.current_boss.max_health
                health_width = int(bar_width * health_percent)
                
                if health_percent > 0.5:
                    health_color = (150, 0, 150)
                elif health_percent > 0.25:
                    health_color = (200, 0, 100)
                else:
                    health_color = (255, 0, 0)
                
                pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_width, bar_height))
                pygame.draw.rect(self.screen, (200, 0, 200), (bar_x, bar_y, bar_width, bar_height), 3)
                
                # Show health numbers inside bar
                health_font = pygame.font.Font(None, 24)
                health_str = f'{int(self.current_boss.health)} / {int(self.current_boss.max_health)}'
                health_text = health_font.render(health_str, True, (255, 255, 255))
                health_rect = health_text.get_rect(center=(self.width // 2, bar_y + bar_height // 2))
                self.screen.blit(health_text, health_rect)
            
            # Stats panel in top left
            self.draw_stats_panel()
            
            # Boss pointer
            if self.boss_active and self.current_boss:
                self.draw_boss_pointer()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return 'menu'
    
    def draw_boss_pointer(self):
        """Draw pointer showing boss location on screen edge"""
        boss = self.current_boss
        
        # Calculate boss position relative to screen
        boss_screen_x = boss.x - self.camera_x
        boss_screen_y = boss.y - self.camera_y
        
        # Check if boss is off-screen
        margin = 50
        is_off_screen = (boss_screen_x < 0 or boss_screen_x > self.width or
                        boss_screen_y < 0 or boss_screen_y > self.height)
        
        if is_off_screen:
            # Calculate angle to boss from screen center
            center_x = self.width // 2
            center_y = self.height // 2
            dx = boss_screen_x - center_x
            dy = boss_screen_y - center_y
            angle = math.atan2(dy, dx)
            
            # Find intersection with screen edge
            # Calculate where the line from center to boss intersects screen edge
            if abs(dx) > abs(dy):
                # Intersects left or right edge
                if dx > 0:
                    pointer_x = self.width - margin
                else:
                    pointer_x = margin
                pointer_y = center_y + (pointer_x - center_x) * math.tan(angle)
                pointer_y = max(margin, min(self.height - margin, pointer_y))
            else:
                # Intersects top or bottom edge
                if dy > 0:
                    pointer_y = self.height - margin
                else:
                    pointer_y = margin
                pointer_x = center_x + (pointer_y - center_y) / math.tan(angle) if math.tan(angle) != 0 else center_x
                pointer_x = max(margin, min(self.width - margin, pointer_x))
            
            # Draw pointer arrow
            arrow_size = 20
            arrow_points = [
                (pointer_x + math.cos(angle) * arrow_size,
                 pointer_y + math.sin(angle) * arrow_size),
                (pointer_x + math.cos(angle + 2.5) * arrow_size * 0.6,
                 pointer_y + math.sin(angle + 2.5) * arrow_size * 0.6),
                (pointer_x + math.cos(angle - 2.5) * arrow_size * 0.6,
                 pointer_y + math.sin(angle - 2.5) * arrow_size * 0.6)
            ]
            
            # Pulsing effect
            pulse = int(abs(math.sin(self.frame_count * 0.1)) * 100) + 155
            color = (pulse, 0, pulse)
            
            # Draw arrow
            pygame.draw.polygon(self.screen, color, arrow_points)
            pygame.draw.polygon(self.screen, (255, 255, 255), arrow_points, 2)
    
    def draw_stats_panel(self):
        """Draw player stats panel in top left"""
        panel_x = 10
        panel_y = 10
        panel_width = 220
        panel_height = 186  # Increased for speed stat
        
        # Semi-transparent background
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 20, 40, 220), panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (100, 120, 150, 255), panel_surf.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render('STATS', True, (200, 220, 255))
        self.screen.blit(title_text, (panel_x + 10, panel_y + 8))
        
        # Stats
        stat_font = pygame.font.Font(None, 24)
        y_offset = panel_y + 38
        line_height = 26
        
        # Kills
        if not self.boss_active:
            kills_text = stat_font.render(f'Kills: {self.kills}/{self.goal}', True, (255, 255, 255))
            self.screen.blit(kills_text, (panel_x + 10, y_offset))
            y_offset += line_height
        
        # Multi-shot
        shots_color = (100, 200, 255) if self.player.multi_shot > 1 else (180, 180, 180)
        shots_text = stat_font.render(f'Shots: {self.player.multi_shot}', True, shots_color)
        self.screen.blit(shots_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Fire rate
        fire_rate_percent = self.player.get_fire_rate_percent()
        fire_color = (255, 100, 255) if fire_rate_percent > 100 else (180, 180, 180)
        fire_text = stat_font.render(f'Fire Rate: {fire_rate_percent}%', True, fire_color)
        self.screen.blit(fire_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Damage
        damage_color = (255, 150, 50) if self.player.damage > 5 else (180, 180, 180)
        damage_text = stat_font.render(f'Damage: {self.player.damage}', True, damage_color)
        self.screen.blit(damage_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Bounce
        bounce_color = (0, 255, 255) if self.player.bullet_bounce > 0 else (180, 180, 180)
        bounce_text = stat_font.render(f'Bounces: {self.player.bullet_bounce}', True, bounce_color)
        self.screen.blit(bounce_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Speed
        speed_percent = int((self.player.speed / 5) * 100)
        speed_color = (100, 255, 100) if speed_percent > 100 else (180, 180, 180)
        speed_text = stat_font.render(f'Speed: {speed_percent}%', True, speed_color)
        self.screen.blit(speed_text, (panel_x + 10, y_offset))
    
    def show_victory(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        return 'menu'
            
            self.screen.fill((20, 40, 20))
            
            title_font = pygame.font.Font(None, 80)
            title_text = title_font.render('VICTORY!', True, (100, 255, 100))
            title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(title_text, title_rect)
            
            msg_font = pygame.font.Font(None, 40)
            msg_text = msg_font.render(f'You eliminated all {self.goal} enemies!', True, (255, 255, 255))
            msg_rect = msg_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(msg_text, msg_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def show_game_over(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        return 'menu'
            
            self.screen.fill((40, 20, 20))
            
            title_font = pygame.font.Font(None, 80)
            title_text = title_font.render('GAME OVER', True, (255, 100, 100))
            title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(title_text, title_rect)
            
            msg_font = pygame.font.Font(None, 40)
            msg_text = msg_font.render(f'Kills: {self.kills} / {self.goal}', True, (255, 255, 255))
            msg_rect = msg_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(msg_text, msg_rect)
            
            pygame.display.flip()
            self.clock.tick(60)


def run(screen):
    """Entry point for the game"""
    game = ShooterGame(screen)
    return game.run()
