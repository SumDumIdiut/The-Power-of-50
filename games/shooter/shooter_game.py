"""
Shooter Game — Kill 50 enemies
Top-down auto-shooter with procedurally generated dungeon.
All visuals use pygame primitives — no external sprite assets.

Improvements:
- Distinct per-enemy graphics & unique attack sets
- Per-boss unique attack patterns per level
- Seamless wall textures via noise-seeded variation
- Enemy spawn validation (never inside walls)
- Crate power-up drops with icons
- Kill counter in HUD
- Cool boss health bar with segments & name
- Polished power-up panel UI
"""
from __future__ import annotations

import math
import random
import os

import pygame

# Ensure this package's own directory is resolved first,
# without polluting sys.path in a way that grabs sibling packages.
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))

def _pkg_import(name: str):
    """Import a module by absolute file path from this package's directory."""
    import importlib.util
    path = os.path.join(_PKG_DIR, name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_tilemap_mod      = _pkg_import("tilemap")
_wall_renderer_mod = _pkg_import("wall_renderer")
_helpers_mod      = _pkg_import("helpers")
_save_mod         = _pkg_import("shooter_save")

Tilemap      = _tilemap_mod.Tilemap
MapGenerator = _tilemap_mod.MapGenerator
WallRenderer = _wall_renderer_mod.WallRenderer

distance_sq        = _helpers_mod.distance_sq
normalize          = _helpers_mod.normalize
angle_lerp         = _helpers_mod.angle_lerp
angle_of           = _helpers_mod.angle_of
spread_directions  = _helpers_mod.spread_directions
ring_directions    = _helpers_mod.ring_directions
circles_overlap    = _helpers_mod.circles_overlap
rect_plane_overlap = _helpers_mod.rect_plane_overlap
has_line_of_sight  = _helpers_mod.has_line_of_sight
random_open_position = _helpers_mod.random_open_position
is_off_screen      = _helpers_mod.is_off_screen
clamp              = _helpers_mod.clamp

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VIEWPORT_W       = 1600
VIEWPORT_H       = 900
WORLD_SIZE       = 18000
TILE_SIZE        = 40
CHUNK_SIZE       = 500
WIN_KILLS        = 9999   # effectively endless survival

MAX_ENEMIES      = 30
SPAWN_DELAY_BASE = 150
SPAWN_DELAY_MIN  = 20
SPAWN_KILLS_STEP = 3

# Mega-boss spawns every this many kills
MEGA_BOSS_INTERVAL = 50
# Mini-boss spawns every this many kills
MINI_BOSS_INTERVAL = 10

# Palette
C_BG           = (18,  18,  32)
C_GRID         = (28,  28,  48)
C_PLAYER       = (60, 160, 255)
C_PLAYER_CORE  = (180, 230, 255)
C_PLAYER_EDGE  = (255, 255, 255)
C_GUN          = (255, 210,  60)
C_ORBITAL      = (255, 210,   0)
C_ORBITAL_RIM  = (255, 100,   0)
C_BULLET       = (255, 255,  80)
C_BULLET_BOUNCE= (0,   255, 220)
C_BULLET_PIERCE= (220,  60, 255)
C_EBULLET      = (255,  60,  60)
C_ECANNON      = (255, 140,  40)
C_WHITE        = (255, 255, 255)
C_GREY         = (160, 160, 160)
C_PANEL_BG     = (12,  14,  28, 210)
C_PANEL_EDGE   = (80,  110, 160)
C_HEALTH_GREEN = (60,  240,  80)
C_HEALTH_YEL   = (255, 210,  50)
C_HEALTH_RED   = (255,  60,  60)

# Enemy palettes
ENEMY_STYLES = {
    'normal':  {'body': (220, 55, 55),   'rim': (255, 120, 120), 'dark': (140, 20, 20)},
    'fast':    {'body': (255, 200, 40),  'rim': (255, 240, 140), 'dark': (180, 120, 0)},
    'tank':    {'body': (80,  100, 180), 'rim': (160, 180, 255), 'dark': (40, 50, 110)},
    'shooter': {'body': (60,  200, 100), 'rim': (140, 255, 160), 'dark': (20, 100, 40)},
}
BOSS_STYLES = {
    1: {'body': (180,  30, 200), 'rim': (255, 100, 255), 'dark': (80, 0, 100),   'name': 'VOIDCALLER'},
    2: {'body': (200,  80,  20), 'rim': (255, 200,  60), 'dark': (120, 30, 0),   'name': 'INFERNAX'},
    3: {'body': ( 20, 160, 180), 'rim': ( 80, 240, 255), 'dark': (10, 80, 100),  'name': 'GLACIUS'},
    4: {'body': (160, 160,  20), 'rim': (255, 255, 100), 'dark': (80, 80, 0),    'name': 'SOLARCH'},
    5: {'body': (220,  20,  60), 'rim': (255, 120, 140), 'dark': (120, 0, 30),   'name': 'NECRAXIS'},
    6: {'body': ( 20,  80, 220), 'rim': (100, 180, 255), 'dark': (10, 30, 120),  'name': 'ABYSSTIDE'},
    7: {'body': (180, 140,  20), 'rim': (255, 220,  80), 'dark': (90, 70, 0),    'name': 'WRATHBORN'},
    8: {'body': ( 20, 200,  80), 'rim': ( 80, 255, 160), 'dark': (10, 100, 40),  'name': 'VIRULEX'},
}
BOSS_FINAL_STYLE = {'body': (220, 0, 80), 'rim': (255, 80, 180), 'dark': (100, 0, 40), 'name': 'OMEGA PRIME'}

# Item visual config
ITEM_CONFIG = {
    # Standard drops
    'firerate':  {'color': (255, 100, 255), 'name': '+Fire Rate',    'desc': 'FASTER',   'icon': 'firerate'},
    'multishot': {'color': (100, 200, 255), 'name': '+Multi-Shot',   'desc': 'SPREAD',   'icon': 'multishot'},
    'damage':    {'color': (255, 150,  50), 'name': '+Damage',       'desc': 'POWER',    'icon': 'damage'},
    'bounce':    {'color': (  0, 255, 220), 'name': '+Bounce',       'desc': 'RICOH',    'icon': 'bounce'},
    'pierce':    {'color': (220,  60, 255), 'name': '+Pierce',       'desc': 'PIERCE',   'icon': 'pierce'},
    'speed':     {'color': (100, 255, 100), 'name': '+Speed',        'desc': 'SWIFT',    'icon': 'speed'},
    'steady':    {'color': (180, 255, 180), 'name': '+Steady Aim',    'desc': 'STEADY',   'icon': 'steady'},
    # Consumable
    'health':    {'color': ( 80, 220,  80), 'name': '+1 Health',      'desc': 'HEAL',     'icon': 'health'},
    # Boss-only drops
    'orbital':   {'color': (255, 210,   0), 'name': 'ORBITAL SAW',   'desc': 'ORBITAL',  'icon': 'orbital'},
    'dual_gun':  {'color': (255, 100, 100), 'name': 'DUAL GUN',      'desc': 'DUAL',     'icon': 'dual_gun'},
    'explode':   {'color': (255, 160,  30), 'name': 'EXPLOSIVE RDS', 'desc': 'BOOM',     'icon': 'explode'},
    'magnet':    {'color': (100, 200, 255), 'name': 'MAGNET',        'desc': 'PULL',     'icon': 'magnet'},
}


# ---------------------------------------------------------------------------
# Noise helper for seamless textures
# ---------------------------------------------------------------------------

def _hash2(x: int, y: int) -> float:
    """Deterministic pseudo-random float [0,1] from grid coords."""
    n = x * 73856093 ^ y * 19349663
    n = (n ^ (n >> 13)) * 1664525 + 1013904223
    return ((n & 0xFFFFFF) / 0xFFFFFF)


# ---------------------------------------------------------------------------
# Wall
# ---------------------------------------------------------------------------

class Wall:
    PLANE_THICKNESS = 5

    def __init__(self, x, y, w, h, has_left, has_right, has_top, has_bottom):
        self.x, self.y, self.width, self.height = x, y, w, h
        pt = self.PLANE_THICKNESS
        self.left_plane   = (x - pt, y,     pt, h) if not has_left   else None
        self.right_plane  = (x + w,  y,     pt, h) if not has_right  else None
        self.top_plane    = (x,      y - pt, w, pt) if not has_top    else None
        self.bottom_plane = (x,      y + h,  w, pt) if not has_bottom else None

    def collides(self, cx, cy, size):
        return (rect_plane_overlap(self.left_plane,   cx, cy, size) or
                rect_plane_overlap(self.right_plane,  cx, cy, size) or
                rect_plane_overlap(self.top_plane,    cx, cy, size) or
                rect_plane_overlap(self.bottom_plane, cx, cy, size))

    def is_visible(self, cam_x, cam_y, sw, sh, buf=50):
        sx, sy = self.x - cam_x, self.y - cam_y
        return (sx + self.width  > -buf and sx < sw + buf and
                sy + self.height > -buf and sy < sh + buf)


# ---------------------------------------------------------------------------
# Chunk Manager
# ---------------------------------------------------------------------------

class ChunkManager:
    def __init__(self, world_size: int, chunk_size: int = CHUNK_SIZE) -> None:
        self.world_size  = world_size
        self.chunk_size  = chunk_size
        self.all_walls:   list[Wall] = []
        self.wall_chunks: dict[tuple, list] = {}
        self.loaded_chunks: set[tuple] = set()
        self.tilemap     = Tilemap(tile_size=TILE_SIZE)
        self.rooms:       list[tuple] = []
        self.no_spawn_zones: set[tuple] = set()

    def generate_map(self) -> None:
        gen = MapGenerator(self.tilemap, self.world_size)
        self.rooms, self.no_spawn_zones = gen.generate()
        self._build_walls()

    def _build_walls(self) -> None:
        ts = self.tilemap.tile_size
        tiles = self.tilemap.get_all_tiles()
        visited: set[tuple] = set()
        for gx, gy in tiles:
            if (gx, gy) in visited:
                continue
            hl = self.tilemap.has_tile(gx - 1, gy)
            hr = self.tilemap.has_tile(gx + 1, gy)
            ht = self.tilemap.has_tile(gx, gy - 1)
            hb = self.tilemap.has_tile(gx, gy + 1)
            pat = (hl, hr, ht, hb)
            w = 1
            while w < 3 and (gx + w, gy) not in visited and self.tilemap.has_tile(gx + w, gy):
                np = (self.tilemap.has_tile(gx+w-1,gy), self.tilemap.has_tile(gx+w+1,gy),
                      self.tilemap.has_tile(gx+w,gy-1), self.tilemap.has_tile(gx+w,gy+1))
                if np == pat: w += 1
                else: break
            h = 1
            while h < 3:
                ok = True
                for dx in range(w):
                    if (gx+dx, gy+h) in visited or not self.tilemap.has_tile(gx+dx, gy+h):
                        ok = False; break
                    rp = (self.tilemap.has_tile(gx+dx-1,gy+h), self.tilemap.has_tile(gx+dx+1,gy+h),
                          self.tilemap.has_tile(gx+dx,gy+h-1), self.tilemap.has_tile(gx+dx,gy+h+1))
                    if rp != pat: ok = False; break
                if ok: h += 1
                else: break
            for dx in range(w):
                for dy in range(h):
                    visited.add((gx+dx, gy+dy))
            self.all_walls.append(Wall(gx*ts, gy*ts, w*ts, h*ts, hl, hr, ht, hb))

    def load_chunks_around(self, x, y):
        cx, cy = int(x // self.chunk_size), int(y // self.chunk_size)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                key = (cx+dx, cy+dy)
                if key not in self.loaded_chunks:
                    self._load_chunk(key)

    def _load_chunk(self, key):
        cx, cy = key
        ox, oy = cx * self.chunk_size, cy * self.chunk_size
        cs = self.chunk_size
        self.wall_chunks[key] = [
            w for w in self.all_walls
            if (w.x < ox+cs and w.x+w.width > ox and w.y < oy+cs and w.y+w.height > oy)
        ]
        self.loaded_chunks.add(key)

    def unload_distant(self, x, y):
        cx, cy = int(x//self.chunk_size), int(y//self.chunk_size)
        stale = [k for k in self.loaded_chunks if abs(k[0]-cx)>4 or abs(k[1]-cy)>4]
        for k in stale:
            self.wall_chunks.pop(k, None)
            self.loaded_chunks.discard(k)

    def get_nearby_walls(self, x, y):
        cx, cy = int(x//self.chunk_size), int(y//self.chunk_size)
        seen: set[int] = set()
        result = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk = self.wall_chunks.get((cx+dx, cy+dy))
                if chunk:
                    for w in chunk:
                        wid = id(w)
                        if wid not in seen:
                            seen.add(wid)
                            result.append(w)
        return result

    def get_visible_walls(self, cam_x, cam_y, sw, sh):
        cx, cy = int(cam_x//self.chunk_size), int(cam_y//self.chunk_size)
        wide  = sw // self.chunk_size + 2
        tall  = sh // self.chunk_size + 2
        seen: set[int] = set()
        result = []
        for dx in range(wide+1):
            for dy in range(tall+1):
                chunk = self.wall_chunks.get((cx+dx, cy+dy))
                if chunk:
                    for w in chunk:
                        wid = id(w)
                        if wid not in seen and w.is_visible(cam_x, cam_y, sw, sh):
                            seen.add(wid)
                            result.append(w)
        return result

    def has_los(self, x1, y1, x2, y2):
        mid_x, mid_y = (x1+x2)*0.5, (y1+y2)*0.5
        walls = self.get_nearby_walls(mid_x, mid_y)
        return has_line_of_sight(x1, y1, x2, y2, walls)

    def is_pos_safe(self, px: float, py: float, radius: float = 24.0) -> bool:
        """Return True if a circle at (px,py) with given radius doesn't overlap any wall tile."""
        return not self.tilemap.check_collision(px, py, radius)

    def get_random_open_pos(self, safety: int = 3) -> tuple[float, float]:
        ts = self.tilemap.tile_size
        gw = self.world_size // ts
        gh = self.world_size // ts
        pos = random_open_position(self.no_spawn_zones, gw, gh, ts, safety)
        if pos:
            # Extra pixel-level validation
            if self.is_pos_safe(pos[0], pos[1], 24):
                return pos
        # Fallback: room centres
        if self.rooms:
            random.shuffle(self.rooms)
            for r in self.rooms:
                cx, cy = r[0] + r[2]//2, r[1] + r[3]//2
                if self.is_pos_safe(cx, cy, 24):
                    return (cx, cy)
        return (self.world_size // 2, self.world_size // 2)

    def get_safe_pos_near_room(self) -> tuple[float, float]:
        """Return a verified safe spawn inside a random room."""
        if self.rooms:
            random.shuffle(self.rooms)
            for room in self.rooms:
                rx, ry, rw, rh = room
                for _ in range(20):
                    tx = rx + random.randint(rw//4, 3*rw//4)
                    ty = ry + random.randint(rh//4, 3*rh//4)
                    if self.is_pos_safe(tx, ty, 24):
                        return (tx, ty)
        return self.get_random_open_pos()


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    SIZE          = 20
    BASE_SPEED    = 5
    BASE_FIRE_RATE= 30
    BASE_DAMAGE   = 5
    MAX_HEALTH    = 10

    def __init__(self, x, y):
        self.x, self.y  = float(x), float(y)
        self.health      = self.MAX_HEALTH
        self.speed       = float(self.BASE_SPEED)
        self.fire_rate   = self.BASE_FIRE_RATE
        self.damage      = self.BASE_DAMAGE
        self.multi_shot  = 1
        self.bullet_bounce = 0
        self.bullet_pierce = 0
        self.has_orbital   = False
        self.orbital_angle = 0.0
        self.has_dual_gun  = False
        self.orbital_count = 0
        self.dual_gun_count= 0
        self.bullet_explode= 0   # explosion radius stacks
        self.magnet_count  = 0   # stacks: each adds pull range
        self.magnet_angle  = 0.0
        self.magnet_target_angle = 0.0
        self.steady_aim    = 0   # reduces inaccuracy and speeds up aim lerp
        self.shoot_dir     = [0.0, -1.0]
        self.has_target    = False
        self.invincible    = 0   # invincibility frames after hit
        self.thruster_anim = 0.0

    def move(self, keys, chunk_manager: ChunkManager):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx != 0 or dy != 0:
            self.thruster_anim += 0.18  # faster pulse while moving

        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed
        walls = chunk_manager.get_nearby_walls(self.x, self.y)
        if nx != self.x and not any(w.collides(nx, self.y, self.SIZE) for w in walls):
            self.x = nx
        if ny != self.y and not any(w.collides(self.x, ny, self.SIZE) for w in walls):
            self.y = ny
        ws = chunk_manager.world_size
        self.x = clamp(self.x, self.SIZE, ws - self.SIZE)
        self.y = clamp(self.y, self.SIZE, ws - self.SIZE)
        if self.invincible > 0:
            self.invincible -= 1

    def update_aim(self, enemies):
        if not enemies:
            self.has_target = False
            return
        nearest = min(enemies, key=lambda e: distance_sq(self.x, self.y, e.x, e.y))
        dx, dy = nearest.x - self.x, nearest.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0: return
        target_angle  = angle_of(dx, dy)
        current_angle = angle_of(self.shoot_dir[0], self.shoot_dir[1])
        # Lerp speed increases with steady_aim; base aim wanders a bit
        lerp_t = min(0.95, 0.12 + self.steady_aim * 0.10)
        # Add angular noise that decreases with steady_aim
        wobble = 0.04 * max(0.0, 1.0 - self.steady_aim * 0.25)
        noise = random.uniform(-wobble, wobble)
        new_angle = angle_lerp(current_angle, target_angle + noise, lerp_t)
        self.shoot_dir = [math.cos(new_angle), math.sin(new_angle)]
        self.has_target = True

    def update_orbital(self):
        if self.has_orbital:
            self.orbital_angle += 0.1

    def take_damage(self, amount: int) -> bool:
        """Apply damage. Returns True if actually hurt."""
        if self.invincible > 0:
            return False
        self.health -= amount
        self.invincible = 20
        return True

    def draw(self, screen: pygame.Surface, cam_x, cam_y, frame: int = 0):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        angle = angle_of(self.shoot_dir[0], self.shoot_dir[1])

        # Always tick thruster so idle engine pulses too
        self.thruster_anim += 0.18

        ca = math.cos(angle)
        sa = math.sin(angle)

        def rot(lx, ly):
            return (int(sx + lx*ca - ly*sa), int(sy + lx*sa + ly*ca))

        def rpts(*pts):
            return [rot(lx, ly) for lx, ly in pts]

        flash = self.invincible > 0 and (frame // 3) % 2 == 0

        # ── Engine exhaust flames (drawn first, behind everything) ──
        for ny in (-5, 0, 5):
            pulse = 0.45 + 0.55 * math.sin(self.thruster_anim * 3.2 + ny * 0.28)
            nozzle = rot(-20, ny)
            pygame.draw.circle(screen, (38, 44, 60), nozzle, 4)
            for fi in range(1, 4):
                fl = int(fi * 5 * pulse)
                fp = rot(-20 - fl, ny)
                fc = (max(8, 25 - fi*6), max(55, 95 - fi*14), min(255, 175 + fi*22))
                pygame.draw.circle(screen, fc, fp, max(1, 4 - fi))

        # ── Left shoulder plate ──
        lsh = rpts((-10, 12), (-4, 19), (6, 18), (8, 12), (2, 10))
        pygame.draw.polygon(screen, (56, 48, 38) if not flash else (255,255,255), lsh)
        pygame.draw.polygon(screen, (102, 88, 66), lsh, 2)
        # shoulder bolt detail
        pygame.draw.circle(screen, (80, 70, 54), rot(2, 15), 2)

        # ── Right shoulder plate ──
        rsh = rpts((-10,-12), (-4,-19), (6,-18), (8,-12), (2,-10))
        pygame.draw.polygon(screen, (56, 48, 38) if not flash else (255,255,255), rsh)
        pygame.draw.polygon(screen, (102, 88, 66), rsh, 2)
        pygame.draw.circle(screen, (80, 70, 54), rot(2, -15), 2)

        # ── Main hull ──
        hull = rpts((-18,0), (-15,-9), (-4,-13), (6,-11), (6,11), (-4,13), (-15,9))
        pygame.draw.polygon(screen, (48, 56, 80) if not flash else (220,230,255), hull)
        pygame.draw.polygon(screen, (92, 108, 152), hull, 2)
        # armor panel etch lines
        if not flash:
            pygame.draw.line(screen, (36, 42, 60), rot(-13,-5), rot(3,-8), 1)
            pygame.draw.line(screen, (36, 42, 60), rot(-13, 5), rot(3,  8), 1)
            pygame.draw.line(screen, (36, 42, 60), rot(-8,  0), rot(-2, 0), 1)

        # ── Front chest plate ──
        chest = rpts((4,-10), (4,10), (14,6), (16,0), (14,-6))
        pygame.draw.polygon(screen, (65, 88, 136) if not flash else (255,255,255), chest)
        pygame.draw.polygon(screen, (108, 140, 200), chest, 2)

        # ── Cockpit lens ──
        cock = rot(5, 0)
        pygame.draw.circle(screen, (18, 175, 228) if not flash else (255,255,255), cock, 6)
        pygame.draw.circle(screen, (120, 225, 255), cock, 4)
        pygame.draw.circle(screen, (210, 248, 255), cock, 2)

        # ── Main cannon ──
        barrel = rpts((14,-4), (14,4), (27,3), (27,-3))
        pygame.draw.polygon(screen, (60, 54, 46) if not flash else (255,255,255), barrel)
        pygame.draw.polygon(screen, (105, 96, 80), barrel, 1)
        # segment rings
        for cx_l in (18, 22):
            pygame.draw.line(screen, (88, 80, 68), rot(cx_l, -3), rot(cx_l, 3), 1)
        # muzzle ring
        pygame.draw.circle(screen, (78, 70, 58), rot(27, 0), 4)
        # glowing tip
        tip_pulse = 0.7 + 0.3 * math.sin(self.thruster_anim * 4.0)
        tip = rot(27, 0)
        pygame.draw.circle(screen, (255, int(190 + 50*tip_pulse), 40), tip, 3)
        pygame.draw.circle(screen, (255, 240, 160), tip, 1)

        # ── Dual side guns (one pair per stack) ──
        if self.has_dual_gun:
            for gn in range(self.dual_gun_count):
                off = 10 + gn * 10
                for sign in (-1, 1):
                    sy2 = sign * off
                    side = rpts((8,sy2-2),(8,sy2+2),(22,sy2+1),(22,sy2-1))
                    pygame.draw.polygon(screen, (60, 54, 46) if not flash else (255,255,255), side)
                    pygame.draw.polygon(screen, (95, 86, 72), side, 1)
                    stip = rot(22, sy2)
                    pygame.draw.circle(screen, (255, 170, 30), stip, 3)


    def draw_orbital(self, screen: pygame.Surface, cam_x, cam_y, frame: int = 0):
        if not self.has_orbital:
            return
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        count = min(self.orbital_count, 8)
        for i in range(count):
            a = self.orbital_angle + i * 2 * math.pi / count
            ox = int(sx + math.cos(a) * 55)
            oy = int(sy + math.sin(a) * 55)
            # Saw body
            pygame.draw.circle(screen, C_ORBITAL, (ox, oy), 13)
            pygame.draw.circle(screen, C_ORBITAL_RIM, (ox, oy), 13, 2)
            # Spinning teeth
            spin = frame * 0.18 + i
            for j in range(6):
                ba = spin + j * math.pi / 3
                pygame.draw.line(screen, (255, 240, 100),
                                 (int(ox + math.cos(ba)*9), int(oy + math.sin(ba)*9)),
                                 (int(ox + math.cos(ba)*13), int(oy + math.sin(ba)*13)), 2)

    def update_magnet(self, items: list):
        if not self.magnet_count:
            return
        PULL_RANGE = 200.0 + self.magnet_count * 120.0   # 320, 440, 560... per stack
        PULL_SPEED = 3.5 + self.magnet_count * 0.5
        nearest_dist = float('inf')
        nearest_angle = self.magnet_angle
        for item in items:
            dx, dy = item.x - self.x, item.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < PULL_RANGE and dist > 0:
                # Pull crate toward player
                item.x -= dx / dist * PULL_SPEED
                item.y -= dy / dist * PULL_SPEED
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_angle = math.atan2(dy, dx)
        # Orbit slowly, but snap toward nearest crate when one is in range
        if nearest_dist < PULL_RANGE:
            self.magnet_angle = angle_lerp(self.magnet_angle, nearest_angle, 0.12)
        else:
            self.magnet_angle += 0.04

    def draw_magnet(self, screen: pygame.Surface, cam_x, cam_y):
        if not self.magnet_count:
            return
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        ORBIT_R = 38
        mx = int(sx + math.cos(self.magnet_angle) * ORBIT_R)
        my = int(sy + math.sin(self.magnet_angle) * ORBIT_R)

        # Glow (cached)
        if not hasattr(self, '_magnet_glow'):
            self._magnet_glow = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self._magnet_glow, (100, 200, 255, 50), (16, 16), 14)
        screen.blit(self._magnet_glow, (mx - 16, my - 16))

        # U-shape magnet body — oriented so the opening faces outward from player
        # Rotate the U so its opening points away from centre
        face_angle = self.magnet_angle + math.pi  # opening faces away from player
        arm_len = 7
        gap     = 5
        for sign, pole_col in ((-1, (255, 80, 80)), (1, (80, 160, 255))):
            # Perpendicular offset for each arm
            perp = face_angle + sign * math.pi / 2
            ax = mx + math.cos(perp) * gap
            ay = my + math.sin(perp) * gap
            # Arm end (opening)
            ex = ax + math.cos(face_angle) * arm_len
            ey = ay + math.sin(face_angle) * arm_len
            pygame.draw.line(screen, (100, 200, 255), (int(ax), int(ay)), (int(ex), int(ey)), 3)
            # Pole tip colour
            pygame.draw.circle(screen, pole_col, (int(ex), int(ey)), 3)
        # Bridge (closed end)
        b_angle = face_angle + math.pi
        b1x = mx + math.cos(face_angle - math.pi/2) * gap + math.cos(b_angle) * 1
        b1y = my + math.sin(face_angle - math.pi/2) * gap + math.sin(b_angle) * 1
        b2x = mx + math.cos(face_angle + math.pi/2) * gap + math.cos(b_angle) * 1
        b2y = my + math.sin(face_angle + math.pi/2) * gap + math.sin(b_angle) * 1
        pygame.draw.line(screen, (100, 200, 255), (int(b1x), int(b1y)), (int(b2x), int(b2y)), 3)

    def get_fire_rate_pct(self) -> int:
        return int(self.BASE_FIRE_RATE / self.fire_rate * 100)


# ---------------------------------------------------------------------------
# Bullet
# ---------------------------------------------------------------------------

class Bullet:
    __slots__ = ('x', 'y', 'dir', 'speed', 'size', 'damage',
                 'bounces_left', 'max_bounces', 'pierce_left', 'max_pierce',
                 'lifetime', 'last_bounce_frame', 'hit_enemies')

    SPEED    = 10
    SIZE     = 5
    LIFETIME = 300
    INACCURACY = 0.20

    def __init__(self, x, y, direction, damage=10, bounces=0, pierce=0, inaccuracy=None, speed=None):
        self.x, self.y    = float(x), float(y)
        acc = self.INACCURACY if inaccuracy is None else inaccuracy
        rdx = direction[0] + random.uniform(-acc, acc)
        rdy = direction[1] + random.uniform(-acc, acc)
        ndx, ndy          = normalize(rdx, rdy)
        self.dir          = [ndx, ndy]
        self.speed        = self.SPEED if speed is None else speed
        self.size         = self.SIZE
        self.damage       = damage
        self.bounces_left = bounces
        self.max_bounces  = bounces
        self.pierce_left  = pierce
        self.max_pierce   = pierce
        self.lifetime     = self.LIFETIME
        self.last_bounce_frame = -1
        self.hit_enemies: set[int] = set()

    def update(self):
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed
        self.lifetime -= 1

    def expired(self):
        return self.lifetime <= 0

    def try_bounce(self, wall: Wall, frame: int) -> bool:
        if self.bounces_left <= 0 or frame == self.last_bounce_frame:
            return False
        self.last_bounce_frame = frame
        cx = wall.x + wall.width  / 2
        cy = wall.y + wall.height / 2
        dx, dy = self.x - cx, self.y - cy
        if abs(dx / max(wall.width, 1)) > abs(dy / max(wall.height, 1)):
            self.dir[0] *= -1
        else:
            self.dir[1] *= -1
        self.bounces_left -= 1
        return True

    def draw(self, screen: pygame.Surface, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if self.max_pierce > 0:
            color = C_BULLET_PIERCE
        elif self.max_bounces > 0:
            color = C_BULLET_BOUNCE
        else:
            color = C_BULLET
        pygame.draw.circle(screen, color, (sx, sy), self.size)


# ---------------------------------------------------------------------------
# Enemy Bullet
# ---------------------------------------------------------------------------

class EnemyBullet:
    __slots__ = ('x', 'y', 'dir', 'speed', 'size', 'is_cannon', 'bullet_type',
                 'lifetime', '_homing_target')

    def __init__(self, x, y, direction, *, is_cannon=False, bullet_type='normal', lifetime=220):
        self.x, self.y   = float(x), float(y)
        self.dir         = list(direction)
        self.is_cannon   = is_cannon
        self.bullet_type = bullet_type
        self.lifetime    = lifetime
        if   bullet_type == 'laser':    self.speed, self.size = 14, 5
        elif bullet_type == 'mortar':   self.speed, self.size = 3, 14
        elif bullet_type == 'homing':   self.speed, self.size = 5, 7
        elif bullet_type == 'snipe':    self.speed, self.size = 18, 4
        elif is_cannon:                 self.speed, self.size = 4, 12
        else:                           self.speed, self.size = 6, 6
        self._homing_target = None

    def update(self, px: float = 0, py: float = 0):
        self.lifetime -= 1
        if self.bullet_type == 'homing':
            # Gentle home toward player
            tdx, tdy = px - self.x, py - self.y
            dist = math.sqrt(tdx*tdx + tdy*tdy)
            if dist > 0:
                tdx /= dist; tdy /= dist
                self.dir[0] = lerp(self.dir[0], tdx, 0.04)
                self.dir[1] = lerp(self.dir[1], tdy, 0.04)
                self.dir[0], self.dir[1] = normalize(self.dir[0], self.dir[1])
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

    def draw(self, screen: pygame.Surface, cam_x, cam_y):
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        t = self.bullet_type
        if   t == 'laser':  pygame.draw.circle(screen, (255, 80,  80),  (sx, sy), self.size)
        elif t == 'mortar': pygame.draw.circle(screen, (200, 140,  40), (sx, sy), self.size)
        elif t == 'homing': pygame.draw.circle(screen, (220,  60, 255), (sx, sy), self.size)
        elif t == 'snipe':  pygame.draw.circle(screen, (255,  80,  80), (sx, sy), self.size)
        elif self.is_cannon:pygame.draw.circle(screen, C_ECANNON,       (sx, sy), self.size)
        else:               pygame.draw.circle(screen, C_EBULLET,       (sx, sy), self.size)


def lerp(a, b, t):
    return a + (b-a)*t


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------

class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size')

    def __init__(self, x, y, vx, vy, color, size=3, life=30):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.color       = color
        self.size        = size
        self.life        = life
        self.max_life    = life

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= 0.88
        self.vy *= 0.88
        self.life -= 1

    def draw(self, screen: pygame.Surface, cam_x, cam_y):
        frac = self.life / self.max_life
        bright = frac ** 0.45   # stays vivid longer, then fades sharply at end
        r = int(self.color[0] * bright)
        g = int(self.color[1] * bright)
        b = int(self.color[2] * bright)
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        r2 = max(1, int(self.size * frac))
        pygame.draw.circle(screen, (r, g, b), (sx, sy), r2)


def _spawn_particles(x, y, color, count=14, speed=4.0, size=4, life=35) -> list[Particle]:
    """Burst of particles at (x, y) in random directions."""
    out = []
    for _ in range(count):
        a  = random.uniform(0, math.pi * 2)
        sp = random.uniform(speed * 0.4, speed)
        out.append(Particle(x, y, math.cos(a)*sp, math.sin(a)*sp, color, size, life))
    return out


# ---------------------------------------------------------------------------
# Popup
# ---------------------------------------------------------------------------

class Popup:
    FONT: pygame.font.Font | None = None

    def __init__(self, text, x, y, color):
        self.text = text
        self.x, self.y = x, y
        self.color = color
        self.lifetime = 70
        self.alpha = 255

    @classmethod
    def get_font(cls):
        if cls.FONT is None:
            cls.FONT = pygame.font.SysFont('segoeui', 22, bold=True)
        return cls.FONT

    def update(self):
        self.lifetime -= 1
        self.y -= 1.2
        self.alpha = int(255 * max(0, self.lifetime / 70))

    def draw(self, screen, cam_x, cam_y):
        font = self.get_font()
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        s = font.render(self.text, True, self.color)
        s.set_alpha(self.alpha)
        sh = font.render(self.text, True, (0,0,0))
        sh.set_alpha(self.alpha//2)
        cx = sx - s.get_width()//2
        screen.blit(sh, (cx+2, sy+2))
        screen.blit(s,  (cx,   sy))


# ---------------------------------------------------------------------------
# Item (power-up crate with icon)
# ---------------------------------------------------------------------------

# Pre-bake icon draw functions
def _draw_icon_firerate(surf, cx, cy, c, size):
    """Lightning bolt icon."""
    pts = [(cx-2, cy-size*0.8), (cx+3, cy-size*0.1), (cx, cy-size*0.1),
           (cx+3, cy+size*0.8), (cx-3, cy+size*0.1), (cx, cy+size*0.1)]
    pygame.draw.polygon(surf, c, pts)

def _draw_icon_multishot(surf, cx, cy, c, size):
    """Three arrows fanning out."""
    for ang in (-0.5, 0, 0.5):
        ex = cx + math.cos(-math.pi/2 + ang) * size*0.9
        ey = cy + math.sin(-math.pi/2 + ang) * size*0.9
        pygame.draw.line(surf, c, (cx, cy+size*0.3), (int(ex), int(ey)), 2)
        pygame.draw.polygon(surf, c, [
            (int(ex), int(ey)),
            (int(ex + math.cos(-math.pi/2+ang+0.5)*4), int(ey + math.sin(-math.pi/2+ang+0.5)*4)),
            (int(ex + math.cos(-math.pi/2+ang-0.5)*4), int(ey + math.sin(-math.pi/2+ang-0.5)*4)),
        ])

def _draw_icon_damage(surf, cx, cy, c, size):
    """Skull-ish star."""
    for i in range(8):
        a = i * math.pi/4
        r = size*0.9 if i%2==0 else size*0.5
        pygame.draw.line(surf, c, (cx, cy),
                         (int(cx+math.cos(a)*r), int(cy+math.sin(a)*r)), 2)

def _draw_icon_bounce(surf, cx, cy, c, size):
    """Bouncing arrow path."""
    s = int(size*0.8)
    pts = [(cx-s, cy-s//2), (cx, cy+s//2), (cx+s, cy-s//2)]
    pygame.draw.lines(surf, c, False, pts, 2)
    pygame.draw.circle(surf, c, (cx, int(cy+s//2)), 3)

def _draw_icon_pierce(surf, cx, cy, c, size):
    """Arrow going through two shapes."""
    pygame.draw.circle(surf, (*c, 120), (int(cx-size//3), cy), size//3)
    pygame.draw.circle(surf, (*c, 120), (int(cx+size//3), cy), size//3)
    pygame.draw.line(surf, c, (cx-int(size*0.8), cy), (cx+int(size*0.8), cy), 3)
    pygame.draw.polygon(surf, c, [(int(cx+size*0.8), cy),
                                   (int(cx+size*0.5), cy-4), (int(cx+size*0.5), cy+4)])

def _draw_icon_speed(surf, cx, cy, c, size):
    """Three speed lines."""
    for i, length in enumerate([0.9, 0.7, 0.55]):
        y = cy + (i-1)*5
        pygame.draw.line(surf, c, (int(cx-size*length), y), (int(cx+size*length), y), 2)
    pygame.draw.polygon(surf, c, [(int(cx+size*0.9), cy),
                                   (int(cx+size*0.55), cy-6), (int(cx+size*0.55), cy+6)])

def _draw_icon_orbital(surf, cx, cy, c, size):
    """Orbit ring with dot."""
    pygame.draw.circle(surf, c, (cx, cy), size//2, 2)
    pygame.draw.circle(surf, c, (int(cx+size//2), cy), 4)
    pygame.draw.circle(surf, c, (int(cx-size//2), cy), 4)

def _draw_icon_dual_gun(surf, cx, cy, c, size):
    """Two parallel gun barrels."""
    for sign in (-1, 1):
        ox = sign * 5
        pygame.draw.rect(surf, c, (cx+ox-2, cy-int(size*0.8), 4, int(size*1.6)))
    pygame.draw.rect(surf, c, (cx-8, cy+int(size*0.3), 16, 5))

def _draw_icon_explode(surf, cx, cy, c, size):
    """Explosion starburst."""
    for i in range(8):
        a = i * math.pi / 4
        r = size * 0.95 if i % 2 == 0 else size * 0.55
        pygame.draw.line(surf, c, (cx, cy),
                         (int(cx + math.cos(a)*r), int(cy + math.sin(a)*r)), 2)
    pygame.draw.circle(surf, c, (cx, cy), int(size * 0.3))

def _draw_icon_magnet(surf, cx, cy, c, size):
    """U-shaped magnet with poles."""
    s = int(size * 0.8)
    # U arch — two vertical arms + curved top
    arm_w, arm_h = max(3, s//3), int(s * 0.9)
    gap = s // 2
    lx, rx = cx - gap, cx + gap
    # Left arm
    pygame.draw.rect(surf, c, (lx - arm_w//2, cy - arm_h//2, arm_w, arm_h), border_radius=2)
    # Right arm
    pygame.draw.rect(surf, c, (rx - arm_w//2, cy - arm_h//2, arm_w, arm_h), border_radius=2)
    # Bridge across top
    pygame.draw.rect(surf, c, (lx - arm_w//2, cy - arm_h//2, gap*2 + arm_w, arm_w))
    # Pole tips — opposite colours
    pygame.draw.rect(surf, (255, 80, 80),  (lx - arm_w//2, cy + arm_h//2 - arm_w, arm_w, arm_w), border_radius=1)
    pygame.draw.rect(surf, (80, 160, 255), (rx - arm_w//2, cy + arm_h//2 - arm_w, arm_w, arm_w), border_radius=1)

def _draw_icon_health(surf, cx, cy, c, size):
    """Red cross / plus sign."""
    s = int(size * 0.75)
    t = max(3, s // 3)
    pygame.draw.rect(surf, c, (cx - t//2, cy - s//2, t, s), border_radius=1)
    pygame.draw.rect(surf, c, (cx - s//2, cy - t//2, s, t), border_radius=1)

def _draw_icon_steady(surf, cx, cy, c, size):
    """Crosshair / reticle icon."""
    s = int(size * 0.8)
    pygame.draw.circle(surf, c, (cx, cy), s, 2)
    for a in (0, math.pi/2, math.pi, 3*math.pi/2):
        pygame.draw.line(surf, c,
                         (int(cx + math.cos(a) * (s - 4)), int(cy + math.sin(a) * (s - 4))),
                         (int(cx + math.cos(a) * (s + 4)), int(cy + math.sin(a) * (s + 4))), 2)
    pygame.draw.circle(surf, c, (cx, cy), 3)

_ICON_DRAW = {
    'firerate':  _draw_icon_firerate,
    'multishot': _draw_icon_multishot,
    'damage':    _draw_icon_damage,
    'bounce':    _draw_icon_bounce,
    'pierce':    _draw_icon_pierce,
    'speed':     _draw_icon_speed,
    'orbital':   _draw_icon_orbital,
    'dual_gun':  _draw_icon_dual_gun,
    'explode':   _draw_icon_explode,
    'magnet':    _draw_icon_magnet,
    'health':    _draw_icon_health,
    'steady':    _draw_icon_steady,
}

_LABEL_FONT: pygame.font.Font | None = None
_FONT_CACHE: dict[tuple, pygame.font.Font] = {}

def _get_font(size: int, bold: bool = True) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont('segoeui', size, bold=bold)
    return _FONT_CACHE[key]

def _label_font():
    global _LABEL_FONT
    if _LABEL_FONT is None:
        _LABEL_FONT = pygame.font.SysFont('segoeui', 13, bold=True)
    return _LABEL_FONT


class Item:
    CRATE_SIZE = 22

    def __init__(self, x, y, item_type: str):
        self.x, self.y = float(x), float(y)
        self.type = item_type
        cfg = ITEM_CONFIG.get(item_type, {'color': C_WHITE, 'name': item_type, 'desc': item_type, 'icon': item_type})
        self.color = cfg['color']
        self.name  = cfg['name']
        self.desc  = cfg['desc']
        self.size  = self.CRATE_SIZE
        self.bob   = random.uniform(0, math.pi*2)   # phase for bob animation
        self._icon_surf: pygame.Surface | None = None
        self._border_surf: pygame.Surface | None = None
        self._glow_surf: pygame.Surface | None = None
        self._label_surf: pygame.Surface | None = None
        self._label_bg_surf: pygame.Surface | None = None

    def _get_icon_surf(self) -> pygame.Surface:
        if self._icon_surf is None:
            s = self.size
            surf = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
            fn = _ICON_DRAW.get(self.type)
            if fn:
                try:
                    fn(surf, s, s, self.color, int(s*0.6))
                except Exception:
                    pass
            self._icon_surf = surf
        return self._icon_surf

    def _build_crate_surfs(self):
        s = self.size
        c = self.color
        # Border glow (SRCALPHA, built once)
        bs = pygame.Surface((s*2+4, s*2+4), pygame.SRCALPHA)
        pygame.draw.rect(bs, (*c, 200), bs.get_rect(), 2, border_radius=8)
        self._border_surf = bs
        # Glow (SRCALPHA, fixed alpha, built once)
        gsize = s + 10
        gs = pygame.Surface((gsize*2+4, gsize*2+4), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*c, 28), (2, 2, gsize*2, gsize*2), border_radius=8)
        self._glow_surf = gs
        self._glow_off  = gsize
        # Label
        font = _label_font()
        lbl = font.render(self.name, True, c)
        self._label_surf = lbl
        bg_w, bg_h = lbl.get_width()+6, lbl.get_height()+2
        lbg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        pygame.draw.rect(lbg, (0, 0, 0, 160), lbg.get_rect(), border_radius=3)
        self._label_bg_surf = lbg

    def draw(self, screen: pygame.Surface, cam_x, cam_y):
        self.bob += 0.04
        bob_y = math.sin(self.bob) * 4
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y + bob_y)
        s  = self.size
        c  = self.color

        # Build cached surfaces on first draw
        if self._border_surf is None:
            self._build_crate_surfs()

        # Glow (fixed alpha cached surf)
        go = self._glow_off
        screen.blit(self._glow_surf, (sx-go-2, sy-go-2))

        # Crate body — rounded square
        crate_rect = pygame.Rect(sx-s, sy-s, s*2, s*2)
        pygame.draw.rect(screen, (20, 22, 38), crate_rect, border_radius=7)
        # Colored border glow (cached)
        screen.blit(self._border_surf, (sx-s-2, sy-s-2))
        # Inner accent lines
        pygame.draw.line(screen, (*c, 80), (sx-s+4, sy-s+2), (sx+s-4, sy-s+2), 1)
        pygame.draw.line(screen, (*c, 80), (sx-s+2, sy-s+4), (sx-s+2, sy+s-4), 1)

        # Icon
        icon = self._get_icon_surf()
        screen.blit(icon, (sx - s, sy - s))

        # Label (cached)
        lbl = self._label_surf
        lbg = self._label_bg_surf
        screen.blit(lbg, (sx - lbg.get_width()//2, sy+s+4))
        screen.blit(lbl, (sx - lbl.get_width()//2,  sy+s+5))

    def apply_to(self, player: Player) -> None:
        if   self.type == 'firerate':  player.fire_rate       = max(5, player.fire_rate - 2)
        elif self.type == 'multishot': player.multi_shot      += 1
        elif self.type == 'damage':    player.damage          += 2
        elif self.type == 'bounce':    player.bullet_bounce    = min(3, player.bullet_bounce+1)
        elif self.type == 'pierce':    player.bullet_pierce    = min(5, player.bullet_pierce+1)
        elif self.type == 'speed':     player.speed            = min(12, player.speed+0.5)
        elif self.type == 'orbital':   player.has_orbital = True; player.orbital_count += 1          # +1 saw
        elif self.type == 'dual_gun':  player.has_dual_gun = True; player.dual_gun_count += 1
        elif self.type == 'explode':   player.bullet_explode += 1                                     # no cap
        elif self.type == 'magnet':    player.magnet_count += 1                                       # +range per stack
        elif self.type == 'steady':    player.steady_aim += 1                                         # no cap
        elif self.type == 'health':    player.health = min(player.MAX_HEALTH, player.health + 1)


# ---------------------------------------------------------------------------
# Enemy — distinct graphics per type + unique attack sets
# ---------------------------------------------------------------------------

class Enemy:
    UNLOAD_DIST_SQ = 3000 * 3000
    UNLOAD_DELAY   = 600

    def __init__(self, x, y, health=50, *, is_boss=False, is_final=False,
                 boss_id=1, enemy_type='normal'):
        self.x, self.y   = float(x), float(y)
        self.is_boss      = is_boss
        self.is_final     = is_final
        self.boss_id      = max(1, min(boss_id, 8))
        self.enemy_type   = enemy_type

        if is_final:
            self.size  = 48
            self.speed = random.uniform(0.8, 1.4)
        elif is_boss:
            self.size  = 34
            self.speed = random.uniform(0.6, 1.2)
        elif enemy_type == 'fast':
            self.size  = 11
            self.speed = random.uniform(3.5, 5.0)
        elif enemy_type == 'tank':
            self.size  = 22
            self.speed = random.uniform(0.8, 1.2)
        elif enemy_type == 'shooter':
            self.size  = 14
            self.speed = random.uniform(2.0, 2.5)
        else:
            self.size  = 15
            self.speed = random.uniform(1.5, 3.0)

        self.health     = health
        self.max_health = health
        # Shoot rates per type
        if enemy_type == 'shooter':  self.shoot_rate = 55
        elif enemy_type == 'tank':   self.shoot_rate = 420
        elif is_final:               self.shoot_rate = 60
        elif is_boss:                self.shoot_rate = 90
        else:                        self.shoot_rate = 9999999

        self.shoot_cooldown    = random.randint(0, self.shoot_rate)
        self.attack_pattern    = 0
        self.pattern_timer     = 0
        self.phase_len         = 250 if is_final else 300   # overridden by spawn for scaling
        self.minion_spawn_timer= 0
        self.frames_far        = 0
        self.cached_los        = True
        self.anim_angle        = random.uniform(0, math.pi*2)
        self.anim_timer        = 0

        # Fast dash
        self.is_dashing    = False
        self.dash_timer    = 0
        self.dash_cooldown = 0
        self.dash_dir      = [0.0, 0.0]
        self.dash_trail: list[tuple[float, float]] = []

        # Fast: track angle toward player (updated in update())
        self.face_angle = random.uniform(0, math.pi * 2)

    def update(self, px, py, chunk_manager: ChunkManager, has_los: bool):
        self.anim_timer += 1
        self.anim_angle += 0.05

        if not has_los and not self.is_boss:
            return

        dx, dy   = px - self.x, py - self.y
        dist_sq  = dx*dx + dy*dy
        dist     = math.sqrt(dist_sq) if dist_sq > 0 else 0.001

        # Always track the angle toward the player (used by fast draw)
        self.face_angle = math.atan2(dy, dx)

        # Fast: point at player, telegraph then dash
        if self.enemy_type == 'fast':
            if self.is_dashing:
                self.dash_trail.append((self.x, self.y))
                if len(self.dash_trail) > 12: self.dash_trail.pop(0)
                self.dash_timer -= 1
                if self.dash_timer <= 0:
                    self.is_dashing = False
                    self.dash_trail.clear()
                else:
                    self._move(self.dash_dir[0]*self.speed*3, self.dash_dir[1]*self.speed*3, chunk_manager)
                    return
            else:
                self.dash_cooldown -= 1
                if self.dash_cooldown <= 0 and dist_sq < 450**2:
                    self.dash_dir = [dx/dist, dy/dist]
                    self.is_dashing = True
                    self.dash_timer = 15
                    self.dash_cooldown = 160
                    return
                # Creep slowly toward player while not dashing
                self._move(dx/dist * self.speed * 0.3, dy/dist * self.speed * 0.3, chunk_manager)
        else:
            if dist_sq > 0:
                spd = self.speed
                # Enrage: move faster below 25 % HP
                if self.is_boss and self.health < self.max_health * 0.25:
                    spd *= 1.7
                self._move(dx/dist * spd, dy/dist * spd, chunk_manager)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.is_boss:
            self.pattern_timer += 1
            # Enrage: cycle attack phases faster below 25 % HP
            effective_phase = max(80, self.phase_len // 2) if self.health < self.max_health * 0.25 else self.phase_len
            n_patterns = 5 if self.is_final else 4
            if self.pattern_timer > effective_phase:
                self.attack_pattern = (self.attack_pattern + 1) % n_patterns
                self.pattern_timer  = 0

    def _move(self, vx, vy, cm: ChunkManager):
        nx, ny = self.x+vx, self.y+vy
        if not cm.tilemap.check_collision(nx, self.y, self.size): self.x = nx
        if not cm.tilemap.check_collision(self.x, ny, self.size): self.y = ny

    def can_shoot(self) -> bool:
        return (self.is_boss or self.enemy_type in ('shooter', 'tank')) \
               and self.shoot_cooldown == 0

    def shoot(self, px, py) -> list[EnemyBullet]:
        self.shoot_cooldown = self.shoot_rate
        dx, dy = px - self.x, py - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0: return []
        base = [dx/dist, dy/dist]
        base_angle = angle_of(dx, dy)
        pt = self.pattern_timer
        bullets = []

        def B(direction, btype='normal', is_cannon=False, lifetime=220):
            return EnemyBullet(self.x, self.y, list(direction),
                               is_cannon=is_cannon, bullet_type=btype, lifetime=lifetime)

        # ---- Non-boss typed attacks ----
        if not self.is_boss:
            if self.enemy_type == 'shooter':
                # Triple burst with slight spread
                for d in spread_directions(*base, 3, 0.25):
                    bullets.append(B(d))
            elif self.enemy_type == 'tank':
                # Cannon ball + two flanking mortars
                bullets.append(B(base, is_cannon=True))
                for sign in (-1, 1):
                    a = base_angle + sign*0.5
                    bullets.append(B((math.cos(a), math.sin(a)), btype='mortar'))
            return bullets

        # ---- Per-boss attack sets ----
        if self.is_final:
            FINAL = [
                # Pattern 0: massive spread + homing ring
                lambda: [B(d) for d in spread_directions(*base, 14, 1.8)]
                       + [B(d, 'homing') for d in ring_directions(6, pt*0.05)],
                # Pattern 1: rotating double ring
                lambda: [B(d) for d in ring_directions(8, pt*0.1)]
                       + [B(d) for d in ring_directions(8, pt*0.1+math.pi/8)],
                # Pattern 2: snipe burst + ring
                lambda: [B(d,'snipe') for d in ring_directions(4)]
                       + [B(d) for d in spread_directions(*base, 18, 1.9)],
                # Pattern 3: homing swarm + mortar ring
                lambda: [B(d,'homing') for d in ring_directions(10, pt*0.08)]
                       + [B(d,'mortar') for d in ring_directions(5)],
                # Pattern 4: laser cross + spread
                lambda: [B(d,'laser') for d in ring_directions(4)]
                       + [B(d) for d in spread_directions(*base, 20, 2.0)],
            ]
            idx = self.attack_pattern % len(FINAL)
            return FINAL[idx]()

        # Mini bosses with per-boss-id flavour
        MINI = {
            1: [  # VOIDCALLER — homing + ring
                lambda: [B(d,'homing') for d in ring_directions(6, pt*0.06)],
                lambda: [B(d) for d in spread_directions(*base, 7, 1.4)],
                lambda: [B(d,'homing') for d in ring_directions(4)] + [B(d) for d in ring_directions(4, math.pi/4)],
                lambda: [B(d) for d in ring_directions(10, pt*0.08)],
            ],
            2: [  # INFERNAX — mortar + laser
                lambda: [B(d,'mortar') for d in ring_directions(6)],
                lambda: [B(d,'laser')  for d in spread_directions(*base, 5, 1.0)],
                lambda: [B(d,'mortar') for d in ring_directions(4, pt*0.05)] + [B(base,'laser')],
                lambda: [B(d,'laser')  for d in ring_directions(8, pt*0.1)],
            ],
            3: [  # GLACIUS — sniper beams
                lambda: [B(d,'snipe') for d in spread_directions(*base, 3, 0.6)],
                lambda: [B(d,'snipe') for d in ring_directions(4, pt*0.07)],
                lambda: [B(d) for d in ring_directions(12)] + [B(d,'snipe') for d in ring_directions(4, math.pi/4)],
                lambda: [B(d,'snipe') for d in ring_directions(6, pt*0.04)],
            ],
            4: [  # SOLARCH — cannon + spread
                lambda: [B(d, is_cannon=True) for d in ring_directions(4)],
                lambda: [B(d) for d in spread_directions(*base, 10, 1.6)],
                lambda: [B(d, is_cannon=True) for d in spread_directions(*base, 4, 1.0)],
                lambda: [B(d) for d in ring_directions(14, pt*0.09)],
            ],
            5: [  # NECRAXIS — homing swarm
                lambda: [B(d,'homing') for d in ring_directions(8, pt*0.07)],
                lambda: [B(d,'homing') for d in spread_directions(*base, 12, 1.7)],
                lambda: [B(d,'mortar') for d in ring_directions(6)] + [B(d,'homing') for d in ring_directions(4, math.pi/6)],
                lambda: [B(d,'homing') for d in ring_directions(10, pt*0.05)],
            ],
            6: [  # ABYSSTIDE — deep-water slow death waves
                lambda: [B(d) for d in ring_directions(16, pt*0.04)],
                lambda: [B(d,'mortar') for d in ring_directions(8, pt*0.06)] + [B(d,'homing') for d in ring_directions(4)],
                lambda: [B(d,'laser') for d in spread_directions(*base, 8, 1.8)],
                lambda: [B(d) for d in ring_directions(12)] + [B(d,'mortar') for d in ring_directions(6, math.pi/6)],
            ],
            7: [  # WRATHBORN — rage-fueled spread
                lambda: [B(d) for d in spread_directions(*base, 16, 2.0)],
                lambda: [B(d,'laser') for d in ring_directions(6, pt*0.08)] + [B(d) for d in ring_directions(6, math.pi/6)],
                lambda: [B(d,'snipe') for d in spread_directions(*base, 4, 0.5)] + [B(d,'homing') for d in ring_directions(8)],
                lambda: [B(d) for d in ring_directions(20, pt*0.06)],
            ],
            8: [  # VIRULEX — infectious spread clusters
                lambda: [B(d,'homing') for d in ring_directions(12, pt*0.05)],
                lambda: [B(d,'mortar') for d in spread_directions(*base, 6, 1.2)] + [B(d,'snipe') for d in ring_directions(4)],
                lambda: [B(d) for d in ring_directions(18, pt*0.07)],
                lambda: [B(d,'laser') for d in ring_directions(8, pt*0.1)] + [B(d,'homing') for d in spread_directions(*base, 6, 1.0)],
            ],
        }
        fns = MINI.get(self.boss_id, MINI[1])
        idx = self.attack_pattern % len(fns)
        return fns[idx]()

    # ------------------------------------------------------------------
    # Drawing — distinct visuals per enemy type
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        t = self.enemy_type

        if self.is_final:
            self._draw_final_boss(screen, sx, sy)
        elif self.is_boss:
            self._draw_mini_boss(screen, sx, sy)
        elif t == 'normal':
            self._draw_normal(screen, sx, sy)
        elif t == 'fast':
            self._draw_fast(screen, sx, sy)
        elif t == 'tank':
            self._draw_tank(screen, sx, sy)
        elif t == 'shooter':
            self._draw_shooter(screen, sx, sy)

        self._draw_healthbar(screen, sx, sy)

    def _draw_normal(self, screen, sx, sy):
        style = ENEMY_STYLES['normal']
        s = self.size
        # Outer hexagon
        pts = [(sx + math.cos(self.anim_angle + i*math.pi/3)*s,
                sy + math.sin(self.anim_angle + i*math.pi/3)*s) for i in range(6)]
        pygame.draw.polygon(screen, style['dark'], pts)
        # Inner filled hex (slightly smaller)
        inner = [(sx + math.cos(self.anim_angle + i*math.pi/3)*(s-4),
                  sy + math.sin(self.anim_angle + i*math.pi/3)*(s-4)) for i in range(6)]
        pygame.draw.polygon(screen, style['body'], inner)
        pygame.draw.polygon(screen, style['rim'],  pts, 2)
        # Inner triangle counter-rotating
        for i in range(3):
            a = -self.anim_angle * 1.5 + i * 2*math.pi/3
            pygame.draw.line(screen, style['dark'],
                             (sx, sy),
                             (int(sx + math.cos(a)*(s-6)), int(sy + math.sin(a)*(s-6))), 2)
        # Pulsing eye
        pulse = 4 + int(2 * math.sin(self.anim_timer * 0.15))
        pygame.draw.circle(screen, (255, 60, 60), (sx, sy), pulse)
        pygame.draw.circle(screen, (255, 200, 200), (sx, sy), max(1, pulse-2))

    def _draw_fast(self, screen, sx, sy):
        style = ENEMY_STYLES['fast']
        s = self.size
        # Always face the player; during dash use locked dash direction
        a = math.atan2(self.dash_dir[1], self.dash_dir[0]) if self.is_dashing else self.face_angle
        # Pre-dash telegraph: tighten/brighten slightly when dash is ready
        ready = (not self.is_dashing and self.dash_cooldown <= 0)
        # Motion-blur ghost trails (only while dashing)
        trail_pts = self.dash_trail if self.is_dashing else []
        for i, (tx, ty) in enumerate(trail_pts):
            frac = (i + 1) / max(len(trail_pts), 1)
            c = style['body']
            tc = (int(c[0]*frac*0.4), int(c[1]*frac*0.4), int(c[2]*frac*0.4))
            pygame.draw.circle(screen, tc, (int(tx), int(ty)), max(1, int(s*frac+1)))
        # Arrowhead body — sharper, two-tone
        pts_outer = [
            (sx + math.cos(a)*s*1.5,           sy + math.sin(a)*s*1.5),
            (sx + math.cos(a+2.3)*s,            sy + math.sin(a+2.3)*s),
            (sx + math.cos(a+math.pi)*s*0.45,   sy + math.sin(a+math.pi)*s*0.45),
            (sx + math.cos(a-2.3)*s,            sy + math.sin(a-2.3)*s),
        ]
        pts_inner = [
            (sx + math.cos(a)*s*0.9,            sy + math.sin(a)*s*0.9),
            (sx + math.cos(a+2.3)*s*0.55,       sy + math.sin(a+2.3)*s*0.55),
            (sx + math.cos(a+math.pi)*s*0.3,    sy + math.sin(a+math.pi)*s*0.3),
            (sx + math.cos(a-2.3)*s*0.55,       sy + math.sin(a-2.3)*s*0.55),
        ]
        pygame.draw.polygon(screen, style['dark'], pts_outer)
        pygame.draw.polygon(screen, style['body'], pts_inner)
        pygame.draw.polygon(screen, style['rim'],  pts_outer, 2)
        # Speed lines behind (only while dashing)
        if self.is_dashing:
            for i in range(4):
                la = a + math.pi + (i - 1.5) * 0.22
                pygame.draw.line(screen, style['rim'],
                                 (int(sx + math.cos(la)*4),     int(sy + math.sin(la)*4)),
                                 (int(sx + math.cos(la)*s*1.4), int(sy + math.sin(la)*s*1.4)), 1)
        # Telegraph ring when dash is charged
        if ready:
            pulse = 0.6 + 0.4 * math.sin(self.anim_timer * 0.3)
            rc = (int(255*pulse), int(240*pulse), int(80*pulse))
            pygame.draw.circle(screen, rc, (sx, sy), s + 5, 2)

    def _draw_tank(self, screen, sx, sy):
        style = ENEMY_STYLES['tank']
        s = self.size

        # Spinning flail — drawn BEHIND body
        chain_len = int(s * 2.6)
        ball_r    = int(s * 0.85)
        fa  = self.anim_angle * 2.2  # faster spin than body
        fx  = sx + int(math.cos(fa) * chain_len)
        fy  = sy + int(math.sin(fa) * chain_len)
        # Chain links
        link_count = 5
        for li in range(1, link_count + 1):
            t = li / (link_count + 1)
            lx = int(sx + math.cos(fa) * chain_len * t)
            ly = int(sy + math.sin(fa) * chain_len * t)
            pygame.draw.circle(screen, style['dark'], (lx, ly), 3)
            pygame.draw.circle(screen, style['rim'],  (lx, ly), 3, 1)
        # Flail ball — spiked
        pygame.draw.circle(screen, style['dark'], (fx, fy), ball_r + 3)
        pygame.draw.circle(screen, style['body'], (fx, fy), ball_r)
        pygame.draw.circle(screen, style['rim'],  (fx, fy), ball_r, 2)
        spike_n = 6
        for si in range(spike_n):
            sa = fa + si * math.pi / 3
            pygame.draw.line(screen, style['rim'],
                             (int(fx + math.cos(sa) * (ball_r - 2)), int(fy + math.sin(sa) * (ball_r - 2))),
                             (int(fx + math.cos(sa) * (ball_r + 6)), int(fy + math.sin(sa) * (ball_r + 6))), 2)

        # Armour body (square)
        r_outer = pygame.Rect(sx-s, sy-s, s*2, s*2)
        pygame.draw.rect(screen, style['dark'], r_outer, border_radius=5)
        r_inner = r_outer.inflate(-5, -5)
        pygame.draw.rect(screen, style['body'], r_inner, border_radius=4)
        pygame.draw.line(screen, style['dark'], (sx-s+5, sy), (sx+s-5, sy), 2)
        pygame.draw.line(screen, style['dark'], (sx, sy-s+5), (sx, sy+s-5), 2)
        pygame.draw.rect(screen, style['rim'], r_outer, 2, border_radius=5)
        for cx2, cy2 in [(-s+5,-s+5),(s-5,-s+5),(-s+5,s-5),(s-5,s-5)]:
            pygame.draw.circle(screen, style['rim'],  (sx+cx2, sy+cy2), 4)
            pygame.draw.circle(screen, style['dark'], (sx+cx2, sy+cy2), 2)

    def _draw_shooter(self, screen, sx, sy):
        style = ENEMY_STYLES['shooter']
        s = self.size
        # Rotating ring + core
        for i in range(3):
            a = self.anim_angle + i * 2*math.pi/3
            rx = sx + math.cos(a)*s
            ry = sy + math.sin(a)*s
            pygame.draw.circle(screen, style['body'], (int(rx), int(ry)), 5)
        pygame.draw.circle(screen, style['dark'], (sx, sy), s, 2)
        pygame.draw.circle(screen, style['body'], (sx, sy), s-4)
        pygame.draw.circle(screen, style['rim'],  (sx, sy), s-4, 2)
        # Turrets
        for i in range(3):
            a = self.anim_angle + i * 2*math.pi/3
            tx = sx + math.cos(a)*(s-2)
            ty = sy + math.sin(a)*(s-2)
            tx2 = sx + math.cos(a)*(s+8)
            ty2 = sy + math.sin(a)*(s+8)
            pygame.draw.line(screen, style['rim'], (int(tx),int(ty)), (int(tx2),int(ty2)), 3)

    def _draw_mini_boss(self, screen, sx, sy):
        bid = self.boss_id
        style = BOSS_STYLES.get(bid, BOSS_STYLES[1])
        s = self.size

        # Glow layers (2 only, cached)
        if not hasattr(self, '_glow_surfs'):
            self._glow_surfs = []
            for i in range(2):
                gr = s + (2-i)*10
                gs2 = pygame.Surface((gr*2+2, gr*2+2), pygame.SRCALPHA)
                pygame.draw.circle(gs2, (*style['body'], 28), (gr+1, gr+1), gr)
                self._glow_surfs.append((gs2, gr))
        for gs2, gr in self._glow_surfs:
            screen.blit(gs2, (sx-gr-1, sy-gr-1))

        # Outer rotating petals
        petal_n = 5 + bid  # 6-13 petals for bosses 1-8
        for i in range(petal_n):
            a = self.anim_angle*1.2 + i*2*math.pi/petal_n
            px2 = sx + math.cos(a)*s
            py2 = sy + math.sin(a)*s
            pygame.draw.circle(screen, style['rim'], (int(px2), int(py2)), 6)

        # Core body — octagon
        pts = [(sx+math.cos(self.anim_angle+i*math.pi/4)*s,
                sy+math.sin(self.anim_angle+i*math.pi/4)*s) for i in range(8)]
        pygame.draw.polygon(screen, style['dark'], pts)
        pygame.draw.polygon(screen, style['body'], [(sx+math.cos(self.anim_angle+i*math.pi/4)*(s-4),
                                                     sy+math.sin(self.anim_angle+i*math.pi/4)*(s-4)) for i in range(8)])
        pygame.draw.polygon(screen, style['rim'], pts, 3)
        pygame.draw.circle(screen, style['rim'], (sx, sy), s//3)
        # Eye
        pygame.draw.circle(screen, style['body'], (sx, sy), s//4)

    def _draw_final_boss(self, screen, sx, sy):
        style = BOSS_FINAL_STYLE
        s = self.size
        t = self.anim_timer

        # Multi-layer glow (3 cached layers, pulse via modulation)
        if not hasattr(self, '_glow_surfs'):
            self._glow_surfs = []
            for i in range(3):
                gr = s + (3-i)*14
                gs2 = pygame.Surface((gr*2+2, gr*2+2), pygame.SRCALPHA)
                pygame.draw.circle(gs2, (*style['body'], 22), (gr+1, gr+1), gr)
                self._glow_surfs.append((gs2, gr))
        for gs2, gr in self._glow_surfs:
            screen.blit(gs2, (sx-gr-1, sy-gr-1))

        # Outer ring of spikes
        for i in range(12):
            a = self.anim_angle*0.7 + i*2*math.pi/12
            tip = s + 18 + math.sin(t*0.1 + i)*4
            pygame.draw.line(screen, style['rim'], (sx, sy), (int(sx+math.cos(a)*tip), int(sy+math.sin(a)*tip)), 3)

        # Second layer counter-rotating
        for i in range(8):
            a = -self.anim_angle*1.2 + i*2*math.pi/8
            px2 = sx + math.cos(a)*(s-4)
            py2 = sy + math.sin(a)*(s-4)
            pygame.draw.circle(screen, style['rim'], (int(px2), int(py2)), 8)

        # Body — 12-sided
        pts = [(sx+math.cos(self.anim_angle*0.4+i*math.pi/6)*s,
                sy+math.sin(self.anim_angle*0.4+i*math.pi/6)*s) for i in range(12)]
        pygame.draw.polygon(screen, style['dark'], pts)
        pygame.draw.polygon(screen, style['body'],
                            [(sx+math.cos(self.anim_angle*0.4+i*math.pi/6)*(s-6),
                              sy+math.sin(self.anim_angle*0.4+i*math.pi/6)*(s-6)) for i in range(12)])
        pygame.draw.polygon(screen, style['rim'], pts, 4)
        # Inner eye
        pygame.draw.circle(screen, style['body'], (sx, sy), s//2)
        pygame.draw.circle(screen, style['rim'],  (sx, sy), s//2, 3)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), s//5)
        pulse_r = int(s//8 + 3*math.sin(t*0.15))
        pygame.draw.circle(screen, style['dark'], (sx, sy), pulse_r)

    def _draw_healthbar(self, screen, sx, sy):
        if self.is_boss:
            return   # boss bar is in HUD
        bw = max(36, self.size*2+10)
        bh = 8
        bx = sx - bw//2
        by = sy - self.size - 14
        pygame.draw.rect(screen, (30, 30, 40), (bx, by, bw, bh), border_radius=3)
        pct = self.health / max(self.max_health, 1)
        hw  = int(bw * pct)
        hc  = C_HEALTH_GREEN if pct > 0.5 else (C_HEALTH_YEL if pct > 0.25 else C_HEALTH_RED)
        if hw > 0:
            pygame.draw.rect(screen, hc, (bx, by, hw, bh), border_radius=3)
        pygame.draw.rect(screen, (150, 150, 180), (bx, by, bw, bh), 1, border_radius=3)


# ---------------------------------------------------------------------------
# ShooterGame
# ---------------------------------------------------------------------------

class ShooterGame:
    def __init__(self, screen: pygame.Surface,
                 seed: str | None = None,
                 save_data: dict | None = None):
        self.display_screen = screen
        disp_w, disp_h = screen.get_size()
        # Use .convert() so pixel format matches the display — faster blitting every frame
        self.screen = pygame.Surface((VIEWPORT_W, VIEWPORT_H)).convert()
        scale = min(disp_w/VIEWPORT_W, disp_h/VIEWPORT_H)
        self.scale    = scale
        self.offset_x = int((disp_w - VIEWPORT_W*scale)//2)
        self.offset_y = int((disp_h - VIEWPORT_H*scale)//2)
        # Pre-allocate the scaled output surface so _flip() never allocates one per frame
        _sw = int(VIEWPORT_W * scale)
        _sh = int(VIEWPORT_H * scale)
        self._scaled_surf = pygame.Surface((_sw, _sh)).convert()
        self.clock    = pygame.time.Clock()
        self.font     = pygame.font.SysFont('segoeui', 26, bold=True)

        self.seed = seed or _save_mod.new_seed()

        print(f"Generating map (seed={self.seed})…")
        random.seed(_save_mod.seed_to_int(self.seed))
        self.chunk_manager = ChunkManager(WORLD_SIZE)
        self.chunk_manager.generate_map()
        random.seed()   # re-randomise for gameplay
        print(f"Map ready. Rooms: {len(self.chunk_manager.rooms)}")

        self.wall_renderer = WallRenderer(self.chunk_manager.tilemap)

        cx = cy = WORLD_SIZE // 2
        self.player = Player(cx, cy)
        self.chunk_manager.load_chunks_around(cx, cy)

        self.cam_x = 0.0
        self.cam_y = 0.0

        self.bullets:       list[Bullet]      = []
        self.enemy_bullets: list[EnemyBullet] = []
        self.enemies:       list[Enemy]       = []
        self.items:         list[Item]        = []
        self.popups:        list[Popup]       = []
        self.particles:     list[Particle]   = []
        self.kills          = 0
        self.shoot_cd       = 0
        self.spawn_timer    = 0
        self.frame          = 0
        self.boss_active    = False
        self.current_boss:  Enemy | None = None

        self._init_spawns_left = 8
        self._init_spawn_timer = 0

        # Precompute seamless floor pattern
        self._floor_surf: pygame.Surface | None = None

        # Precompute vignette overlay (dark edges, transparent centre)
        self._vignette = self._build_vignette()

        # Restore a saved run if provided
        if save_data:
            self._restore_state(save_data)

    # ------------------------------------------------------------------
    # Save / restore
    # ------------------------------------------------------------------

    def _save_state(self) -> dict:
        p = self.player
        return {
            'seed':     self.seed,
            'kills':    self.kills,
            'player_x': p.x,
            'player_y': p.y,
            'player': {
                'health':        p.health,
                'fire_rate':     p.fire_rate,
                'multi_shot':    p.multi_shot,
                'damage':        p.damage,
                'bullet_bounce': p.bullet_bounce,
                'bullet_pierce': p.bullet_pierce,
                'speed':         p.speed,
                'has_orbital':   p.has_orbital,
                'orbital_count': p.orbital_count,
                'has_dual_gun':  p.has_dual_gun,
                'dual_gun_count':p.dual_gun_count,
                'bullet_explode':p.bullet_explode,
                'magnet_count':  p.magnet_count,
                'steady_aim':    p.steady_aim,
            },
        }

    def _restore_state(self, data: dict) -> None:
        p  = self.player
        pd = data.get('player', {})
        p.health         = int(pd.get('health',        p.MAX_HEALTH))
        p.fire_rate      = int(pd.get('fire_rate',     Player.BASE_FIRE_RATE))
        p.multi_shot     = int(pd.get('multi_shot',    1))
        p.damage         = int(pd.get('damage',        Player.BASE_DAMAGE))
        p.bullet_bounce  = int(pd.get('bullet_bounce', 0))
        p.bullet_pierce  = int(pd.get('bullet_pierce', 0))
        p.speed          = float(pd.get('speed',       Player.BASE_SPEED))
        p.has_orbital    = bool(pd.get('has_orbital',  False))
        p.orbital_count  = int(pd.get('orbital_count', 0))
        p.has_dual_gun   = bool(pd.get('has_dual_gun', False))
        p.dual_gun_count = int(pd.get('dual_gun_count',0))
        p.bullet_explode = int(pd.get('bullet_explode', 0))
        p.magnet_count   = int(pd.get('magnet_count',  0))
        p.steady_aim     = int(pd.get('steady_aim',    0))
        self.kills       = int(data.get('kills', 0))
        p.x = float(data.get('player_x', WORLD_SIZE // 2))
        p.y = float(data.get('player_y', WORLD_SIZE // 2))

    # ------------------------------------------------------------------
    # Display helper
    # ------------------------------------------------------------------

    def _flip(self):
        """Composite viewport surface to display and flip."""
        # 3-arg scale writes into the pre-allocated surface — no allocation per frame
        pygame.transform.scale(self.screen, self._scaled_surf.get_size(), self._scaled_surf)
        self.display_screen.fill((0, 0, 0))
        self.display_screen.blit(self._scaled_surf, (self.offset_x, self.offset_y))
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Pause menu
    # ------------------------------------------------------------------

    def _pause_menu(self) -> str:
        """Overlay pause menu. Returns 'resume', 'save_quit', or 'quit'."""
        snapshot = self.display_screen.copy()
        dark = pygame.Surface(self.display_screen.get_size(), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 160))

        dw, dh = self.display_screen.get_size()
        pw, ph = 360, 310
        px = (dw - pw) // 2
        py = (dh - ph) // 2

        f_title = _get_font(28)
        f_btn   = _get_font(20)
        f_seed  = _get_font(14)

        btns = [
            ('RESUME',      'resume'),
            ('SAVE & QUIT', 'save_quit'),
            ('QUIT',        'quit'),
        ]
        btn_w, btn_h = 250, 52
        rects = [
            pygame.Rect(px + (pw - btn_w)//2, py + 90 + i*68, btn_w, btn_h)
            for i in range(len(btns))
        ]

        clock = pygame.time.Clock()
        while True:
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'resume'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, (_, result) in zip(rects, btns):
                        if rect.collidepoint(event.pos):
                            return result

            self.display_screen.blit(snapshot, (0, 0))
            self.display_screen.blit(dark, (0, 0))

            # Panel
            pygame.draw.rect(self.display_screen, (14, 12, 10), (px, py, pw, ph), border_radius=14)
            pygame.draw.rect(self.display_screen, (110, 98, 72), (px, py, pw, ph), 2, border_radius=14)

            title = f_title.render('PAUSED', True, (224, 204, 140))
            self.display_screen.blit(title, title.get_rect(center=(px + pw//2, py + 44)))

            seed_lbl = f_seed.render(f'Seed: {self.seed}', True, (120, 110, 86))
            self.display_screen.blit(seed_lbl, seed_lbl.get_rect(center=(px + pw//2, py + 70)))

            for rect, (label, _) in zip(rects, btns):
                hover = rect.collidepoint(mx, my)
                bg  = (74, 68, 52) if hover else (36, 32, 24)
                bdr = (200, 180, 100) if hover else (88, 80, 58)
                pygame.draw.rect(self.display_screen, bg,  rect, border_radius=8)
                pygame.draw.rect(self.display_screen, bdr, rect, 2, border_radius=8)
                txt = f_btn.render(label, True, (220, 210, 180))
                self.display_screen.blit(txt, txt.get_rect(center=rect.center))

            pygame.display.flip()
            clock.tick(60)

    # ------------------------------------------------------------------
    # Seamless floor texture
    # ------------------------------------------------------------------

    def _build_floor_surf(self):
        """Bake a tiling castle-stone surface one viewport + 1 tile in each direction."""
        ts = 96   # stone flag size — world-space pixels per slab
        self._floor_ts = ts
        cols = VIEWPORT_W // ts + 2
        rows = VIEWPORT_H // ts + 2
        surf = pygame.Surface((cols * ts, rows * ts))
        # Store world-grid offsets so we can reuse the same surface for any camera position
        # by seeding noise from world-grid coords at draw time.
        # Here we bake a reusable tile palette of 32 unique slabs, drawn by hashing world coords.
        self._floor_cols = cols
        self._floor_rows = rows
        self._floor_surf = surf   # will be filled per-frame cheaply via _draw_floor

    def _build_vignette(self) -> pygame.Surface:
        """Pre-render dark-edge vignette once; blit each frame at zero GC cost."""
        surf = pygame.Surface((VIEWPORT_W, VIEWPORT_H), pygame.SRCALPHA)
        cx, cy = VIEWPORT_W // 2, VIEWPORT_H // 2
        max_r = int(math.sqrt(cx * cx + cy * cy)) + 30
        steps = 20
        for i in range(steps):
            frac = i / (steps - 1)          # 0 = innermost ring, 1 = outermost
            r = int(max_r * (0.38 + frac * 0.62))
            alpha = int(115 * frac ** 2.4)  # stays clear in centre, dark at edges
            ring_w = max(5, max_r // steps + 3)
            pygame.draw.circle(surf, (0, 0, 0, alpha), (cx, cy), r, ring_w)
        return surf

    def _draw_floor(self):
        """Scroll the stone floor. Only redraws tile content when the camera crosses a tile boundary;
        smooth sub-tile scrolling is free (just a blit offset)."""
        ts = getattr(self, '_floor_ts', None)
        if ts is None:
            self._build_floor_surf()
            ts = self._floor_ts

        surf = self._floor_surf
        cols = self._floor_cols
        rows = self._floor_rows

        cam_x, cam_y = int(self.cam_x), int(self.cam_y)
        start_gx = cam_x // ts
        start_gy = cam_y // ts
        ox = cam_x % ts
        oy = cam_y % ts

        # Only rebuild tile content when the grid origin changes (roughly every 24 frames at walking speed)
        if start_gx != getattr(self, '_floor_gx', -9999) or start_gy != getattr(self, '_floor_gy', -9999):
            self._floor_gx = start_gx
            self._floor_gy = start_gy
            for row in range(rows):
                for col in range(cols):
                    gx = start_gx + col
                    gy = start_gy + row
                    n0 = _hash2(gx * 17 + 3,  gy * 13 + 7)
                    n1 = _hash2(gx * 7  + 31, gy * 29 + 5)
                    base_r = 32 + int(n0 * 10)
                    base_g = 29 + int(n0 * 8)
                    base_b = 26 + int(n0 * 7)
                    rx = col * ts
                    ry = row * ts
                    rect = pygame.Rect(rx, ry, ts, ts)
                    pygame.draw.rect(surf, (base_r, base_g, base_b), rect)
                    crack_c = (max(0, base_r-8), max(0, base_g-7), max(0, base_b-6))
                    if n1 < 0.30:
                        mid = int(ts * 0.4 + n1 * ts * 0.5)
                        pygame.draw.line(surf, crack_c, (rx+mid, ry+6), (rx+mid, ry+ts-6), 1)
                    elif n1 < 0.55:
                        mid = int(ts * 0.4 + (n1-0.3) * ts * 0.6)
                        pygame.draw.line(surf, crack_c, (rx+6, ry+mid), (rx+ts-6, ry+mid), 1)
                    grout = (max(0, base_r-14), max(0, base_g-12), max(0, base_b-10))
                    pygame.draw.rect(surf, grout, rect, 2)

        self.screen.blit(surf, (-ox, -oy))

    # ------------------------------------------------------------------
    # Spawn (guaranteed safe positions)
    # ------------------------------------------------------------------

    def _spawn_enemy(self):
        if self.boss_active:
            return
        # HP scales aggressively with kills
        tier = self.kills // 10
        base_hp = 60 + tier * 80
        is_mega = self.kills > 0 and self.kills % MEGA_BOSS_INTERVAL == 0
        is_mini = self.kills > 0 and self.kills % MINI_BOSS_INTERVAL == 0 and not is_mega

        if is_mega or is_mini:
            self.enemies.clear()
            self.bullets.clear()
            self.enemy_bullets.clear()
            bx, by = self.chunk_manager.get_safe_pos_near_room()

            if is_mega:
                # HP: starts at 3 000, +100 per kill
                mega_hp  = 3000 + self.kills * 100
                boss     = Enemy(bx, by, mega_hp, is_boss=True, is_final=True)
                # Speed: +0.8 % per kill, capped at 2.5×
                spd_mult = min(2.5, 1.0 + self.kills * 0.008)
                boss.speed      = random.uniform(0.9, 1.5) * spd_mult
                # Fire rate: starts at 60 frames, minimum 20
                boss.shoot_rate = max(20, 60 - self.kills // 4)
                # Phase length: starts at 250, minimum 100
                boss.phase_len  = max(100, 250 - self.kills)
            else:
                # Mini boss — cycle through IDs 1-8
                bid     = ((self.kills // MINI_BOSS_INTERVAL - 1) % 8) + 1
                # HP: starts at 400, +150 per tier (tier = kills // 10)
                mini_hp = 400 + tier * 150
                boss    = Enemy(bx, by, mini_hp, is_boss=True, boss_id=bid)
                # Speed: +1 % per kill, capped at 2.2×
                spd_mult = min(2.2, 1.0 + self.kills * 0.010)
                boss.speed      = random.uniform(0.7, 1.3) * spd_mult
                # Fire rate: starts at 90 frames, minimum 30
                boss.shoot_rate = max(30, 90 - self.kills // 3)
                # Phase length: starts at 300, minimum 120
                boss.phase_len  = max(120, 300 - self.kills)
                # Size grows slightly with kills (capped at 46)
                boss.size       = min(46, 34 + self.kills // 15)

            if not self.chunk_manager.is_pos_safe(boss.x, boss.y, boss.size):
                boss.x, boss.y = self.chunk_manager.get_safe_pos_near_room()
            self.enemies.append(boss)
            self.current_boss = boss
            self.boss_active  = True
            return

        # Regular enemy — 4 types, weights shift with kills
        rand = random.random()
        if self.kills < 20:
            if   rand < 0.40: etype, hp = 'normal',  base_hp
            elif rand < 0.65: etype, hp = 'fast',    int(base_hp*0.5)
            elif rand < 0.82: etype, hp = 'tank',    int(base_hp*2)
            else:             etype, hp = 'shooter', int(base_hp*0.7)
        else:
            if   rand < 0.25: etype, hp = 'normal',  base_hp
            elif rand < 0.45: etype, hp = 'fast',    int(base_hp*0.5)
            elif rand < 0.70: etype, hp = 'tank',    int(base_hp*2.2)
            else:             etype, hp = 'shooter', int(base_hp*0.7)

        _size_map = {'normal': 15, 'fast': 11, 'tank': 22, 'shooter': 14}
        check_r = _size_map.get(etype, 16) + 14
        for _ in range(400):
            ex, ey = self.chunk_manager.get_safe_pos_near_room()
            if not is_off_screen(ex-self.cam_x, ey-self.cam_y, VIEWPORT_W, VIEWPORT_H, margin=80):
                continue
            if not self.chunk_manager.is_pos_safe(ex, ey, check_r):
                continue
            e = Enemy(ex, ey, hp, enemy_type=etype)
            self.enemies.append(e)
            break

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> str:
        while True:
            self.frame += 1
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _save_mod.update_best_kills(self.kills)
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        result = self._pause_menu()
                        if result == 'save_quit':
                            _save_mod.save(self._save_state())
                            _save_mod.update_best_kills(self.kills)
                            return 'menu'
                        elif result == 'quit':
                            _save_mod.update_best_kills(self.kills)
                            return 'menu'
                        # 'resume' → fall through

            self._update(keys)
            self._draw()

            if self.kills >= WIN_KILLS:
                _save_mod.delete()
                _save_mod.update_best_kills(self.kills)
                return self._end_screen("VICTORY!", "You conquered the dungeon!", (100,255,120), (12,30,18))
            if self.player.health <= 0:
                _save_mod.delete()
                _save_mod.update_best_kills(self.kills)
                return self._end_screen("GAME OVER", f"Kills: {self.kills}", (255,80,80), (30,10,12))

            self.clock.tick(60)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, keys):
        p  = self.player
        cm = self.chunk_manager

        self.cam_x = clamp(p.x - VIEWPORT_W//2, 0, WORLD_SIZE - VIEWPORT_W)
        self.cam_y = clamp(p.y - VIEWPORT_H//2, 0, WORLD_SIZE - VIEWPORT_H)

        cm.load_chunks_around(p.x, p.y)
        cm.unload_distant(p.x, p.y)

        p.move(keys, cm)
        p.update_aim(self.enemies)
        p.update_orbital()
        p.update_magnet(self.items)

        # Auto-shoot
        if self.shoot_cd == 0 and p.has_target:
            ba = math.atan2(p.shoot_dir[1], p.shoot_dir[0])
            tip_x = p.x + math.cos(ba) * 27
            tip_y = p.y + math.sin(ba) * 27

            # Build barrel positions: main cannon + one pair per dual_gun stack
            perp_x = math.cos(ba + math.pi / 2)
            perp_y = math.sin(ba + math.pi / 2)
            gun_positions = [(tip_x, tip_y)]
            if p.has_dual_gun:
                fwd_x = p.x + math.cos(ba) * 22
                fwd_y = p.y + math.sin(ba) * 22
                for gn in range(p.dual_gun_count):
                    off = 10 + gn * 10
                    gun_positions.append((fwd_x + perp_x * off, fwd_y + perp_y * off))
                    gun_positions.append((fwd_x - perp_x * off, fwd_y - perp_y * off))

            step = 0.22
            shot_inaccuracy = max(0.02, Bullet.INACCURACY - p.steady_aim * 0.04)
            shot_speed = Bullet.SPEED * (p.speed / Player.BASE_SPEED)
            for bx, by in gun_positions:
                dirs = [[p.shoot_dir[0], p.shoot_dir[1]]]
                for k in range(1, p.multi_shot):
                    side = 1 if k % 2 == 1 else -1
                    off  = side * step * ((k + 1) // 2)
                    dirs.append([math.cos(ba + off), math.sin(ba + off)])
                for d in dirs:
                    self.bullets.append(Bullet(bx, by, d, p.damage, p.bullet_bounce, p.bullet_pierce,
                                               inaccuracy=shot_inaccuracy, speed=shot_speed))
            self.shoot_cd = p.fire_rate
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        if self.boss_active and self.current_boss not in self.enemies:
            self.boss_active  = False
            self.current_boss = None
            p.health = min(p.MAX_HEALTH, p.health + 3)

        if self._init_spawns_left > 0:
            self._init_spawn_timer += 1
            if self._init_spawn_timer >= 12:
                self._spawn_enemy()
                self._init_spawns_left -= 1
                self._init_spawn_timer  = 0
        if not self.boss_active and self._init_spawns_left <= 0:
            self.spawn_timer += 1
            delay = max(SPAWN_DELAY_MIN, SPAWN_DELAY_BASE - self.kills*SPAWN_KILLS_STEP)
            if self.spawn_timer >= delay and len(self.enemies) < MAX_ENEMIES:
                self._spawn_enemy()
                self.spawn_timer = 0

        self._update_player_bullets()
        self._update_enemies()
        self._update_enemy_bullets()
        self._pickup_items()

        for popup in self.popups:
            popup.update()
        self.popups = [pop for pop in self.popups if pop.lifetime > 0]

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        if len(self.particles) > 120:
            self.particles = self.particles[-120:]

    # ------------------------------------------------------------------
    # Player bullet update
    # ------------------------------------------------------------------

    def _update_player_bullets(self):
        ws = WORLD_SIZE
        keep = []
        if len(self.bullets) > 500:
            self.bullets = self.bullets[-500:]

        # Sub-step size must be smaller than Wall.PLANE_THICKNESS (5 px) to
        # prevent tunnelling.  ceil(speed / 4) steps keeps each step ≤ 4 px.
        _STEP = 4.0
        cs = self.chunk_manager.chunk_size
        wall_cache: dict[tuple[int,int], list] = {}

        for b in self.bullets:
            b.lifetime -= 1
            if b.lifetime <= 0:
                continue

            steps = max(1, math.ceil(b.speed / _STEP))
            sdx   = b.dir[0] * b.speed / steps
            sdy   = b.dir[1] * b.speed / steps

            hit_wall = False
            for _ in range(steps):
                b.x += sdx
                b.y += sdy

                if b.x < 0 or b.x > ws or b.y < 0 or b.y > ws:
                    hit_wall = True
                    break

                ck = (int(b.x) // cs, int(b.y) // cs)
                if ck not in wall_cache:
                    wall_cache[ck] = self.chunk_manager.get_nearby_walls(b.x, b.y)

                for wall in wall_cache[ck]:
                    if wall.collides(b.x, b.y, b.size):
                        if b.bounces_left > 0 and b.try_bounce(wall, self.frame):
                            b.x += b.dir[0] * b.speed * 2
                            b.y += b.dir[1] * b.speed * 2
                        else:
                            hit_wall = True
                        break

                if hit_wall:
                    break

            if not hit_wall:
                keep.append(b)

        self.bullets = keep

    # ------------------------------------------------------------------
    # Enemy update
    # ------------------------------------------------------------------

    def _update_enemies(self):
        p = self.player
        px, py = p.x, p.y
        bullets_to_remove: set[int] = set()
        still_alive: list[Enemy] = []

        # Bucket bullets into a spatial grid — avoids O(E×B) full scan
        _BCELL = 80
        bullet_grid: dict[tuple[int,int], list] = {}
        for _b in self.bullets:
            _k = (int(_b.x) // _BCELL, int(_b.y) // _BCELL)
            if _k not in bullet_grid:
                bullet_grid[_k] = []
            bullet_grid[_k].append(_b)

        for enemy in self.enemies:
            eid = id(enemy)
            dx, dy = enemy.x-px, enemy.y-py
            dist_sq = dx*dx + dy*dy

            if not enemy.is_boss:
                if dist_sq > enemy.UNLOAD_DIST_SQ:
                    enemy.frames_far += 1
                    if enemy.frames_far > enemy.UNLOAD_DELAY:
                        continue
                else:
                    enemy.frames_far = 0

            if enemy.is_boss or self.frame % 10 == 0:
                enemy.cached_los = self.chunk_manager.has_los(enemy.x, enemy.y, px, py)

            enemy.update(px, py, self.chunk_manager, enemy.cached_los)

            if enemy.can_shoot() and enemy.cached_los:
                self.enemy_bullets.extend(enemy.shoot(px, py))

            # Final boss minion spawn
            if enemy.is_final and len(self.enemies) < 12:
                enemy.minion_spawn_timer += 1
                if enemy.minion_spawn_timer >= 200:
                    enemy.minion_spawn_timer = 0
                    for _ in range(20):
                        a = random.random()*2*math.pi
                        mx = enemy.x + math.cos(a)*120
                        my = enemy.y + math.sin(a)*120
                        if self.chunk_manager.is_pos_safe(mx, my, 16):
                            mtype = random.choice(['fast','shooter','sniper'])
                            minion = Enemy(mx, my, 100, enemy_type=mtype)
                            still_alive.append(minion)
                            break

            # Contact damage
            cdist = p.SIZE + enemy.size
            if dist_sq < cdist*cdist:
                contact_dmg = {'tank': 3, 'fast': 1, 'normal': 1, 'shooter': 1}.get(enemy.enemy_type, 1)
                p.take_damage(contact_dmg)
                if not enemy.is_boss:
                    self.kills += 1
                    style = ENEMY_STYLES.get(enemy.enemy_type, {'rim': (255, 100, 60)})
                    self.particles += _spawn_particles(enemy.x, enemy.y, style['rim'],
                                                       count=14, speed=4.5, size=4, life=35)
                    self.items.append(Item(enemy.x, enemy.y, self._random_item_type()))
                    continue

            # Orbital damage
            if p.has_orbital and dist_sq < 7000 and self.frame % 3 == 0:
                count = min(3+p.orbital_count-1, 6)
                for i in range(count):
                    a = p.orbital_angle + i*2*math.pi/count
                    sdx = px + math.cos(a)*55 - enemy.x
                    sdy = py + math.sin(a)*55 - enemy.y
                    if sdx*sdx + sdy*sdy < (14+enemy.size)**2:
                        enemy.health -= 3

            # Bullet hits — only check bullets in nearby grid cells
            killed = False
            _ecx = int(enemy.x) // _BCELL
            _ecy = int(enemy.y) // _BCELL
            _nearby: list = []
            for _ddx in range(-1, 2):
                for _ddy in range(-1, 2):
                    _nearby.extend(bullet_grid.get((_ecx+_ddx, _ecy+_ddy), []))
            for b in _nearby:
                if id(b) in bullets_to_remove: continue
                if killed: break
                if id(enemy) in b.hit_enemies: continue
                bdx, bdy = b.x-enemy.x, b.y-enemy.y
                if bdx*bdx+bdy*bdy < (b.size+enemy.size)**2:
                    b.hit_enemies.add(eid)
                    enemy.health -= b.damage

                    # Explosive rounds — AoE splash to nearby enemies
                    if p.bullet_explode > 0:
                        blast_r = 40 + p.bullet_explode * 18
                        for other in still_alive:
                            if other is enemy: continue
                            odx, ody = other.x - b.x, other.y - b.y
                            if odx*odx + ody*ody < blast_r*blast_r:
                                other.health -= max(1, b.damage // 2)

                    if b.pierce_left > 0:
                        b.pierce_left -= 1
                    elif b.bounces_left > 0:
                        dist2 = math.sqrt(bdx*bdx+bdy*bdy)
                        if dist2 > 0: b.dir = [bdx/dist2, bdy/dist2]
                        b.bounces_left -= 1
                        b.lifetime = min(b.lifetime, 60)
                        b.x += b.dir[0]*b.speed*2
                        b.y += b.dir[1]*b.speed*2
                    else:
                        bullets_to_remove.add(id(b))

                    if enemy.health <= 0:
                        self.kills += 1
                        killed = True
                        itype = self._boss_item_type() if enemy.is_boss else self._random_item_type()
                        self.items.append(Item(enemy.x, enemy.y, itype))
                        self.popups.append(Popup(
                            '+1 KILL', enemy.x, enemy.y-30, (255,220,60)
                        ))
                        # Death particles
                        style = ENEMY_STYLES.get(enemy.enemy_type, {'rim': (255,120,60)})
                        pcol = style['rim'] if enemy.enemy_type in ENEMY_STYLES else (255,140,60)
                        self.particles += _spawn_particles(enemy.x, enemy.y, pcol,
                                                           count=18, speed=5.0, size=5, life=40)
                        if enemy.is_boss:
                            self.particles += _spawn_particles(enemy.x, enemy.y, (255,255,100),
                                                               count=30, speed=7.0, size=7, life=55)

            if not killed:
                still_alive.append(enemy)

        self.bullets = [b for b in self.bullets if id(b) not in bullets_to_remove]
        self.enemies = still_alive

    def _random_item_type(self) -> str:
        r = random.random()
        if   r < 0.12: return 'health'
        elif r < 0.24: return 'firerate'
        elif r < 0.36: return 'multishot'
        elif r < 0.50: return 'damage'
        elif r < 0.62: return 'bounce'
        elif r < 0.74: return 'pierce'
        elif r < 0.87: return 'speed'
        else:          return 'steady'

    def _boss_item_type(self) -> str:
        return random.choice(['orbital', 'dual_gun', 'explode', 'magnet'])

    # ------------------------------------------------------------------
    # Enemy bullet update
    # ------------------------------------------------------------------

    def _update_enemy_bullets(self):
        p  = self.player
        ws = WORLD_SIZE
        cdist_sq = (p.SIZE + 7) ** 2
        if len(self.enemy_bullets) > 5000:
            self.enemy_bullets = self.enemy_bullets[-5000:]
        keep = []
        for b in self.enemy_bullets:
            b.update(p.x, p.y)
            if b.lifetime <= 0 or b.x<0 or b.x>ws or b.y<0 or b.y>ws:
                continue
            dx, dy = b.x-p.x, b.y-p.y
            if dx*dx+dy*dy < cdist_sq:
                # Damage by bullet type — shooter=1, tank cannon=3, tank mortar=2, boss bullets vary
                if b.is_cannon:                dmg = 3
                elif b.bullet_type == 'mortar': dmg = 2
                elif b.bullet_type == 'laser':  dmg = 2
                elif b.bullet_type == 'snipe':  dmg = 3
                elif b.bullet_type == 'homing': dmg = 2
                else:                           dmg = 1
                p.take_damage(dmg)
                continue
            if self.chunk_manager.tilemap.check_collision(b.x, b.y, b.size):
                continue
            keep.append(b)
        self.enemy_bullets = keep

    # ------------------------------------------------------------------
    # Item pickup
    # ------------------------------------------------------------------

    def _pickup_items(self):
        p = self.player
        keep = []
        for item in self.items:
            dx, dy = item.x-p.x, item.y-p.y
            if dx*dx+dy*dy < (item.size+p.SIZE+8)**2:
                cfg = ITEM_CONFIG.get(item.type, {})
                self.popups.append(Popup(
                    cfg.get('name', item.type), item.x, item.y-25,
                    cfg.get('color', C_WHITE)
                ))
                item.apply_to(p)
            else:
                keep.append(item)
        self.items = keep

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        scr = self.screen
        cx, cy = self.cam_x, self.cam_y
        p = self.player
        VW, VH = VIEWPORT_W, VIEWPORT_H

        # Frustum helper — True if world-space (wx, wy) is within the viewport + margin
        def vis(wx, wy, m=24):
            sx = wx - cx; sy = wy - cy
            return -m < sx < VW + m and -m < sy < VH + m

        # Seamless floor
        self._draw_floor()

        # Tiles
        self.wall_renderer.draw_tiles(scr, cx, cy, VW, VH, self.frame)

        # Orbital + Player
        p.draw_orbital(scr, cx, cy, self.frame)
        p.draw_magnet(scr, cx, cy)
        p.draw(scr, cx, cy, self.frame)

        # Player bullets — skip anything outside the viewport
        for b in self.bullets:
            if vis(b.x, b.y):
                b.draw(scr, cx, cy)

        # Enemy bullets — same cull
        for b in self.enemy_bullets:
            if vis(b.x, b.y):
                b.draw(scr, cx, cy)

        # Enemies and bosses — always drawn (no culling)
        for e in self.enemies:
            e.draw(scr, cx, cy)

        # Items — cull with a larger margin so magnetised items just off-screen still appear smoothly
        for item in self.items:
            if vis(item.x, item.y, m=60):
                item.draw(scr, cx, cy)

        # Particles — tight cull, they're tiny
        for part in self.particles:
            if vis(part.x, part.y, m=8):
                part.draw(scr, cx, cy)

        # Popups — generous margin so text isn't clipped mid-float
        for popup in self.popups:
            if vis(popup.x, popup.y, m=80):
                popup.draw(scr, cx, cy)

        # Vignette (dark-edge overlay, pre-cached)
        scr.blit(self._vignette, (0, 0))

        # HUD
        self._draw_hud()

        # Composite
        self._flip()

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _draw_hud(self):
        self._draw_powerup_panel()
        self._draw_kill_counter()
        self._draw_health_bar()
        if self.boss_active and self.current_boss:
            self._draw_boss_bar()
            self._draw_boss_pointer()

    def _draw_powerup_panel(self):
        scr = self.screen
        p   = self.player

        px, py = 12, 12
        pw  = 190   # column width for right-aligning values
        sf  = _get_font(14)
        hf  = _get_font(12)
        y   = py
        lh  = 20
        sh  = 16   # section header height

        def _txt(text, color, bx, by):
            shadow = sf.render(text, True, (0, 0, 0))
            scr.blit(shadow, (bx+1, by+1))
            scr.blit(sf.render(text, True, color), (bx, by))

        def section(label):
            nonlocal y
            y += 4
            lbl = hf.render(label, True, (110, 105, 90))
            scr.blit(lbl, (px + 2, y))
            pygame.draw.line(scr, (70, 65, 52),
                             (px + 2, y + sh - 2), (px + pw - 2, y + sh - 2), 1)
            y += sh

        def row(label, val, col):
            nonlocal y
            # val is a number or string; active when non-zero / non-default
            if isinstance(val, str):
                active = val not in ('0', '100%', 'NO')
            else:
                active = val != 0
            dot_c = col if active else (50, 48, 42)
            pygame.draw.circle(scr, dot_c, (px + 6, y + 8), 4)
            lbl_c = (200, 195, 185) if active else (95, 90, 82)
            val_c = col if active else (85, 82, 75)
            _txt(label, lbl_c, px + 16, y)
            vs  = str(val)
            vw  = sf.size(vs)[0]
            _txt(vs, val_c, px + pw - vw, y)
            y += lh

        speed_pct = int((p.speed / Player.BASE_SPEED) * 100)
        mag_range = int(200 + p.magnet_count * 120) if p.magnet_count else 0
        blast_r   = 40 + p.bullet_explode * 18

        section('— BULLET —')
        row('Fire Rate',   f'{p.get_fire_rate_pct()}%',  (255, 100, 255))
        row('Multi-Shot',  p.multi_shot,                  (100, 200, 255))
        row('Damage',      p.damage,                      (255, 150,  50))
        row('Bounce',      p.bullet_bounce,               (  0, 255, 220))
        row('Pierce',      p.bullet_pierce,               (220,  60, 255))

        section('— BODY —')
        row('Speed',       f'{speed_pct}%',               (100, 255, 100))
        row('Steady Aim',  p.steady_aim,                  (180, 255, 180))

        section('— SPECIAL —')
        row('Orbital Saws',p.orbital_count,               (255, 210,   0))
        row('Dual Guns',   p.dual_gun_count,              (255, 100, 100))
        row('Blast Radius',blast_r if p.bullet_explode else 0, (255, 160, 30))
        row('Magnet Range',mag_range if p.magnet_count else 0, (100, 200, 255))

    def _draw_kill_counter(self):
        scr = self.screen
        kf  = _get_font(22)
        kills_txt = f'{self.kills}  KILLS'
        cx = VIEWPORT_W // 2
        # Drop shadow then text
        sh = kf.render(kills_txt, True, (0, 0, 0))
        tx = kf.render(kills_txt, True, (255, 230, 80))
        scr.blit(sh, (cx - sh.get_width()//2 + 2, 14))
        scr.blit(tx, (cx - tx.get_width()//2,     12))
        # Next boss indicator
        next_boss = MINI_BOSS_INTERVAL - (self.kills % MINI_BOSS_INTERVAL)
        if next_boss == MINI_BOSS_INTERVAL:
            next_boss = 0  # just spawned one
        hint_f = _get_font(13)
        is_next_mega = ((self.kills // MINI_BOSS_INTERVAL + 1) * MINI_BOSS_INTERVAL) % MEGA_BOSS_INTERVAL == 0
        boss_label = 'MEGA BOSS' if is_next_mega else 'BOSS'
        if next_boss > 0:
            hint = hint_f.render(f'{boss_label} IN {next_boss}', True, (200, 100, 60))
            scr.blit(hint, hint.get_rect(center=(cx, 12 + tx.get_height() + 5)))

    def _draw_health_bar(self):
        scr = self.screen
        p   = self.player
        bw  = 320
        bx  = VIEWPORT_W - bw - 10
        by  = 10
        seg_count = p.MAX_HEALTH
        seg_w = bw // seg_count - 1
        seg_h = 18
        for i in range(seg_count):
            sx = bx + i * (seg_w + 1)
            pygame.draw.rect(scr, (30, 35, 50), (sx, by, seg_w, seg_h), border_radius=2)
            if i < p.health:
                pct = p.health / p.MAX_HEALTH
                hc  = C_HEALTH_GREEN if pct > 0.5 else (C_HEALTH_YEL if pct > 0.25 else C_HEALTH_RED)
                pygame.draw.rect(scr, hc, (sx, by, seg_w, seg_h), border_radius=2)
                pygame.draw.rect(scr, (*hc, 80), (sx, by, seg_w, seg_h // 2), border_radius=2)


    def _draw_boss_bar(self):
        scr  = self.screen
        boss = self.current_boss
        if boss is None: return

        if boss.is_final:
            style = BOSS_FINAL_STYLE
        else:
            style = BOSS_STYLES.get(boss.boss_id, BOSS_STYLES[1])

        body_col = style['body']
        rim_col  = style['rim']
        name     = style['name']

        bw, bh = 640, 36
        bx = (VIEWPORT_W - bw) // 2
        by = 14

        # Backing panel (solid, no SRCALPHA)
        pygame.draw.rect(scr, (8, 8, 18), (bx-8, by-20, bw+16, bh+40), border_radius=12)
        pygame.draw.rect(scr, rim_col,    (bx-8, by-20, bw+16, bh+40), 1, border_radius=12)

        # Boss name
        nf = _get_font(15)
        nlbl = nf.render(f'⟨ {name} ⟩', True, rim_col)
        scr.blit(nlbl, ((VIEWPORT_W - nlbl.get_width())//2, by - 16))

        # Main bar track
        pygame.draw.rect(scr, (20, 10, 30), (bx, by, bw, bh), border_radius=6)

        pct = boss.health / max(boss.max_health, 1)
        fw  = int(bw * pct)

        # Segment markers (every 25%)
        for seg in [0.25, 0.5, 0.75]:
            mx = bx + int(bw * seg)
            pygame.draw.line(scr, (30, 20, 40), (mx, by), (mx, by+bh), 2)

        # Health fill gradient simulation (3 layers)
        if fw > 0:
            hc  = body_col if pct > 0.5 else ((200, 80, 30) if pct > 0.25 else C_HEALTH_RED)
            pygame.draw.rect(scr, hc, (bx, by, fw, bh), border_radius=6)
            # Bright top highlight (solid lighter rect, no SRCALPHA)
            hl_c = tuple(min(255, ch + 40) for ch in hc)
            pygame.draw.rect(scr, hl_c, (bx, by, fw, bh//3), border_radius=4)
            # Pulse flicker when low
            if pct < 0.25 and (self.frame // 6) % 2 == 0:
                pygame.draw.rect(scr, (255, 60, 60), (bx, by, fw, bh), 2, border_radius=6)

        # Rim
        pygame.draw.rect(scr, rim_col, (bx, by, bw, bh), 2, border_radius=6)

        # HP text
        hpf = _get_font(17)
        hp_lbl = hpf.render(f'{max(0, int(boss.health))} / {boss.max_health}', True, C_WHITE)
        scr.blit(hp_lbl, hp_lbl.get_rect(center=(VIEWPORT_W//2, by+bh//2)))

    def _draw_boss_pointer(self):
        if not self.current_boss: return
        scr  = self.screen
        boss = self.current_boss
        bsx  = boss.x - self.cam_x
        bsy  = boss.y - self.cam_y
        if not is_off_screen(bsx, bsy, VIEWPORT_W, VIEWPORT_H):
            return
        margin = 55
        ccx, ccy = VIEWPORT_W//2, VIEWPORT_H//2
        dx, dy   = bsx - ccx, bsy - ccy
        angle    = math.atan2(dy, dx)
        if abs(dx) > abs(dy):
            px_p = VIEWPORT_W-margin if dx>0 else margin
            py_p = clamp(ccy + (px_p-ccx)*math.tan(angle), margin, VIEWPORT_H-margin)
        else:
            py_p_f = float(VIEWPORT_H-margin if dy>0 else margin)
            tan_a  = math.tan(angle)
            px_p   = clamp(ccx + (py_p_f-ccy)/tan_a if tan_a!=0 else ccx, margin, VIEWPORT_W-margin)
            py_p   = py_p_f

        if self.current_boss.is_final:
            style = BOSS_FINAL_STYLE
        else:
            style = BOSS_STYLES.get(self.current_boss.boss_id, BOSS_STYLES[1])
        pulse = 0.6 + 0.4*math.sin(self.frame*0.12)
        col = tuple(int(c*pulse) for c in style['rim'])
        sz = 18
        pts = [
            (px_p + math.cos(angle)*sz,        py_p + math.sin(angle)*sz),
            (px_p + math.cos(angle+2.4)*sz*0.6, py_p + math.sin(angle+2.4)*sz*0.6),
            (px_p + math.cos(angle-2.4)*sz*0.6, py_p + math.sin(angle-2.4)*sz*0.6),
        ]
        pygame.draw.polygon(scr, col, pts)
        pygame.draw.polygon(scr, C_WHITE, pts, 2)

    # ------------------------------------------------------------------
    # End screens
    # ------------------------------------------------------------------

    def _end_screen(self, title, subtitle, title_color, bg_color) -> str:
        tf = pygame.font.SysFont('segoeui', 64, bold=True)
        mf = pygame.font.SysFont('segoeui', 30)
        hint_f = pygame.font.SysFont('segoeui', 20)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE): return 'menu'
            self.screen.fill(bg_color)
            t1 = tf.render(title, True, title_color)
            t2 = mf.render(subtitle, True, C_WHITE)
            t3 = hint_f.render('Press ENTER or ESC to continue', True, C_GREY)
            self.screen.blit(t1, t1.get_rect(center=(VIEWPORT_W//2, VIEWPORT_H//2 - 60)))
            self.screen.blit(t2, t2.get_rect(center=(VIEWPORT_W//2, VIEWPORT_H//2 + 20)))
            self.screen.blit(t3, t3.get_rect(center=(VIEWPORT_W//2, VIEWPORT_H//2 + 70)))
            self.display_screen.fill((0,0,0))
            scaled = pygame.transform.scale(self.screen,
                (int(VIEWPORT_W*self.scale), int(VIEWPORT_H*self.scale)))
            self.display_screen.blit(scaled, (self.offset_x, self.offset_y))
            pygame.display.flip()
            self.clock.tick(60)


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def _draw_menu_bg(surf: pygame.Surface) -> None:
    """Stone-textured dark background for the shooter menu."""
    w, h = surf.get_size()
    surf.fill((16, 14, 12))
    ts = 80
    for gx in range(w // ts + 2):
        for gy in range(h // ts + 2):
            n0 = _hash2(gx * 17 + 5, gy * 13 + 3)
            n1 = _hash2(gx * 7 + 31, gy * 29 + 11)
            r = 28 + int(n0 * 10)
            g = 25 + int(n0 * 8)
            b = 22 + int(n0 * 7)
            rect = pygame.Rect(gx * ts, gy * ts, ts, ts)
            pygame.draw.rect(surf, (r, g, b), rect)
            grout = (max(0, r - 10), max(0, g - 9), max(0, b - 8))
            pygame.draw.rect(surf, grout, rect, 2)
            if n1 < 0.3:
                mid = int(ts * 0.4 + n1 * ts * 0.5)
                pygame.draw.line(surf, (max(0, r-6), max(0, g-5), max(0, b-4)),
                                 (gx*ts + mid, gy*ts + 6), (gx*ts + mid, gy*ts + ts - 6), 1)


def run_shooter_menu(screen: pygame.Surface) -> str:
    """Shooter main menu. Returns 'menu' or 'quit'."""
    dw, dh = screen.get_size()

    # Pre-bake background once
    bg = pygame.Surface((dw, dh))
    _draw_menu_bg(bg)

    # Fonts
    f_title  = _get_font(62)
    f_sub    = _get_font(24)
    f_btn    = _get_font(22)
    f_small  = _get_font(15)
    f_seed   = _get_font(17)

    cx = dw // 2
    cy = dh // 2

    # Seed state
    current_seed  = _save_mod.new_seed()
    seed_editing  = False
    seed_input    = current_seed

    # Button layout
    btn_w, btn_h = 300, 58
    new_rect  = pygame.Rect(cx - btn_w//2, cy - 20,        btn_w, btn_h)
    cont_rect = pygame.Rect(cx - btn_w//2, cy - 20 + 78,   btn_w, btn_h)
    back_rect = pygame.Rect(cx - btn_w//2, cy - 20 + 156,  btn_w, btn_h)

    # Seed area
    seed_rect = pygame.Rect(cx - 140, dh - 110, 220, 36)
    shuf_rect = pygame.Rect(cx +  88, dh - 110, 120, 36)

    clock = pygame.time.Clock()

    def _btn(rect, label, hover, active=True):
        if not active:
            pygame.draw.rect(screen, (30, 28, 22), rect, border_radius=9)
            pygame.draw.rect(screen, (55, 50, 40), rect, 2, border_radius=9)
            t = f_btn.render(label, True, (70, 65, 55))
        else:
            bg_c  = (74, 68, 52) if hover else (40, 36, 28)
            bdr_c = (210, 185, 105) if hover else (95, 86, 64)
            pygame.draw.rect(screen, bg_c,  rect, border_radius=9)
            pygame.draw.rect(screen, bdr_c, rect, 2, border_radius=9)
            t = f_btn.render(label, True, (230, 215, 175))
        screen.blit(t, t.get_rect(center=rect.center))

    while True:
        mx, my = pygame.mouse.get_pos()
        has_save = _save_mod.has_save()
        best     = _save_mod.get_best_kills()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if event.type == pygame.KEYDOWN:
                if seed_editing:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        current_seed = seed_input.upper() if seed_input else _save_mod.new_seed()
                        seed_editing = False
                    elif event.key == pygame.K_BACKSPACE:
                        seed_input = seed_input[:-1]
                    elif len(seed_input) < 12 and event.unicode.isalnum():
                        seed_input = (seed_input + event.unicode).upper()
                else:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'

            if event.type == pygame.MOUSEBUTTONDOWN:
                if seed_editing:
                    if not seed_rect.collidepoint(event.pos):
                        current_seed = seed_input.upper() if seed_input else _save_mod.new_seed()
                        seed_editing = False

                if new_rect.collidepoint(event.pos) and not seed_editing:
                    game = ShooterGame(screen, seed=current_seed)
                    result = game.run()
                    if result == 'quit':
                        return 'quit'
                    # Refresh bg in case display changed
                    bg.fill((0, 0, 0))
                    _draw_menu_bg(bg)
                    current_seed = _save_mod.new_seed()

                elif cont_rect.collidepoint(event.pos) and has_save and not seed_editing:
                    save_data = _save_mod.load()
                    if save_data:
                        game = ShooterGame(screen, seed=save_data.get('seed', current_seed),
                                           save_data=save_data)
                        result = game.run()
                        if result == 'quit':
                            return 'quit'
                        bg.fill((0, 0, 0))
                        _draw_menu_bg(bg)

                elif back_rect.collidepoint(event.pos) and not seed_editing:
                    return 'menu'

                elif shuf_rect.collidepoint(event.pos) and not seed_editing:
                    current_seed = _save_mod.new_seed()
                    seed_input   = current_seed

                elif seed_rect.collidepoint(event.pos):
                    seed_editing = True
                    seed_input   = current_seed

        # --- Draw ---
        screen.blit(bg, (0, 0))

        # Title
        t1 = f_title.render('THE POWER OF 50', True, (214, 188, 110))
        t2 = f_sub.render('— D U N G E O N —', True, (160, 80, 60))
        screen.blit(t1, t1.get_rect(center=(cx, cy - 160)))
        screen.blit(t2, t2.get_rect(center=(cx, cy - 100)))

        # Best score
        if best > 0:
            bs = f_small.render(f'Best run: {best} kills', True, (130, 160, 110))
            screen.blit(bs, bs.get_rect(center=(cx, cy - 66)))

        # Buttons
        _btn(new_rect,  '▶  NEW GAME',  new_rect.collidepoint(mx, my))
        _btn(cont_rect, '⟲  CONTINUE',  cont_rect.collidepoint(mx, my), active=has_save)
        _btn(back_rect, '←  BACK',      back_rect.collidepoint(mx, my))

        # Save indicator under Continue
        if has_save:
            sd = _save_mod.load()
            if sd:
                info = f_small.render(
                    f"  {sd.get('kills', 0)} kills · seed {sd.get('seed','?')}",
                    True, (140, 160, 110))
                screen.blit(info, info.get_rect(midleft=(cont_rect.left + 8, cont_rect.bottom + 8)))

        # Seed area
        seed_bg = (28, 30, 22) if seed_editing else (22, 20, 16)
        seed_bdr = (180, 200, 100) if seed_editing else (80, 76, 56)
        pygame.draw.rect(screen, seed_bg,  seed_rect, border_radius=6)
        pygame.draw.rect(screen, seed_bdr, seed_rect, 2, border_radius=6)
        disp_seed = seed_input if seed_editing else current_seed
        if seed_editing and (pygame.time.get_ticks() // 500) % 2 == 0:
            disp_seed += '|'
        slbl = f_seed.render(disp_seed, True, (200, 210, 160))
        screen.blit(slbl, slbl.get_rect(midleft=(seed_rect.left + 8, seed_rect.centery)))

        hover_shuf = shuf_rect.collidepoint(mx, my)
        pygame.draw.rect(screen, (58, 54, 40) if hover_shuf else (32, 30, 22), shuf_rect, border_radius=6)
        pygame.draw.rect(screen, (160, 145, 90) if hover_shuf else (72, 66, 48), shuf_rect, 2, border_radius=6)
        sl = f_small.render('Shuffle', True, (200, 190, 150))
        screen.blit(sl, sl.get_rect(center=shuf_rect.center))

        seed_hint = f_small.render('Seed (click to edit)', True, (90, 84, 64))
        screen.blit(seed_hint, seed_hint.get_rect(midbottom=(seed_rect.centerx, seed_rect.top - 4)))

        pygame.display.flip()
        clock.tick(60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(screen: pygame.Surface) -> str:
    return run_shooter_menu(screen)