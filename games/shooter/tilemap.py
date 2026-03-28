"""
Shooter Game - Tilemap

Responsibilities
----------------
* Store which grid cells are solid tiles.
* Track per-tile metadata (neighbour count, corner flag) used by WallRenderer.
* Procedurally generate a dungeon (rooms + corridors) via MapGenerator.
* Fast tile-level collision check.
* Build and expose the no-spawn-zone set used by the spawner.
"""
from __future__ import annotations

import random


# ---------------------------------------------------------------------------
# Tilemap
# ---------------------------------------------------------------------------

class Tilemap:
    """Sparse grid of solid tiles with renderer metadata."""

    def __init__(self, tile_size: int = 40) -> None:
        self.tile_size = tile_size
        # {(gx, gy): {"neighbor_count": int, "corner": bool}}
        self.tiles: dict[tuple[int, int], dict] = {}

    # ------------------------------------------------------------------
    # Tile manipulation
    # ------------------------------------------------------------------

    def place_tile(self, gx: int, gy: int, *, update: bool = True) -> None:
        self.tiles[(gx, gy)] = {"neighbor_count": 0, "corner": False}
        if update:
            self.update_tiles()

    def remove_tile(self, gx: int, gy: int, *, update: bool = True) -> None:
        self.tiles.pop((gx, gy), None)
        if update:
            self.update_tiles()

    def has_tile(self, gx: int, gy: int) -> bool:
        return (gx, gy) in self.tiles

    def get_all_tiles(self) -> list[tuple[int, int]]:
        return list(self.tiles.keys())

    # ------------------------------------------------------------------
    # Metadata refresh
    # ------------------------------------------------------------------

    def update_tiles(self) -> None:
        """Recompute neighbor_count and corner flag for every tile."""
        new: dict[tuple[int, int], dict] = {}
        for gx, gy in self.tiles:
            n = (
                int((gx,     gy - 1) in self.tiles) +
                int((gx,     gy + 1) in self.tiles) +
                int((gx - 1, gy    ) in self.tiles) +
                int((gx + 1, gy    ) in self.tiles)
            )
            corner = not (
                (gx - 1, gy - 1) in self.tiles and
                (gx + 1, gy - 1) in self.tiles and
                (gx - 1, gy + 1) in self.tiles and
                (gx + 1, gy + 1) in self.tiles
            )
            new[(gx, gy)] = {"neighbor_count": n, "corner": corner}
        self.tiles = new

    # ------------------------------------------------------------------
    # Collision
    # ------------------------------------------------------------------

    def check_collision(self, x: float, y: float, size: float) -> bool:
        """True when a circle at (x, y) with radius size overlaps any tile."""
        gx = int(x // self.tile_size)
        gy = int(y // self.tile_size)
        ts = self.tile_size
        for cgx in range(gx - 1, gx + 2):
            for cgy in range(gy - 1, gy + 2):
                if (cgx, cgy) in self.tiles:
                    tx, ty = cgx * ts, cgy * ts
                    if (x + size > tx and x - size < tx + ts and
                            y + size > ty and y - size < ty + ts):
                        return True
        return False


# ---------------------------------------------------------------------------
# Map generator
# ---------------------------------------------------------------------------

class MapGenerator:
    """
    Fills a Tilemap with a procedurally-generated dungeon.

    Usage::

        tilemap = Tilemap(tile_size=40)
        gen = MapGenerator(tilemap, world_size=18000)
        pixel_rooms, no_spawn_zones = gen.generate()
    """

    def __init__(
        self,
        tilemap: Tilemap,
        world_size: int,
        *,
        num_rooms: int = 30,
        min_room: int = 30,
        max_room: int = 50,
        corridor_hw: int = 7,      # half-width of corridors in tiles
        room_padding: int = 4,
        extra_links: int | None = None,   # None → same as num_rooms
        enforce_passes: int = 3,
    ) -> None:
        self.tilemap = tilemap
        self.world_size = world_size
        self.tile_size = tilemap.tile_size
        self.grid_w = world_size // self.tile_size
        self.grid_h = world_size // self.tile_size

        self.num_rooms = num_rooms
        self.min_room = min_room
        self.max_room = max_room
        self.corridor_hw = corridor_hw
        self.room_padding = room_padding
        self.extra_links = extra_links if extra_links is not None else num_rooms
        self.enforce_passes = enforce_passes

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def generate(self) -> tuple[list[tuple[int, int, int, int]], set[tuple[int, int]]]:
        """
        Run the full pipeline.

        Returns:
            pixel_rooms    – list of (x, y, w, h) in pixel space.
            no_spawn_zones – set of solid grid cells unsafe for spawning.
        """
        tm = self.tilemap
        gw, gh = self.grid_w, self.grid_h

        # 1. Fill everything solid (deferred update)
        for x in range(gw):
            for y in range(gh):
                tm.place_tile(x, y, update=False)

        # 2. Carve rooms
        grid_rooms = self._carve_rooms()

        # 3. Connect rooms with corridors
        self._connect_all(grid_rooms)

        # 4. Remove pencil-thin walls
        self._enforce_thickness(gw, gh)

        # 5. Single bulk metadata refresh
        tm.update_tiles()

        # 6. Convert to pixel space
        ts = self.tile_size
        pixel_rooms = [(x * ts, y * ts, w * ts, h * ts) for x, y, w, h in grid_rooms]

        # 7. Build no-spawn zones (all solid tiles)
        no_spawn = set(tm.tiles.keys())

        return pixel_rooms, no_spawn

    # ------------------------------------------------------------------
    # Room carving
    # ------------------------------------------------------------------

    def _carve_rooms(self) -> list[tuple[int, int, int, int]]:
        tm = self.tilemap
        gw, gh = self.grid_w, self.grid_h
        pad = self.room_padding

        # Large starting room at world centre
        half = 30
        cx, cy = gw // 2, gh // 2
        rooms: list[tuple[int, int, int, int]] = [(cx - half, cy - half, half * 2, half * 2)]

        for _ in range(self.num_rooms):
            for _ in range(50):
                w = random.randint(self.min_room, self.max_room)
                h = random.randint(self.min_room, self.max_room)
                x = random.randint(5, gw - w - 5)
                y = random.randint(5, gh - h - 5)
                if not any(
                    x + w + pad >= rx and x - pad <= rx + rw and
                    y + h + pad >= ry and y - pad <= ry + rh
                    for rx, ry, rw, rh in rooms
                ):
                    rooms.append((x, y, w, h))
                    break

        for x, y, w, h in rooms:
            for rx in range(x, x + w):
                for ry in range(y, y + h):
                    if 0 <= rx < gw and 0 <= ry < gh:
                        tm.remove_tile(rx, ry, update=False)

        return rooms

    # ------------------------------------------------------------------
    # Corridor carving
    # ------------------------------------------------------------------

    def _carve_corridor(
        self,
        r1: tuple[int, int, int, int],
        r2: tuple[int, int, int, int],
    ) -> None:
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
        cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
        hw = self.corridor_hw
        gw, gh = self.grid_w, self.grid_h
        tm = self.tilemap

        for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
            for ow in range(-hw, hw + 1):
                if 0 <= cy1 + ow < gh and 0 <= x < gw:
                    tm.remove_tile(x, cy1 + ow, update=False)

        for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
            for ow in range(-hw, hw + 1):
                if 0 <= cx2 + ow < gw and 0 <= y < gh:
                    tm.remove_tile(cx2 + ow, y, update=False)

    def _connect_all(self, rooms: list[tuple[int, int, int, int]]) -> None:
        for i in range(len(rooms) - 1):
            self._carve_corridor(rooms[i], rooms[i + 1])
        for _ in range(self.extra_links):
            i, j = random.randrange(len(rooms)), random.randrange(len(rooms))
            if i != j:
                self._carve_corridor(rooms[i], rooms[j])

    # ------------------------------------------------------------------
    # Wall thickness enforcement
    # ------------------------------------------------------------------

    def _enforce_thickness(self, gw: int, gh: int) -> None:
        tm = self.tilemap
        for _ in range(self.enforce_passes):
            to_remove: set[tuple[int, int]] = set()
            for x, y in list(tm.tiles):
                left  = not tm.has_tile(x - 1, y)
                right = not tm.has_tile(x + 1, y)
                up    = not tm.has_tile(x, y - 1)
                down  = not tm.has_tile(x, y + 1)

                if (left and right) or (up and down):
                    to_remove.add((x, y))
                    continue

                if left and tm.has_tile(x + 1, y) and not tm.has_tile(x + 2, y):
                    to_remove.update({(x, y), (x + 1, y)})
                if up and tm.has_tile(x, y + 1) and not tm.has_tile(x, y + 2):
                    to_remove.update({(x, y), (x, y + 1)})

            for pos in to_remove:
                tm.remove_tile(*pos, update=False)
            if not to_remove:
                break