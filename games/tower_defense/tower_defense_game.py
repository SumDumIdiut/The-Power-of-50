"""
Tower Defense - Survive 50 waves
"""
import pygame
import math
import random


class Tower:
    def __init__(self, x, y, tower_type='basic'):
        self.x = x
        self.y = y
        self.type = tower_type
        self.level = 1
        self.shoot_cooldown = 0
        self.total_cost = 0
        self.upgrade_path = None  # 'top', 'middle', 'bottom'
        self.target_angle = 0  # Angle turret is pointing
        self.current_target = None
        self.update_stats()
        
        self.update_stats()
    
    def update_stats(self):
        """Update tower stats based on type, level, and upgrade path"""
        # Base stats by type (increased costs)
        if self.type == 'basic':
            base_damage = 10
            base_range = 150
            base_fire_rate = 30
            self.color = (100, 150, 255)
            self.base_cost = 100
            self.name = 'Basic Tower'
        elif self.type == 'rapid':
            base_damage = 5
            base_range = 120
            base_fire_rate = 10
            self.color = (255, 255, 100)
            self.base_cost = 150
            self.name = 'Rapid Tower'
        elif self.type == 'bomb':
            base_damage = 30
            base_range = 100
            base_fire_rate = 60
            self.color = (255, 150, 0)
            self.base_cost = 300
            self.name = 'Bomb Tower'
        elif self.type == 'ice':
            base_damage = 2
            base_range = 130
            base_fire_rate = 45
            self.color = (100, 200, 255)
            self.base_cost = 200
            self.name = 'Ice Tower'
        
        # Apply upgrade path bonuses
        if self.level >= 2 and self.upgrade_path:
            if self.upgrade_path == 'top':  # Damage path
                base_damage *= 2
            elif self.upgrade_path == 'middle':  # Range path
                base_range = int(base_range * 1.5) if base_range < 9999 else 9999
            elif self.upgrade_path == 'bottom':  # Speed path
                base_fire_rate = max(5, int(base_fire_rate * 0.6))
        
        # Apply level multipliers
        self.damage = int(base_damage * (1 + (self.level - 1) * 0.5))
        self.range = base_range
        self.fire_rate = base_fire_rate
    
    def get_upgrade_paths(self):
        """Get available upgrade paths with descriptions"""
        if self.level == 1:
            return [
                {'path': 'top', 'name': 'Power', 'desc': '2x Damage', 'cost': self.get_upgrade_cost()},
                {'path': 'middle', 'name': 'Range', 'desc': '+50% Range', 'cost': self.get_upgrade_cost()},
                {'path': 'bottom', 'name': 'Speed', 'desc': '40% Faster', 'cost': self.get_upgrade_cost()}
            ]
        elif self.level == 2 and self.upgrade_path:
            return [{'path': self.upgrade_path, 'name': 'Upgrade', 'desc': 'Enhance further', 'cost': self.get_upgrade_cost()}]
        return []
    
    def get_upgrade_cost(self):
        """Get cost to upgrade to next level"""
        return int(self.base_cost * self.level * 1.2)
    
    def get_sell_value(self):
        """Get 70% of total investment back"""
        return int(self.total_cost * 0.7)
    
    def upgrade(self, path=None):
        """Upgrade tower to next level with chosen path"""
        if self.level < 3:
            if self.level == 1 and path:
                self.upgrade_path = path
            self.level += 1
            self.update_stats()
            return True
        return False
    
    def update_target_angle(self, target):
        """Update turret angle to point at target"""
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            self.target_angle = math.atan2(dy, dx)
            self.current_target = target
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def can_shoot(self):
        return self.shoot_cooldown == 0
    
    def shoot(self, target):
        self.shoot_cooldown = self.fire_rate
        # Ice towers apply slow effect
        applies_ice = (self.type == 'ice')
        return Bullet(self.x, self.y, target, self.damage, applies_ice)
    
    def draw(self, screen, show_range=False):
        # Tower base (stone platform)
        pygame.draw.circle(screen, (80, 80, 90), (int(self.x), int(self.y)), 22)
        pygame.draw.circle(screen, (100, 100, 110), (int(self.x), int(self.y)), 22, 2)
        
        # Tower body (rotates to face target)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 16)
        
        # Rotating turret/barrel
        barrel_length = 20
        barrel_end_x = self.x + math.cos(self.target_angle) * barrel_length
        barrel_end_y = self.y + math.sin(self.target_angle) * barrel_length
        
        # Draw barrel based on type
        if self.type == 'rapid':
            # Multiple barrels
            for offset in [-0.2, 0, 0.2]:
                angle = self.target_angle + offset
                end_x = self.x + math.cos(angle) * (barrel_length - 5)
                end_y = self.y + math.sin(angle) * (barrel_length - 5)
                pygame.draw.line(screen, (200, 200, 80), (self.x, self.y), (end_x, end_y), 3)
        elif self.type == 'ice':
            # Ice crystal barrel
            pygame.draw.line(screen, (150, 220, 255), (self.x, self.y), 
                           (barrel_end_x, barrel_end_y), 5)
            pygame.draw.circle(screen, (200, 240, 255), (int(barrel_end_x), int(barrel_end_y)), 4)
        elif self.type == 'bomb':
            # Mortar tube
            pygame.draw.line(screen, (200, 120, 50), (self.x, self.y), 
                           (barrel_end_x, barrel_end_y), 6)
        else:
            # Basic cannon
            pygame.draw.line(screen, (80, 120, 200), (self.x, self.y), 
                           (barrel_end_x, barrel_end_y), 5)
        
        # Border
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 16, 2)
        
        # Level indicator
        if self.level > 1:
            level_font = pygame.font.Font(None, 16)
            level_text = level_font.render(str(self.level), True, (255, 255, 255))
            level_rect = level_text.get_rect(center=(self.x, self.y + 25))
            pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y + 25)), 8)
            screen.blit(level_text, level_rect)
        
        # Range indicator
        if show_range and self.range < 9999:
            range_surf = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (*self.color, 30), (self.range, self.range), self.range)
            pygame.draw.circle(range_surf, (*self.color, 100), (self.range, self.range), self.range, 2)
            screen.blit(range_surf, (int(self.x - self.range), int(self.y - self.range)))


class Bullet:
    def __init__(self, x, y, target, damage, applies_ice=False):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = 15  # Much faster bullets
        self.size = 4
        self.applies_ice = applies_ice
    
    def update(self):
        # Move towards target (fast enough to appear straight)
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
    
    def draw(self, screen):
        color = (100, 200, 255) if self.applies_ice else (255, 255, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
    
    def hit_target(self):
        if self.target:
            dx = self.x - self.target.x
            dy = self.y - self.target.y
            return math.sqrt(dx*dx + dy*dy) < 10
        return False


class Enemy:
    def __init__(self, path, wave):
        self.path = path
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.base_speed = 1 + (wave * 0.05)
        self.speed = self.base_speed
        self.health = 50 + (wave * 10)
        self.max_health = self.health
        self.size = 15
        self.reward = 10 + wave
        self.ice_timer = 0  # Frames remaining of ice effect
    
    def update(self):
        # Update ice effect
        if self.ice_timer > 0:
            self.ice_timer -= 1
            self.speed = self.base_speed * 0.5  # 50% slow
        else:
            self.speed = self.base_speed
        
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.speed:
                self.path_index += 1
                if self.path_index < len(self.path):
                    self.x, self.y = self.path[self.path_index]
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
    
    def apply_ice(self, duration=120):
        """Apply ice slow effect"""
        self.ice_timer = max(self.ice_timer, duration)
    
    def reached_end(self):
        return self.path_index >= len(self.path) - 1
    
    def draw(self, screen):
        # Enemy body (blue tint if frozen)
        if self.ice_timer > 0:
            color = (150, 150, 255)
            border_color = (100, 100, 200)
        else:
            color = (255, 50, 50)
            border_color = (150, 0, 0)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, border_color, (int(self.x), int(self.y)), self.size, 2)
        
        # Health bar
        bar_width = 30
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size - 8
        
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))


class TowerDefenseGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # UI dimensions
        self.side_panel_width = 200
        self.top_bar_height = 100
        self.play_area_width = self.width - self.side_panel_width
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        
        # Game state
        self.money = 200
        self.lives = 20
        self.wave = 0
        self.max_waves = 50
        
        # Path for enemies - winding loop across full screen
        path_width = self.play_area_width
        path_height = self.height - self.top_bar_height
        
        self.path = [
            (0, self.top_bar_height + path_height * 0.3),
            (path_width * 0.15, self.top_bar_height + path_height * 0.3),
            (path_width * 0.15, self.top_bar_height + path_height * 0.7),
            (path_width * 0.35, self.top_bar_height + path_height * 0.7),
            (path_width * 0.35, self.top_bar_height + path_height * 0.2),
            (path_width * 0.55, self.top_bar_height + path_height * 0.2),
            (path_width * 0.55, self.top_bar_height + path_height * 0.8),
            (path_width * 0.75, self.top_bar_height + path_height * 0.8),
            (path_width * 0.75, self.top_bar_height + path_height * 0.5),
            (path_width - 80, self.top_bar_height + path_height * 0.5)  # End near right edge
        ]
        
        self.towers = []
        self.enemies = []
        self.bullets = []
        
        self.wave_active = False
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.wave_countdown = 600  # 10 seconds at 60fps before first wave
        self.wave_delay = 120  # 2 seconds between waves
        
        # UI
        self.selected_tower_type = 'basic'
        self.placing_tower = False
        self.hover_tower = None
        self.selected_tower = None
        self.dragging_tower = None
        self.drag_start_pos = None
    
    def start_wave(self):
        if not self.wave_active and self.wave < self.max_waves:
            self.wave += 1
            self.wave_active = True
            self.enemies_to_spawn = 5 + self.wave * 2
            self.spawn_timer = 0
            self.wave_countdown = 0
    
    def spawn_enemy(self):
        if self.enemies_to_spawn > 0:
            self.enemies.append(Enemy(self.path, self.wave))
            self.enemies_to_spawn -= 1
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'

                    elif event.key == pygame.K_1:
                        self.selected_tower_type = 'basic'
                    elif event.key == pygame.K_2:
                        self.selected_tower_type = 'rapid'
                    elif event.key == pygame.K_3:
                        self.selected_tower_type = 'bomb'
                    elif event.key == pygame.K_4:
                        self.selected_tower_type = 'ice'
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        # Check if clicking upgrade/sell buttons
                        if self.selected_tower and mouse_x > self.play_area_width:
                            button_clicked = self.handle_tower_menu_click(mouse_y)
                            if button_clicked and button_clicked.startswith('upgrade_'):
                                path = button_clicked.split('_')[1]
                                if self.selected_tower.level < 3:
                                    cost = self.selected_tower.get_upgrade_cost()
                                    if self.money >= cost:
                                        self.money -= cost
                                        self.selected_tower.total_cost += cost
                                        self.selected_tower.upgrade(path)
                            elif button_clicked == 'sell':
                                self.money += self.selected_tower.get_sell_value()
                                self.towers.remove(self.selected_tower)
                                self.selected_tower = None
                        # Check if clicking on buy menu to start drag
                        elif mouse_x > self.play_area_width:
                            tower_type = self.handle_buy_menu_click(mouse_y)
                            if tower_type:
                                tower_costs = {'basic': 100, 'rapid': 150, 'bomb': 300, 'ice': 200}
                                if self.money >= tower_costs[tower_type]:
                                    self.dragging_tower = Tower(mouse_x, mouse_y, tower_type)
                                    self.dragging_tower.total_cost = tower_costs[tower_type]
                                    self.drag_start_pos = (mouse_x, mouse_y)
                        else:
                            # Check if clicking existing tower
                            clicked_tower = False
                            for tower in self.towers:
                                if math.sqrt((mouse_x - tower.x)**2 + (mouse_y - tower.y)**2) < 25:
                                    self.selected_tower = tower
                                    clicked_tower = True
                                    break
                            if not clicked_tower:
                                self.selected_tower = None
                    elif event.button == 3:  # Right click
                        self.selected_tower = None
                        self.dragging_tower = None
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging_tower:  # Release drag
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if self.can_place_tower(mouse_x, mouse_y):
                            tower_costs = {'basic': 100, 'rapid': 150, 'bomb': 300, 'ice': 200}
                            cost = tower_costs[self.dragging_tower.type]
                            self.money -= cost
                            self.dragging_tower.total_cost = cost
                            self.towers.append(self.dragging_tower)
                            self.selected_tower = self.dragging_tower
                        self.dragging_tower = None
            
            # Update dragging tower position
            if self.dragging_tower:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.dragging_tower.x = mouse_x
                self.dragging_tower.y = mouse_y
            
            # Handle wave countdown
            if self.wave_countdown > 0:
                self.wave_countdown -= 1
                if self.wave_countdown == 0:
                    self.start_wave()
            
            # Update
            if self.wave_active:
                self.spawn_timer += 1
                if self.spawn_timer > 60 and self.enemies_to_spawn > 0:
                    self.spawn_enemy()
                    self.spawn_timer = 0
                
                # Check if wave is complete
                if self.enemies_to_spawn == 0 and len(self.enemies) == 0:
                    self.wave_active = False
                    # Give wave completion bonus once
                    if not hasattr(self, 'wave_bonus_given'):
                        wave_bonus = 100 + (self.wave * 20)
                        self.money += wave_bonus
                        self.wave_bonus_given = True
                        # Start countdown for next wave
                        if self.wave < self.max_waves:
                            self.wave_countdown = self.wave_delay
            
            # Reset bonus flag when new wave starts
            if self.wave_active and hasattr(self, 'wave_bonus_given'):
                delattr(self, 'wave_bonus_given')
            
            # Update towers
            for tower in self.towers:
                tower.update()
                
                # Find target
                closest_enemy = None
                closest_dist = tower.range
                
                for enemy in self.enemies:
                    dx = enemy.x - tower.x
                    dy = enemy.y - tower.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_enemy = enemy
                
                # Update turret angle
                if closest_enemy:
                    tower.update_target_angle(closest_enemy)
                    
                    # Shoot if ready
                    if tower.can_shoot():
                        self.bullets.append(tower.shoot(closest_enemy))
            
            # Update bullets
            bullets_to_remove = []
            for bullet in self.bullets:
                bullet.update()
                
                if bullet.hit_target():
                    if bullet.target in self.enemies:
                        bullet.target.health -= bullet.damage
                        # Apply ice effect
                        if bullet.applies_ice:
                            bullet.target.apply_ice()
                        if bullet.target.health <= 0:
                            self.money += bullet.target.reward
                            self.enemies.remove(bullet.target)
                    bullets_to_remove.append(bullet)
                elif bullet.target not in self.enemies:
                    bullets_to_remove.append(bullet)
            
            # Remove bullets in batch
            for bullet in bullets_to_remove:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update()
                
                if enemy.reached_end():
                    self.lives -= 1
                    self.enemies.remove(enemy)
            
            # Check win/lose
            if self.lives <= 0:
                return self.show_game_over()
            if self.wave >= self.max_waves and not self.wave_active and len(self.enemies) == 0:
                return self.show_victory()
            
            # Draw
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return 'menu'
    
    def place_tower(self, x, y):
        # Don't place on top bar
        if y < self.top_bar_height:
            return
        
        # Check if clicking existing tower to select it
        for tower in self.towers:
            if math.sqrt((x - tower.x)**2 + (y - tower.y)**2) < 25:
                self.selected_tower = tower
                return
        
        # Get tower cost
        tower_costs = {'basic': 100, 'rapid': 150, 'bomb': 300, 'ice': 200}
        cost = tower_costs[self.selected_tower_type]
        
        if self.money >= cost:
            # Check if not on path
            on_path = False
            for px, py in self.path:
                if math.sqrt((x - px)**2 + (y - py)**2) < 40:
                    on_path = True
                    break
            
            # Check if not too close to other towers
            too_close = False
            for tower in self.towers:
                if math.sqrt((x - tower.x)**2 + (y - tower.y)**2) < 50:
                    too_close = True
                    break
            
            if not on_path and not too_close:
                new_tower = Tower(x, y, self.selected_tower_type)
                self.towers.append(new_tower)
                self.money -= cost
                self.selected_tower = new_tower
    
    def draw(self):
        self.screen.fill((40, 60, 40))
        
        # Draw path
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, (100, 80, 60), self.path[i], self.path[i + 1], 30)
        
        # Draw path points
        for point in self.path:
            pygame.draw.circle(self.screen, (80, 60, 40), point, 15)
        
        # Draw hut at end of path
        hut_x, hut_y = self.path[-1]
        
        # Hut base
        hut_width = 60
        hut_height = 50
        pygame.draw.rect(self.screen, (139, 90, 43), 
                        (hut_x - hut_width // 2, hut_y - hut_height // 2, hut_width, hut_height))
        pygame.draw.rect(self.screen, (101, 67, 33), 
                        (hut_x - hut_width // 2, hut_y - hut_height // 2, hut_width, hut_height), 3)
        
        # Roof
        roof_points = [
            (hut_x, hut_y - hut_height // 2 - 20),
            (hut_x - hut_width // 2 - 10, hut_y - hut_height // 2),
            (hut_x + hut_width // 2 + 10, hut_y - hut_height // 2)
        ]
        pygame.draw.polygon(self.screen, (160, 82, 45), roof_points)
        pygame.draw.polygon(self.screen, (120, 60, 30), roof_points, 3)
        
        # Door
        pygame.draw.rect(self.screen, (80, 50, 20), 
                        (hut_x - 10, hut_y, 20, 25))
        
        # Health bar above hut
        bar_width = 80
        bar_height = 10
        bar_x = hut_x - bar_width // 2
        bar_y = hut_y - hut_height // 2 - 35
        
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_percent = self.lives / 20
        health_width = int(bar_width * health_percent)
        if health_percent > 0.5:
            health_color = (0, 255, 0)
        elif health_percent > 0.25:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)
        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw towers
        for tower in self.towers:
            show_range = (tower == self.selected_tower)
            tower.draw(self.screen, show_range)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw dragging tower with range indicator
        if self.dragging_tower:
            # Draw range circle
            if self.dragging_tower.range < 9999:
                range_surf = pygame.Surface((self.dragging_tower.range * 2, self.dragging_tower.range * 2), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (255, 255, 255, 50), 
                                 (self.dragging_tower.range, self.dragging_tower.range), 
                                 self.dragging_tower.range)
                pygame.draw.circle(range_surf, (255, 255, 255, 150), 
                                 (self.dragging_tower.range, self.dragging_tower.range), 
                                 self.dragging_tower.range, 2)
                self.screen.blit(range_surf, 
                               (int(self.dragging_tower.x - self.dragging_tower.range), 
                                int(self.dragging_tower.y - self.dragging_tower.range)))
            
            # Check if valid placement
            can_place = self.can_place_tower(self.dragging_tower.x, self.dragging_tower.y)
            
            # Draw tower with transparency
            temp_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            temp_tower = Tower(25, 25, self.dragging_tower.type)
            temp_tower.draw(temp_surf, False)
            temp_surf.set_alpha(200 if can_place else 100)
            self.screen.blit(temp_surf, (int(self.dragging_tower.x - 25), int(self.dragging_tower.y - 25)))
        
        # Draw HUD
        self.draw_hud()
    
    def can_place_tower(self, x, y):
        """Check if tower can be placed at position"""
        if y < self.top_bar_height or x > self.play_area_width:
            return False
        
        # Check if on path
        for px, py in self.path:
            if math.sqrt((x - px)**2 + (y - py)**2) < 40:
                return False
        
        # Check if too close to other towers
        for tower in self.towers:
            if math.sqrt((x - tower.x)**2 + (y - tower.y)**2) < 50:
                return False
        
        return True
    
    def handle_tower_menu_click(self, mouse_y):
        """Handle clicks on tower upgrade/sell menu"""
        if not self.selected_tower:
            return None
        
        paths = self.selected_tower.get_upgrade_paths()
        
        # Check upgrade path buttons
        for i, path_info in enumerate(paths):
            button_y = 150 + i * 70
            if button_y < mouse_y < button_y + 60:
                return f"upgrade_{path_info['path']}"
        
        # Sell button (below upgrade buttons)
        sell_y = 150 + len(paths) * 70 + 10
        if sell_y < mouse_y < sell_y + 60:
            return 'sell'
        
        return None
    
    def handle_buy_menu_click(self, mouse_y):
        """Handle clicks on the buy menu - returns tower type if clicked"""
        # If tower selected, show upgrade/sell menu instead
        if self.selected_tower:
            return None
        
        tower_types = ['basic', 'rapid', 'bomb', 'ice']
        button_height = min(140, (self.height - 200) // 4)
        
        for i, tower_type in enumerate(tower_types):
            button_y = 150 + i * (button_height + 15)
            if button_y < mouse_y < button_y + button_height:
                self.selected_tower_type = tower_type
                return tower_type
        return None
    
    def draw_hud(self):
        # Side panel background
        pygame.draw.rect(self.screen, (30, 40, 30), 
                        (self.play_area_width, 0, self.side_panel_width, self.height))
        pygame.draw.rect(self.screen, (100, 120, 100), 
                        (self.play_area_width, 0, self.side_panel_width, self.height), 3)
        
        # Top bar
        pygame.draw.rect(self.screen, (40, 50, 40), 
                        (0, 0, self.play_area_width, self.top_bar_height))
        pygame.draw.rect(self.screen, (100, 120, 100), 
                        (0, 0, self.play_area_width, self.top_bar_height), 3)
        
        # Money
        money_text = self.font.render(f'${self.money}', True, (255, 255, 100))
        self.screen.blit(money_text, (20, 15))
        
        # Lives (health bar style)
        lives_text = self.font.render(f'Health: {self.lives}/20', True, (255, 100, 100))
        self.screen.blit(lives_text, (20, 45))
        
        # Wave info
        if self.wave_countdown > 0:
            countdown_sec = int(self.wave_countdown / 60) + 1
            wave_text = self.font.render(f'Wave {self.wave + 1} in {countdown_sec}s', True, (100, 255, 100))
        else:
            wave_text = self.font.render(f'Wave {self.wave}/{self.max_waves}', True, (100, 200, 255))
        self.screen.blit(wave_text, (250, 15))
        
        # Buy menu title or tower info
        title_font = pygame.font.Font(None, 48)
        
        if self.selected_tower:
            # Show selected tower info
            title_text = title_font.render(self.selected_tower.name, True, (200, 220, 200))
            title_rect = title_text.get_rect(center=(self.play_area_width + self.side_panel_width // 2, 50))
            self.screen.blit(title_text, title_rect)
            
            # Level and path indicator
            level_font = pygame.font.Font(None, 28)
            level_str = f'Level {self.selected_tower.level}/3'
            if self.selected_tower.upgrade_path:
                path_names = {'top': 'Power', 'middle': 'Range', 'bottom': 'Speed'}
                level_str += f' - {path_names[self.selected_tower.upgrade_path]}'
            level_text = level_font.render(level_str, True, (180, 180, 180))
            level_rect = level_text.get_rect(center=(self.play_area_width + self.side_panel_width // 2, 90))
            self.screen.blit(level_text, level_rect)
            
            x = self.play_area_width + 10
            button_width = self.side_panel_width - 20
            
            # Upgrade path buttons
            paths = self.selected_tower.get_upgrade_paths()
            for i, path_info in enumerate(paths):
                button_y = 150 + i * 70
                button_height = 60
                
                can_afford = self.money >= path_info['cost']
                color = (50, 100, 50) if can_afford else (60, 60, 60)
                border_color = (100, 200, 100) if can_afford else (100, 100, 100)
                
                pygame.draw.rect(self.screen, color, (x, button_y, button_width, button_height), border_radius=5)
                pygame.draw.rect(self.screen, border_color, (x, button_y, button_width, button_height), 3, border_radius=5)
                
                # Path name
                name_font = pygame.font.Font(None, 26)
                name_text = name_font.render(path_info['name'], True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(x + button_width // 2, button_y + 15))
                self.screen.blit(name_text, name_rect)
                
                # Description
                desc_font = pygame.font.Font(None, 20)
                desc_text = desc_font.render(path_info['desc'], True, (200, 200, 200))
                desc_rect = desc_text.get_rect(center=(x + button_width // 2, button_y + 35))
                self.screen.blit(desc_text, desc_rect)
                
                # Cost
                cost_font = pygame.font.Font(None, 22)
                cost_text = cost_font.render(f'${path_info["cost"]}', True, (255, 255, 100))
                cost_rect = cost_text.get_rect(center=(x + button_width // 2, button_y + 50))
                self.screen.blit(cost_text, cost_rect)
            
            if self.selected_tower.level >= 3:
                # Max level indicator
                max_y = 150
                pygame.draw.rect(self.screen, (40, 40, 40), (x, max_y, button_width, 60), border_radius=5)
                pygame.draw.rect(self.screen, (80, 80, 80), (x, max_y, button_width, 60), 3, border_radius=5)
                max_font = pygame.font.Font(None, 28)
                max_text = max_font.render('MAX LEVEL', True, (150, 150, 150))
                max_rect = max_text.get_rect(center=(x + button_width // 2, max_y + 30))
                self.screen.blit(max_text, max_rect)
            
            # Sell button
            sell_y = 150 + len(paths) * 70 + 10 if paths else 220
            sell_height = 60
            sell_value = self.selected_tower.get_sell_value()
            
            pygame.draw.rect(self.screen, (100, 50, 50), (x, sell_y, button_width, sell_height), border_radius=5)
            pygame.draw.rect(self.screen, (200, 100, 100), (x, sell_y, button_width, sell_height), 3, border_radius=5)
            
            sell_font = pygame.font.Font(None, 28)
            sell_text = sell_font.render(f'Sell ${sell_value}', True, (255, 255, 255))
            sell_rect = sell_text.get_rect(center=(x + button_width // 2, sell_y + sell_height // 2))
            self.screen.blit(sell_text, sell_rect)
            
            return  # Don't show tower buy menu
        
        # Show tower buy menu
        title_text = title_font.render('TOWERS', True, (200, 220, 200))
        title_rect = title_text.get_rect(center=(self.play_area_width + self.side_panel_width // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Tower buttons
        tower_types = [
            ('basic', 'Basic', 100),
            ('rapid', 'Rapid', 150),
            ('bomb', 'Bomb', 300),
            ('ice', 'Ice', 200)
        ]
        
        button_height = min(140, (self.height - 200) // 4)
        button_width = self.side_panel_width - 20
        
        for i, (tower_type, name, cost) in enumerate(tower_types):
            y = 150 + i * (button_height + 15)
            x = self.play_area_width + 10
            
            # Button background
            if tower_type == self.selected_tower_type:
                color = (60, 80, 60)
                border_color = (150, 255, 150)
            else:
                color = (40, 50, 40)
                border_color = (80, 100, 80)
            
            pygame.draw.rect(self.screen, color, (x, y, button_width, button_height), border_radius=5)
            pygame.draw.rect(self.screen, border_color, (x, y, button_width, button_height), 3, border_radius=5)
            
            # Tower preview
            preview_tower = Tower(x + button_width // 2, y + 40, tower_type)
            preview_tower.draw(self.screen, False)
            
            # Name
            name_font = pygame.font.Font(None, 28)
            name_text = name_font.render(name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(x + button_width // 2, y + 80))
            self.screen.blit(name_text, name_rect)
            
            # Cost
            cost_color = (255, 255, 100) if self.money >= cost else (255, 100, 100)
            cost_text = name_font.render(f'${cost}', True, cost_color)
            cost_rect = cost_text.get_rect(center=(x + button_width // 2, y + 105))
            self.screen.blit(cost_text, cost_rect)
    
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
            title_rect = title_text.get_rect(center=(400, 200))
            self.screen.blit(title_text, title_rect)
            
            msg_text = self.font.render(f'You survived all {self.max_waves} waves!', True, (255, 255, 255))
            msg_rect = msg_text.get_rect(center=(400, 300))
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
            title_rect = title_text.get_rect(center=(400, 200))
            self.screen.blit(title_text, title_rect)
            
            msg_text = self.font.render(f'Survived {self.wave} / {self.max_waves} waves', True, (255, 255, 255))
            msg_rect = msg_text.get_rect(center=(400, 300))
            self.screen.blit(msg_text, msg_rect)
            
            pygame.display.flip()
            self.clock.tick(60)


def run(screen):
    """Entry point for the game"""
    game = TowerDefenseGame(screen)
    return game.run()
