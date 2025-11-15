"""
Helper functions for Snake game
"""
import random


def generate_random_position(width, height, cell_size, excluded_positions=None):
    """Generate a random grid position avoiding excluded positions"""
    if excluded_positions is None:
        excluded_positions = []
    
    while True:
        x = random.randint(0, (width // cell_size) - 1) * cell_size
        y = random.randint(0, (height // cell_size) - 1) * cell_size
        pos = (x, y)
        if pos not in excluded_positions:
            return pos


def check_collision(pos, obstacles):
    """Check if position collides with any obstacles"""
    return pos in obstacles


def is_out_of_bounds(pos, width, height):
    """Check if position is outside game bounds"""
    x, y = pos
    return x < 0 or x >= width or y < 0 or y >= height
