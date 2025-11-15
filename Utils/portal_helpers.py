"""
Helper functions for Portal animation
"""
import math
import random


def apply_gravity(velocity_y, gravity=0.5):
    """Apply gravity to vertical velocity"""
    return velocity_y + gravity


def apply_friction(velocity, friction=0.98):
    """Apply friction to velocity"""
    return velocity * friction


def rotate_point(x, y, cx, cy, angle):
    """Rotate point (x,y) around center (cx,cy) by angle"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    dx = x - cx
    dy = y - cy
    
    new_x = dx * cos_a - dy * sin_a + cx
    new_y = dx * sin_a + dy * cos_a + cy
    
    return new_x, new_y


def random_color():
    """Generate a random bright color"""
    return (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255)
    )
