"""
Snake Game - Helper Functions
"""
import random


# ---------------------------------------------------------------------------
# Position / grid helpers
# ---------------------------------------------------------------------------

def generate_random_position(grid_tiles_x, grid_tiles_y, tile_width, tile_height,
                              excluded_positions=None, rng=None):
    """Return a random grid-aligned (x, y) pixel position.

    Args:
        grid_tiles_x: Number of columns in the grid.
        grid_tiles_y: Number of rows in the grid.
        tile_width:   Pixel width of one tile.
        tile_height:  Pixel height of one tile.
        excluded_positions: Iterable of (x, y) positions to avoid.
        rng: Optional random.Random instance (defaults to global random).

    Returns:
        (x, y) pixel position that is not in *excluded_positions*.
    """
    if rng is None:
        rng = random
    excluded = set(excluded_positions) if excluded_positions else set()
    while True:
        x = rng.randint(0, grid_tiles_x - 1) * tile_width
        y = rng.randint(0, grid_tiles_y - 1) * tile_height
        pos = (x, y)
        if pos not in excluded:
            return pos


def check_collision(pos, obstacles):
    """Return True if *pos* is found in *obstacles*.

    Args:
        pos:       (x, y) position to test.
        obstacles: Any collection that supports the ``in`` operator.
    """
    return pos in obstacles


def is_out_of_bounds(pos, width, height):
    """Return True if *pos* lies outside the rectangle [0, width) × [0, height).

    Args:
        pos:    (x, y) pixel position.
        width:  Pixel width of the playfield.
        height: Pixel height of the playfield.
    """
    x, y = pos
    return x < 0 or x >= width or y < 0 or y >= height


# ---------------------------------------------------------------------------
# Wall helpers
# ---------------------------------------------------------------------------

def spawn_wall_block(walls, wall_segments, snake, apple_pos,
                     grid_tiles_x, grid_tiles_y,
                     tile_width, tile_height,
                     width, height, rng=None):
    """Add one wall block to *walls* (and track it in *wall_segments*).

    With 50 % probability the new block extends an existing segment;
    otherwise a brand-new segment is started.  The function modifies
    *walls* and *wall_segments* **in place**.

    Args:
        walls:         List of (x, y) wall positions (modified in place).
        wall_segments: List of lists – each inner list is a connected wall
                       segment (modified in place).
        snake:         Current snake body as a list of (x, y) positions.
        apple_pos:     Current apple position.
        grid_tiles_x / grid_tiles_y: Grid dimensions in tiles.
        tile_width / tile_height:    Tile pixel dimensions.
        width / height:              Playfield pixel dimensions.
        rng: Optional random.Random instance (defaults to global random).
    """
    if rng is None:
        rng = random
    snake_set = set(snake)
    wall_set = set(walls)

    adjacent_dirs = [
        (0,  tile_height),
        (0, -tile_height),
        ( tile_width, 0),
        (-tile_width, 0),
    ]

    if wall_segments and rng.random() < 0.5:
        # Try to extend an existing segment
        segment = rng.choice(wall_segments)
        last_block = segment[-1]
        rng.shuffle(adjacent_dirs)
        for dx, dy in adjacent_dirs:
            new_pos = (last_block[0] + dx, last_block[1] + dy)
            if (0 <= new_pos[0] < width and
                    0 <= new_pos[1] < height and
                    new_pos not in wall_set and
                    new_pos not in snake_set and
                    new_pos != apple_pos):
                walls.append(new_pos)
                segment.append(new_pos)
                return

    # Start a new segment
    for _ in range(50):
        x = rng.randint(0, grid_tiles_x - 1) * tile_width
        y = rng.randint(0, grid_tiles_y - 1) * tile_height
        pos = (x, y)
        if pos not in snake_set and pos not in wall_set and pos != apple_pos:
            walls.append(pos)
            wall_segments.append([pos])
            return


# ---------------------------------------------------------------------------
# Direction helpers
# ---------------------------------------------------------------------------

def opposite_direction(direction):
    """Return the direction vector that is the exact opposite of *direction*."""
    dx, dy = direction
    return (-dx, -dy)


def is_valid_turn(current_direction, new_direction):
    """Return True when *new_direction* is not a 180-degree reversal."""
    return new_direction != opposite_direction(current_direction)