"""
Shooter Game - Helper / Utility Functions
Pure functions only — no pygame dependency, no sprite/asset references.
"""
from __future__ import annotations
import math
import random


# ---------------------------------------------------------------------------
# Vector / math
# ---------------------------------------------------------------------------

def distance_sq(x1: float, y1: float, x2: float, y2: float) -> float:
    dx, dy = x2 - x1, y2 - y1
    return dx * dx + dy * dy


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt(distance_sq(x1, y1, x2, y2))


def normalize(dx: float, dy: float) -> tuple[float, float]:
    length = math.sqrt(dx * dx + dy * dy)
    return (dx / length, dy / length) if length > 0 else (0.0, 0.0)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def angle_lerp(current: float, target: float, t: float) -> float:
    diff = target - current
    while diff > math.pi:  diff -= 2 * math.pi
    while diff < -math.pi: diff += 2 * math.pi
    return current + diff * t


def direction_to(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
    return normalize(x2 - x1, y2 - y1)


def angle_of(dx: float, dy: float) -> float:
    return math.atan2(dy, dx)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


# ---------------------------------------------------------------------------
# Bullet pattern generators
# ---------------------------------------------------------------------------

def spread_directions(base_dx: float, base_dy: float, count: int, total_spread: float) -> list[tuple[float, float]]:
    base_angle = angle_of(base_dx, base_dy)
    step = total_spread / max(count - 1, 1)
    return [
        (math.cos(base_angle + (i - (count - 1) / 2) * step),
         math.sin(base_angle + (i - (count - 1) / 2) * step))
        for i in range(count)
    ]


def ring_directions(count: int, phase: float = 0.0) -> list[tuple[float, float]]:
    step = 2 * math.pi / count
    return [(math.cos(phase + i * step), math.sin(phase + i * step)) for i in range(count)]


def arc_directions(base_dx: float, base_dy: float, count: int, spread: float) -> list[tuple[float, float]]:
    """Like spread_directions but returns full direction tuples."""
    return spread_directions(base_dx, base_dy, count, spread)


# ---------------------------------------------------------------------------
# Collision helpers
# ---------------------------------------------------------------------------

def circles_overlap(ax: float, ay: float, ar: float, bx: float, by: float, br: float) -> bool:
    combined = ar + br
    return distance_sq(ax, ay, bx, by) < combined * combined


def rect_plane_overlap(plane: tuple[float, float, float, float] | None, cx: float, cy: float, size: float) -> bool:
    if plane is None:
        return False
    px, py, pw, ph = plane
    return (px < cx + size and px + pw > cx - size and
            py < cy + size and py + ph > cy - size)


# ---------------------------------------------------------------------------
# Line-of-sight
# ---------------------------------------------------------------------------

def has_line_of_sight(x1: float, y1: float, x2: float, y2: float,
                      nearby_walls: list, step_px: int = 15, probe_size: float = 5.0) -> bool:
    if not nearby_walls:
        return True
    dx, dy = x2 - x1, y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist == 0:
        return True
    steps = max(int(dist / step_px), 3)
    inv = 1.0 / steps
    for i in range(1, steps):
        t = i * inv
        for wall in nearby_walls:
            if wall.collides(x1 + dx * t, y1 + dy * t, probe_size):
                return False
    return True


# ---------------------------------------------------------------------------
# Spawn helpers
# ---------------------------------------------------------------------------

def random_open_position(no_spawn_zones: set[tuple[int, int]], grid_w: int, grid_h: int,
                         tile_size: int, safety_radius: int = 3, border: int = 10,
                         attempts: int = 500) -> tuple[float, float] | None:
    for _ in range(attempts):
        gx = random.randint(border, grid_w - border)
        gy = random.randint(border, grid_h - border)
        if all(
            (gx + dx, gy + dy) not in no_spawn_zones
            for dx in range(-safety_radius, safety_radius + 1)
            for dy in range(-safety_radius, safety_radius + 1)
        ):
            return (gx * tile_size + tile_size // 2, gy * tile_size + tile_size // 2)
    return None


def is_off_screen(sx: float, sy: float, screen_w: int, screen_h: int, margin: int = 0) -> bool:
    return (sx < -margin or sx > screen_w + margin or
            sy < -margin or sy > screen_h + margin)