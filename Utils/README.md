# Utils Folder

This folder contains reusable utilities and components that can be used across different games.

## Contents

### portal.py
An interactive physics-based animation with cubes and portals.

**Features:**
- Physics simulation with gravity and friction
- Interactive cube spawning
- Portal effects
- Particle systems

**Usage:**
```python
from Utils.portal import PortalAnimation

animation = PortalAnimation(screen)
result = animation.run()
```

**Controls:**
- **Mouse Click**: Interact with cubes
- **ESC**: Exit animation

### portal_helpers.py
Helper functions for physics and animations:
- `apply_gravity()` - Apply gravity to objects
- `apply_friction()` - Apply friction to velocity
- `rotate_point()` - Rotate point around center
- `random_color()` - Generate random bright colors

### textbox.py
A dialogue system with animated character sprites and text effects.

**Features:**
- Animated character sprites (Hero and Wizard)
- Typewriter text effect
- Speaker highlighting with masks
- Dialogue sequences
- Smooth animations and transitions

**Usage:**
```python
from Utils.textbox import Textbox

textbox = Textbox(screen)
result = textbox.run()
```

**Controls:**
- **SPACE**: Advance dialogue / Skip text animation
- **ESC**: Exit dialogue

## Adding New Utilities

When adding new utilities to this folder:

1. Create a new `.py` file with your utility
2. Add documentation at the top of the file
3. Update this README with a description
4. Make sure it's reusable across different games

## Guidelines

- Keep utilities generic and reusable
- Document all functions and classes
- Include usage examples
- Test utilities independently
- Avoid game-specific logic
