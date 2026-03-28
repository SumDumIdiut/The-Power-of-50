"""
Shooter Game - Wall Renderer (rewritten)

Seamless tiling via per-cell hash noise — no visible tile borders.
Per-tile micro-variation in colour so walls read as one organic surface.
Pre-baked surfaces keyed by (neighbour_count, noise_bucket) for variety.
"""
from __future__ import annotations
import pygame


def _hash2(x: int, y: int) -> float:
    n = x * 73856093 ^ y * 19349663
    n = (n ^ (n >> 13)) * 1664525 + 1013904223
    return (n & 0xFFFFFF) / 0xFFFFFF


_BASE_STYLE: dict[int, tuple] = {
    4: ((58, 54, 48),  (82, 76, 68),   (40, 37, 32)),
    3: ((68, 63, 56),  (96, 89, 78),   (48, 44, 38)),
    2: ((76, 70, 62),  (108,100, 88),  (54, 50, 44)),
    1: ((84, 78, 69),  (118,110, 96),  (60, 55, 48)),
    0: ((88, 82, 72),  (122,114,100),  (62, 57, 50)),
}
_VARIANTS = 4


def _vary(colour: tuple, amount: int) -> tuple:
    r, g, b = colour
    return (max(0,min(255,r+amount)), max(0,min(255,g+amount)), max(0,min(255,b+amount)))


def _make_base_surface(tile_size, fill, variant=0):
    """Flat-filled tile with subtle micro-variation — no bevel lines."""
    shift = (variant - 1) * 4
    fill  = _vary(fill, shift)
    surf  = pygame.Surface((tile_size, tile_size))
    surf.fill(fill)
    t = tile_size
    # Very faint interior detail lines for texture, not at edges
    if variant == 1:
        mid = t // 2
        c = _vary(fill, -5)
        pygame.draw.line(surf, c, (mid, 3), (mid, t - 3), 1)
    elif variant == 2:
        mid = t // 2
        c = _vary(fill, -5)
        pygame.draw.line(surf, c, (3, mid), (t - 3, mid), 1)
    elif variant == 3:
        c = _vary(fill, -4)
        pygame.draw.line(surf, c, (3, 3), (t - 3, t - 3), 1)
    return surf


class WallRenderer:
    UNLOAD_DELAY = 180
    CHUNK_TILES  = 10

    def __init__(self, tilemap) -> None:
        self.tilemap   = tilemap
        self.tile_size = tilemap.tile_size
        # Pre-bake one base surface per (neighbor_count, variant)
        self._surfaces: dict[tuple[int,int], pygame.Surface] = {}
        for n, (fill, *_) in _BASE_STYLE.items():
            for v in range(_VARIANTS):
                self._surfaces[(n, v)] = _make_base_surface(self.tile_size, fill, v)
        self._chunk_last_seen: dict[tuple[int,int], int] = {}

    def _edge_col(self, fill, exposed_top, exposed_left):
        """Return subtle edge highlight colour for exposed faces only."""
        return _vary(fill, 18 if (exposed_top or exposed_left) else 0)

    def draw_tiles(self, screen, camera_x, camera_y, screen_w, screen_h, frame=0):
        ts    = self.tile_size
        tiles = self.tilemap.tiles
        x0 = max(0, int(camera_x // ts) - 1)
        y0 = max(0, int(camera_y // ts) - 1)
        x1 = int((camera_x + screen_w) // ts) + 2
        y1 = int((camera_y + screen_h) // ts) + 2

        # Group by surface key for batched blitting
        by_style: dict[tuple, list] = {k: [] for k in self._surfaces}
        # Collect exposed-edge info separately
        exposed: dict[tuple[int,int], tuple[bool,bool,bool,bool]] = {}

        for gx in range(x0, x1):
            for gy in range(y0, y1):
                ck = (gx // self.CHUNK_TILES, gy // self.CHUNK_TILES)
                self._chunk_last_seen[ck] = frame
                info = tiles.get((gx, gy))
                if info is None:
                    continue
                n   = info["neighbor_count"]
                v   = int(_hash2(gx, gy) * _VARIANTS) % _VARIANTS
                key = (n, v)
                sx  = int(gx * ts - camera_x)
                sy  = int(gy * ts - camera_y)
                by_style[key].append((sx, sy))
                # Which faces are open (no adjacent solid tile)?
                open_top    = (gx, gy - 1) not in tiles
                open_bottom = (gx, gy + 1) not in tiles
                open_left   = (gx - 1, gy) not in tiles
                open_right  = (gx + 1, gy) not in tiles
                exposed[(sx, sy)] = (open_top, open_bottom, open_left, open_right)

        # Blit base surfaces
        for key, positions in by_style.items():
            if not positions:
                continue
            surf = self._surfaces[key]
            for sx, sy in positions:
                screen.blit(surf, (sx, sy))

        # Draw edge highlights only on exposed faces — this kills all interior seams
        for (sx, sy), (ot, ob, ol, or_) in exposed.items():
            # Deduce fill from neighbor count stored implicitly — use a neutral highlight
            light = (120, 112, 96)
            dark  = (32,  28,  22)
            if ot:  pygame.draw.line(screen, light, (sx, sy),         (sx+ts-1, sy),         2)
            if ol:  pygame.draw.line(screen, light, (sx, sy),         (sx, sy+ts-1),         2)
            if ob:  pygame.draw.line(screen, dark,  (sx, sy+ts-1),   (sx+ts-1, sy+ts-1),    2)
            if or_: pygame.draw.line(screen, dark,  (sx+ts-1, sy),   (sx+ts-1, sy+ts-1),    2)

        stale = [ck for ck, last in self._chunk_last_seen.items() if frame - last > self.UNLOAD_DELAY]
        for ck in stale:
            del self._chunk_last_seen[ck]