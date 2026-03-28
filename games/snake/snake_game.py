"""
Snake Game — Remake
Collect 50 apples to win.

Visuals: smooth tube body, gradient colour, glowing apple, particle fx,
         animated eyes/tongue, speed scaling, polished HUD.
"""
from __future__ import annotations
import pygame
import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(__file__))
from helpers import (
    generate_random_position,
    is_out_of_bounds,
    spawn_wall_block,
    is_valid_turn,
)
import snake_save as _ss

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GAME_WIDTH    = 1280
GAME_HEIGHT   = 720
GRID_TILES_X  = 64
GRID_TILES_Y  = 36
TILE_W        = GAME_WIDTH  // GRID_TILES_X   # 20
TILE_H        = GAME_HEIGHT // GRID_TILES_Y   # 20
WIN_SCORE     = 50
WALLS_PER_APPLE   = 2
MOVE_DELAY_START  = 7    # frames between steps at score 0  (was 10 — faster default)
MOVE_DELAY_MIN    = 2    # fastest the snake can get        (was 3)

# Palette
C_BG         = ( 8,  10,  16)
C_GRID       = (14,  17,  26)
C_SNAKE_HEAD = (60, 255,  80)
C_SNAKE_TAIL = (10,  65,  22)
C_TONGUE     = (255,  50,  80)
C_APPLE      = (255,  48,  36)
C_APPLE_HL   = (255, 160, 120)
C_LEAF       = ( 40, 200,  55)
C_WALL       = ( 26,  32,  44)
C_WALL_LT    = ( 48,  60,  80)
C_WALL_DK    = ( 14,  18,  26)
C_HUD        = (225, 230, 240)


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'r', 'g', 'b', 'size')

    def __init__(self, x, y, vx, vy, life, color, size=3):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.life        = int(life)
        self.max_life    = int(life)
        self.r, self.g, self.b = color
        self.size        = size

    def update(self) -> bool:
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.12
        self.vx *= 0.94
        self.life -= 1
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        alpha  = self.life / self.max_life
        radius = max(1, int(self.size * alpha))
        c = (int(self.r * alpha), int(self.g * alpha), int(self.b * alpha))
        pygame.draw.circle(screen, c, (int(self.x), int(self.y)), radius)


# ---------------------------------------------------------------------------
# Popup (floating "+1" text)
# ---------------------------------------------------------------------------
class Popup:
    _font: pygame.font.Font | None = None

    def __init__(self, text: str, x: float, y: float,
                 color=(200, 255, 100)):
        self.text  = text
        self.x     = float(x)
        self.y     = float(y)
        self.life  = 40
        self.color = color

    @classmethod
    def _get_font(cls) -> pygame.font.Font:
        if cls._font is None:
            cls._font = pygame.font.SysFont('segoeui', 20, bold=True)
        return cls._font

    def update(self) -> bool:
        self.y    -= 0.9
        self.life -= 1
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        alpha = min(1.0, self.life / 20.0)
        c = tuple(int(ch * alpha) for ch in self.color)
        surf = self._get_font().render(self.text, True, c)
        screen.blit(surf, (int(self.x) - surf.get_width() // 2, int(self.y)))


# ---------------------------------------------------------------------------
# SnakeGame
# ---------------------------------------------------------------------------
class SnakeGame:

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, screen: pygame.Surface,
                 seed: str | None = None,
                 save_data: dict | None = None):
        self.display_screen = screen
        dw, dh = screen.get_size()
        self.screen   = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        scale         = min(dw / GAME_WIDTH, dh / GAME_HEIGHT)
        self.scale    = scale
        self.offset_x = int((dw - GAME_WIDTH  * scale) // 2)
        self.offset_y = int((dh - GAME_HEIGHT * scale) // 2)
        self.clock    = pygame.time.Clock()

        # Fonts (cached)
        self._f_hud   = pygame.font.SysFont('segoeui', 24, bold=True)
        self._f_big   = pygame.font.SysFont('segoeui', 54, bold=True)
        self._f_hint  = pygame.font.SysFont('segoeui', 22)

        # Effects
        self.particles: list[Particle] = []
        self.popups:    list[Popup]    = []
        self._glow_cache: dict[int, pygame.Surface] = {}

        # Pre-bake background + cached overlay
        self._bg      = self._bake_bg()
        self._overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 145))

        # Seed + deterministic world RNG (walls + apples only)
        self.seed = (seed or _ss.new_seed()).upper()
        self._rng = random.Random(_ss.seed_to_int(self.seed))

        if save_data:
            self._restore_state(save_data)
        else:
            self._fresh_start()

    # ------------------------------------------------------------------
    # State init / save / restore
    # ------------------------------------------------------------------

    def _fresh_start(self) -> None:
        sx = (GRID_TILES_X // 2) * TILE_W
        sy = (GRID_TILES_Y // 2) * TILE_H
        self.snake          = [(sx, sy), (sx - TILE_W, sy), (sx - 2*TILE_W, sy)]
        self.direction      = (1, 0)
        self.next_direction = (1, 0)
        self.walls:         list[tuple] = []
        self.wall_segments: list[list]  = []
        self.apple_pos      = self._new_apple()
        self.score          = 0
        self.frame          = 0
        self.game_over      = False
        self.won            = False
        self.move_timer     = 0

    def _save_state(self) -> dict:
        return {
            'seed':           self.seed,
            'score':          self.score,
            'snake':          [list(p) for p in self.snake],
            'direction':      list(self.direction),
            'next_direction': list(self.next_direction),
            'apple_pos':      list(self.apple_pos),
            'walls':          [list(p) for p in self.walls],
            'wall_segments':  [[list(p) for p in seg] for seg in self.wall_segments],
            'move_timer':     self.move_timer,
        }

    def _restore_state(self, d: dict) -> None:
        self.snake          = [tuple(p) for p in d['snake']]
        self.direction      = tuple(d['direction'])
        self.next_direction = tuple(d['next_direction'])
        self.apple_pos      = tuple(d['apple_pos'])
        self.walls          = [tuple(p) for p in d['walls']]
        self.wall_segments  = [[tuple(p) for p in seg] for seg in d['wall_segments']]
        self.score          = d['score']
        self.move_timer     = d.get('move_timer', 0)
        self.frame          = 0
        self.game_over      = False
        self.won            = False
        # Advance world RNG to approximate where it would be after this many spawns
        for _ in range(self.score * (WALLS_PER_APPLE + 1)):
            self._rng.random()

    # ------------------------------------------------------------------
    # Background
    # ------------------------------------------------------------------

    def _bake_bg(self) -> pygame.Surface:
        surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        for gx in range(GRID_TILES_X):
            for gy in range(GRID_TILES_Y):
                n = (gx * 73856093 ^ gy * 19349663) & 0xFFFFFF
                n = ((n ^ (n >> 13)) * 1664525 + 1013904223) & 0xFFFFFF
                v = (n & 0xFF) / 255.0
                r = min(255, C_BG[0] + int(v * 4))
                g = min(255, C_BG[1] + int(v * 5))
                b = min(255, C_BG[2] + int(v * 7))
                pygame.draw.rect(surf, (r, g, b),
                                 (gx * TILE_W, gy * TILE_H, TILE_W, TILE_H))
        for x in range(0, GAME_WIDTH + 1, TILE_W):
            pygame.draw.line(surf, C_GRID, (x, 0), (x, GAME_HEIGHT))
        for y in range(0, GAME_HEIGHT + 1, TILE_H):
            pygame.draw.line(surf, C_GRID, (0, y), (GAME_WIDTH, y))
        return surf

    # ------------------------------------------------------------------
    # World helpers
    # ------------------------------------------------------------------

    def _new_apple(self) -> tuple:
        excluded = list(self.snake) + self.walls if hasattr(self, 'walls') else list(self.snake)
        return generate_random_position(
            GRID_TILES_X, GRID_TILES_Y, TILE_W, TILE_H,
            excluded_positions=excluded,
            rng=self._rng,
        )

    def _spawn_walls(self, count: int = WALLS_PER_APPLE) -> None:
        for _ in range(count):
            spawn_wall_block(
                self.walls, self.wall_segments, self.snake, self.apple_pos,
                GRID_TILES_X, GRID_TILES_Y, TILE_W, TILE_H,
                GAME_WIDTH, GAME_HEIGHT,
                rng=self._rng,
            )

    def _move_delay(self) -> int:
        return max(MOVE_DELAY_MIN, MOVE_DELAY_START - self.score // 5)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _handle_keydown(self, key) -> str | None:
        if key == pygame.K_ESCAPE:
            return 'pause'
        if self.game_over or self.won:
            if key == pygame.K_RETURN:
                return 'restart' if self.game_over else 'won'
            return None

        key_dir = {
            pygame.K_UP:    (0, -1),  pygame.K_w: (0, -1),
            pygame.K_DOWN:  (0,  1),  pygame.K_s: (0,  1),
            pygame.K_LEFT:  (-1, 0),  pygame.K_a: (-1, 0),
            pygame.K_RIGHT: ( 1, 0),  pygame.K_d: ( 1, 0),
        }
        if key in key_dir:
            nd = key_dir[key]
            if is_valid_turn(self.direction, nd):
                self.next_direction = nd
        return None

    # ------------------------------------------------------------------
    # Step logic
    # ------------------------------------------------------------------

    def _step(self) -> None:
        self.direction = self.next_direction
        hx, hy   = self.snake[0]
        new_head = (hx + self.direction[0] * TILE_W,
                    hy + self.direction[1] * TILE_H)

        if (is_out_of_bounds(new_head, GAME_WIDTH, GAME_HEIGHT) or
                new_head in self.snake or
                new_head in self.walls):
            self.game_over = True
            cx, cy = hx + TILE_W // 2, hy + TILE_H // 2
            for _ in range(22):
                angle = random.uniform(0, math.pi * 2)
                spd   = random.uniform(1.5, 6.0)
                self.particles.append(Particle(
                    cx, cy,
                    math.cos(angle) * spd, math.sin(angle) * spd,
                    random.randint(25, 55),
                    (255, random.randint(30, 80), random.randint(20, 60)),
                    random.randint(3, 7),
                ))
            return

        self.snake.insert(0, new_head)

        # Apple eaten?
        if (new_head[0] // TILE_W == self.apple_pos[0] // TILE_W and
                new_head[1] // TILE_H == self.apple_pos[1] // TILE_H):
            self.score += 1
            ax = self.apple_pos[0] + TILE_W // 2
            ay = self.apple_pos[1] + TILE_H // 2
            for _ in range(16):
                angle = random.uniform(0, math.pi * 2)
                spd   = random.uniform(1.5, 5.5)
                col   = random.choice([
                    (255, 80, 50), (255, 170, 60), (80, 255, 110), (255, 230, 60),
                ])
                self.particles.append(Particle(
                    ax, ay,
                    math.cos(angle) * spd, math.sin(angle) * spd,
                    random.randint(18, 38), col, random.randint(2, 5),
                ))
            self.popups.append(Popup('+1', ax, ay - 12))

            if self.score >= WIN_SCORE:
                self.won = True
                for _ in range(80):
                    px = random.randint(TILE_W, GAME_WIDTH - TILE_W)
                    py = random.randint(TILE_H, GAME_HEIGHT // 2)
                    spd  = random.uniform(2.0, 7.0)
                    ang  = random.uniform(0, math.pi * 2)
                    col  = (random.randint(80, 255),
                            random.randint(80, 255),
                            random.randint(80, 255))
                    self.particles.append(Particle(
                        px, py,
                        math.cos(ang) * spd, math.sin(ang) * spd,
                        random.randint(45, 90), col, random.randint(3, 6),
                    ))
            else:
                self._spawn_walls()
                self.apple_pos = self._new_apple()
        else:
            self.snake.pop()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _body_color(self, i: int) -> tuple:
        n = max(len(self.snake) - 1, 1)
        t = i / n
        r = int(C_SNAKE_HEAD[0] * (1 - t) + C_SNAKE_TAIL[0] * t)
        g = int(C_SNAKE_HEAD[1] * (1 - t) + C_SNAKE_TAIL[1] * t)
        b = int(C_SNAKE_HEAD[2] * (1 - t) + C_SNAKE_TAIL[2] * t)
        return (r, g, b)

    def _get_apple_glow(self, radius: int) -> pygame.Surface:
        if radius not in self._glow_cache:
            size = radius * 2 + 8
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            for layer in range(4):
                gr    = radius + layer * 3
                alpha = max(0, 55 - layer * 14)
                pygame.draw.circle(s, (255, 55, 35, alpha), (size // 2, size // 2), gr)
            self._glow_cache[radius] = s
        return self._glow_cache[radius]

    # ------------------------------------------------------------------
    # Draw: background + world
    # ------------------------------------------------------------------

    def _draw_walls(self) -> None:
        for wx, wy in self.walls:
            pygame.draw.rect(self.screen, C_WALL, (wx, wy, TILE_W, TILE_H))
            pygame.draw.line(self.screen, C_WALL_LT,
                             (wx, wy), (wx + TILE_W - 1, wy), 2)
            pygame.draw.line(self.screen, C_WALL_LT,
                             (wx, wy), (wx, wy + TILE_H - 1), 2)
            pygame.draw.line(self.screen, C_WALL_DK,
                             (wx, wy + TILE_H - 1), (wx + TILE_W - 1, wy + TILE_H - 1), 2)
            pygame.draw.line(self.screen, C_WALL_DK,
                             (wx + TILE_W - 1, wy), (wx + TILE_W - 1, wy + TILE_H - 1), 2)

    def _draw_apple(self) -> None:
        ax, ay = self.apple_pos
        cx, cy = ax + TILE_W // 2, ay + TILE_H // 2
        r = TILE_W // 2 - 1

        glow_r = r + 2 + int(2 * math.sin(self.frame * 0.11))
        gsurf  = self._get_apple_glow(glow_r)
        g_off  = glow_r + 4
        self.screen.blit(gsurf, (cx - g_off, cy - g_off))

        pygame.draw.circle(self.screen, C_APPLE, (cx, cy), r)
        pygame.draw.circle(self.screen, C_APPLE_HL,
                           (cx - r // 3, cy - r // 3), r // 3)
        pygame.draw.circle(self.screen, (255, 228, 210),
                           (cx - r // 3, cy - r // 3), max(1, r // 5))
        pygame.draw.rect(self.screen, C_LEAF, (cx - 1, ay + 1, 3, 5))
        pygame.draw.polygon(self.screen, C_LEAF, [
            (cx,     ay + 1),
            (cx + 6, ay - 3),
            (cx + 5, ay + 3),
        ])

    def _draw_snake(self) -> None:
        if not self.snake:
            return
        rad = TILE_W // 2 - 1

        for i in range(len(self.snake) - 1):
            ax, ay = self.snake[i]
            bx, by = self.snake[i + 1]
            gc = tuple(min(80, ch // 4) for ch in self._body_color(i))
            pygame.draw.line(self.screen, gc,
                             (ax + TILE_W//2, ay + TILE_H//2),
                             (bx + TILE_W//2, by + TILE_H//2),
                             (rad + 3) * 2)
        for i in range(len(self.snake) - 1, -1, -1):
            sx, sy = self.snake[i]
            gc = tuple(min(80, ch // 4) for ch in self._body_color(i))
            pygame.draw.circle(self.screen, gc,
                               (sx + TILE_W//2, sy + TILE_H//2), rad + 3)

        for i in range(len(self.snake) - 1):
            ax, ay = self.snake[i]
            bx, by = self.snake[i + 1]
            pygame.draw.line(self.screen, self._body_color(i),
                             (ax + TILE_W//2, ay + TILE_H//2),
                             (bx + TILE_W//2, by + TILE_H//2),
                             rad * 2)
        for i in range(len(self.snake) - 1, -1, -1):
            sx, sy = self.snake[i]
            pygame.draw.circle(self.screen, self._body_color(i),
                               (sx + TILE_W//2, sy + TILE_H//2), rad)

        half = max(1, len(self.snake) // 2)
        for i in range(half):
            sx, sy = self.snake[i]
            cx2, cy2 = sx + TILE_W//2, sy + TILE_H//2
            c  = self._body_color(i)
            hl = tuple(min(255, ch + 35) for ch in c)
            pygame.draw.circle(self.screen, hl, (cx2 - 2, cy2 - 2), max(1, rad // 2 - 1))

        hx, hy = self.snake[0]
        hcx, hcy = hx + TILE_W//2, hy + TILE_H//2
        dx, dy   = self.direction
        px, pe   = -dy, dx

        eye_off = int(rad * 0.55)
        eye_r   = max(2, rad // 3)
        fwd_off = int(rad * 0.28)
        for sign in (-1, 1):
            ex = int(hcx + dx * fwd_off + px * eye_off * sign)
            ey = int(hcy + dy * fwd_off + pe * eye_off * sign)
            pygame.draw.circle(self.screen, (240, 255, 210), (ex, ey), eye_r)
            pygame.draw.circle(self.screen, (8,   8,    8),
                               (ex + dx, ey + dy), max(1, eye_r - 1))
            pygame.draw.circle(self.screen, (255, 255, 255), (ex - 1, ey - 1), 1)

        if (self.frame % 30) < 14:
            base_x = int(hcx + dx * (rad + 3))
            base_y = int(hcy + dy * (rad + 3))
            root_x = int(hcx + dx * rad)
            root_y = int(hcy + dy * rad)
            pygame.draw.line(self.screen, C_TONGUE, (root_x, root_y), (base_x, base_y), 2)
            for sign in (-1, 1):
                tip_x = int(base_x + dx * 5 + px * sign * 3)
                tip_y = int(base_y + dy * 5 + pe * sign * 3)
                pygame.draw.line(self.screen, C_TONGUE, (base_x, base_y), (tip_x, tip_y), 2)

    def _draw_particles(self) -> None:
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            p.draw(self.screen)

    def _draw_popups(self) -> None:
        self.popups = [p for p in self.popups if p.update()]
        for p in self.popups:
            p.draw(self.screen)

    # ------------------------------------------------------------------
    # Draw: HUD
    # ------------------------------------------------------------------

    def _draw_hud(self) -> None:
        lbl = self._f_hud.render(f'{self.score} / {WIN_SCORE}', True, C_HUD)
        self.screen.blit(lbl, lbl.get_rect(center=(GAME_WIDTH // 2, 18)))

        # Seed display — top-right corner
        seed_lbl = self._f_hud.render(f'#{self.seed}', True, (55, 75, 55))
        self.screen.blit(seed_lbl, (GAME_WIDTH - seed_lbl.get_width() - 8, 6))

    def _draw_overlay(self) -> None:
        if not (self.game_over or self.won):
            return

        self.screen.blit(self._overlay, (0, 0))

        if self.won:
            title = self._f_big.render('YOU WIN!', True, (100, 255, 110))
            hint  = self._f_hint.render('Press ENTER to continue', True, (160, 220, 160))
        else:
            title = self._f_big.render('GAME OVER', True, (255, 75, 55))
            hint  = self._f_hint.render(
                f'Score: {self.score} / {WIN_SCORE}   ·   Press ENTER',
                True, (200, 155, 155))

        self.screen.blit(title, title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 44)))
        self.screen.blit(hint,  hint.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 26)))

    # ------------------------------------------------------------------
    # Pause menu
    # ------------------------------------------------------------------

    def _pause_menu(self) -> str:
        """Runs pause overlay. Returns 'resume', 'save_quit', or 'quit'."""
        snapshot = self.screen.copy()
        overlay  = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 168))

        f_title = pygame.font.SysFont('segoeui', 52, bold=True)
        f_btn   = pygame.font.SysFont('segoeui', 34, bold=True)

        cx = GAME_WIDTH  // 2
        cy = GAME_HEIGHT // 2

        buttons = [
            {'label': 'RESUME',      'rect': pygame.Rect(0, 0, 300, 60), 'action': 'resume'},
            {'label': 'SAVE & QUIT', 'rect': pygame.Rect(0, 0, 300, 60), 'action': 'save_quit'},
            {'label': 'QUIT',        'rect': pygame.Rect(0, 0, 300, 60), 'action': 'quit'},
        ]
        for i, b in enumerate(buttons):
            b['rect'].center = (cx, cy - 10 + i * 80)

        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'resume'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx = (event.pos[0] - self.offset_x) / self.scale
                    my = (event.pos[1] - self.offset_y) / self.scale
                    for b in buttons:
                        if b['rect'].collidepoint(mx, my):
                            return b['action']

            self.screen.blit(snapshot, (0, 0))
            self.screen.blit(overlay,  (0, 0))

            title = f_title.render('PAUSED', True, (210, 220, 255))
            self.screen.blit(title, title.get_rect(center=(cx, cy - 140)))

            raw_mx, raw_my = pygame.mouse.get_pos()
            hov_mx = (raw_mx - self.offset_x) / self.scale
            hov_my = (raw_my - self.offset_y) / self.scale
            for b in buttons:
                hov   = b['rect'].collidepoint(hov_mx, hov_my)
                bg_c  = (38, 48, 72) if hov else (16, 20, 34)
                rim_c = (110, 130, 200) if hov else (42, 52, 80)
                lbl_c = (220, 228, 255) if hov else (120, 140, 185)
                pygame.draw.rect(self.screen, bg_c,  b['rect'], border_radius=12)
                pygame.draw.rect(self.screen, rim_c, b['rect'], 2, border_radius=12)
                lbl = f_btn.render(b['label'], True, lbl_c)
                self.screen.blit(lbl, lbl.get_rect(center=b['rect'].center))

            self._present()
            clock.tick(60)

    # ------------------------------------------------------------------
    # Present
    # ------------------------------------------------------------------

    def _present(self) -> None:
        self.display_screen.fill((0, 0, 0))
        scaled = pygame.transform.scale(
            self.screen,
            (int(GAME_WIDTH * self.scale), int(GAME_HEIGHT * self.scale)),
        )
        self.display_screen.blit(scaled, (self.offset_x, self.offset_y))
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> str:
        while True:
            self.frame += 1
            action = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    res = self._handle_keydown(event.key)
                    if res:
                        action = res

            if action == 'pause':
                result = self._pause_menu()
                if result == 'save_quit':
                    _ss.save(self._save_state())
                    return 'menu'
                elif result == 'quit':
                    _ss.delete()
                    return 'menu'
                # 'resume' → continue
            elif action:
                return action

            if not (self.game_over or self.won):
                self.move_timer += 1
                if self.move_timer >= self._move_delay():
                    self.move_timer = 0
                    self._step()

            # ── Draw ──
            self.screen.blit(self._bg, (0, 0))
            self._draw_walls()
            self._draw_apple()
            self._draw_snake()
            self._draw_particles()
            self._draw_popups()
            self._draw_hud()
            self._draw_overlay()
            self._present()

            self.clock.tick(60)


# ---------------------------------------------------------------------------
# Snake main menu
# ---------------------------------------------------------------------------

def _snake_menu(screen: pygame.Surface) -> tuple[str, str, dict | None]:
    """Returns (action, seed, save_data).
    action is 'play', 'continue', 'quit', or 'menu'.
    """
    dw, dh  = screen.get_size()
    scale   = min(dw / GAME_WIDTH, dh / GAME_HEIGHT)
    off_x   = int((dw - GAME_WIDTH  * scale) // 2)
    off_y   = int((dh - GAME_HEIGHT * scale) // 2)
    surf    = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    f_title  = pygame.font.SysFont('segoeui', 96, bold=True)
    f_btn    = pygame.font.SysFont('segoeui', 38, bold=True)
    f_sub    = pygame.font.SysFont('segoeui', 20)
    f_seed   = pygame.font.SysFont('consolas', 26, bold=True)
    f_slabel = pygame.font.SysFont('segoeui', 16)

    # Bake background once
    bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    for gx in range(GRID_TILES_X):
        for gy in range(GRID_TILES_Y):
            n = (gx * 73856093 ^ gy * 19349663) & 0xFFFFFF
            n = ((n ^ (n >> 13)) * 1664525 + 1013904223) & 0xFFFFFF
            v = (n & 0xFF) / 255.0
            r = min(255, C_BG[0] + int(v * 4))
            g = min(255, C_BG[1] + int(v * 5))
            b = min(255, C_BG[2] + int(v * 7))
            pygame.draw.rect(bg, (r, g, b), (gx * TILE_W, gy * TILE_H, TILE_W, TILE_H))
    for x in range(0, GAME_WIDTH + 1, TILE_W):
        pygame.draw.line(bg, C_GRID, (x, 0), (x, GAME_HEIGHT))
    for y in range(0, GAME_HEIGHT + 1, TILE_H):
        pygame.draw.line(bg, C_GRID, (0, y), (GAME_WIDTH, y))

    cx = GAME_WIDTH  // 2
    cy = GAME_HEIGHT // 2

    has_save = _ss.has_save()
    seed_str = _ss.new_seed()

    # Build button list
    def _make_buttons():
        btns = []
        if _ss.has_save():
            btns.append({'label': 'CONTINUE', 'rect': pygame.Rect(0, 0, 260, 64), 'action': 'continue'})
        btns.append({'label': 'PLAY',     'rect': pygame.Rect(0, 0, 260, 64), 'action': 'play'})
        btns.append({'label': 'QUIT',     'rect': pygame.Rect(0, 0, 260, 64), 'action': 'quit'})
        # Position buttons below seed field
        btn_top = cy + 50
        for i, b in enumerate(btns):
            b['rect'].center = (cx, btn_top + i * 86)
        return btns

    buttons  = _make_buttons()
    seed_rect = pygame.Rect(cx - 110, cy - 26, 220, 48)
    seed_active = False
    cursor_vis  = True
    cursor_tick = 0

    clock = pygame.time.Clock()
    frame = 0

    while True:
        frame += 1
        cursor_tick += 1
        if cursor_tick >= 30:
            cursor_tick = 0
            cursor_vis = not cursor_vis

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ('quit', seed_str, None)
            if event.type == pygame.KEYDOWN:
                if seed_active:
                    if event.key == pygame.K_ESCAPE:
                        seed_active = False
                    elif event.key == pygame.K_RETURN:
                        seed_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        seed_str = seed_str[:-1]
                    else:
                        ch = event.unicode.upper()
                        if ch and ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' and len(seed_str) < 6:
                            seed_str += ch
                else:
                    if event.key == pygame.K_ESCAPE:
                        return ('menu', seed_str, None)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return ('play', seed_str, None)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx = (event.pos[0] - off_x) / scale
                my = (event.pos[1] - off_y) / scale
                if seed_rect.collidepoint(mx, my):
                    seed_active = True
                    cursor_vis  = True
                    cursor_tick = 0
                else:
                    seed_active = False
                    for b in buttons:
                        if b['rect'].collidepoint(mx, my):
                            action = b['action']
                            if action == 'continue':
                                save_data = _ss.load()
                                saved_seed = save_data.get('seed', seed_str) if save_data else seed_str
                                return ('continue', saved_seed, save_data)
                            return (action, seed_str, None)

        surf.blit(bg, (0, 0))

        # Title — pulsing green
        pulse = 0.5 + 0.5 * math.sin(frame * 0.05)
        tc = tuple(int(c * (0.82 + 0.18 * pulse)) for c in C_SNAKE_HEAD)
        title_surf = f_title.render('SNAKE', True, tc)
        surf.blit(title_surf, title_surf.get_rect(center=(cx, cy - 150)))

        # Seed field
        seed_bg   = (22, 40, 26) if seed_active else (14, 24, 16)
        seed_rim  = C_SNAKE_HEAD if seed_active else (38, 75, 48)
        pygame.draw.rect(surf, seed_bg,  seed_rect, border_radius=8)
        pygame.draw.rect(surf, seed_rim, seed_rect, 2, border_radius=8)

        seed_label = f_slabel.render('SEED', True, (55, 90, 60))
        surf.blit(seed_label, (seed_rect.x + 6, seed_rect.y - 18))

        display_seed = seed_str + ('|' if seed_active and cursor_vis else '')
        seed_surf = f_seed.render(display_seed or ' ', True, C_SNAKE_HEAD if seed_active else (140, 200, 150))
        surf.blit(seed_surf, seed_surf.get_rect(center=seed_rect.center))

        # Buttons
        raw_mx, raw_my = pygame.mouse.get_pos()
        hov_mx = (raw_mx - off_x) / scale
        hov_my = (raw_my - off_y) / scale
        for b in buttons:
            hov   = b['rect'].collidepoint(hov_mx, hov_my)
            is_cont = b['action'] == 'continue'
            bg_c  = (28, 55, 32) if (hov and not is_cont) else (28, 45, 55) if (hov and is_cont) else (14, 26, 18)
            rim_c = C_SNAKE_HEAD if (hov and not is_cont) else (80, 160, 220) if (hov and is_cont) else (38, 75, 48)
            lbl_c = C_HUD if hov else (100, 150, 110)
            if is_cont:
                lbl_c = (140, 200, 255) if hov else (80, 130, 170)
            pygame.draw.rect(surf, bg_c,  b['rect'], border_radius=12)
            pygame.draw.rect(surf, rim_c, b['rect'], 2, border_radius=12)
            lbl = f_btn.render(b['label'], True, lbl_c)
            surf.blit(lbl, lbl.get_rect(center=b['rect'].center))

        # Controls hint
        hint = f_sub.render('Arrow keys / WASD   ·   ESC to exit', True, (38, 55, 40))
        surf.blit(hint, hint.get_rect(center=(cx, GAME_HEIGHT - 28)))

        screen.fill((0, 0, 0))
        scaled = pygame.transform.scale(
            surf, (int(GAME_WIDTH * scale), int(GAME_HEIGHT * scale))
        )
        screen.blit(scaled, (off_x, off_y))
        pygame.display.flip()
        clock.tick(60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(screen: pygame.Surface) -> str:
    while True:
        action, seed, save_data = _snake_menu(screen)
        if action in ('quit', 'menu'):
            return action
        if action == 'continue' and save_data:
            game = SnakeGame(screen, seed=seed, save_data=save_data)
        else:
            _ss.delete()           # clear any stale save when starting fresh
            game = SnakeGame(screen, seed=seed)
        result = game.run()
        if result in ('quit', 'menu'):
            return result
        # 'restart' or 'won' → back to menu
