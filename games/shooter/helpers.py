"""
Helper functions for Shooter game
"""
import math


def distance(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def normalize_vector(dx, dy):
    """Normalize a 2D vector"""
    length = math.sqrt(dx*dx + dy*dy)
    if length > 0:
        return dx/length, dy/length
    return 0, 0


def lerp(start, end, t):
    """Linear interpolation"""
    return start + (end - start) * t


def check_line_intersection(x1, y1, x2, y2, walls, step_size=20):
    """Check if line between two points intersects any walls"""
    dx = x2 - x1
    dy = y2 - y1
    dist = distance(x1, y1, x2, y2)
    
    if dist == 0:
        return False
    
    steps = int(dist / step_size)
    for i in range(steps):
        t = i / steps
        check_x = x1 + dx * t
        check_y = y1 + dy * t
        
        for wall in walls:
            if wall.collides_with(check_x, check_y, 5):
                return True
    
    return False
