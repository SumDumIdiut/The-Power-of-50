# Shooter

## Objective
Kill 50 enemies to win.

## Controls
| Input             | Action                    |
|-------------------|---------------------------|
| WASD / Arrow Keys | Move                      |
| IJKL              | Manual aim (optional)     |
| Auto-aim          | Targets visible enemies   |
| ESC               | Quit to menu              |

## Gameplay
- Navigate procedurally generated dungeons
- Auto-fire shoots at enemies in line of sight
- **One hit = death** — avoid all enemy contact
- Enemy health and spawn rate scale with your kill count
- Boss enemies appear every 10 kills
- Collect power-up drops to upgrade your weapon

## Power-ups
| Drop        | Effect              |
|-------------|---------------------|
| Fire Rate   | Shoot faster        |
| Multi-Shot  | Fire extra bullets  |
| Damage      | Increase bullet damage |

## Files
| File               | Purpose                              |
|--------------------|--------------------------------------|
| `shooter_game.py`  | Main game logic                      |
| `shooter_save.py`  | Save/load best score                 |
| `tilemap.py`       | Procedural dungeon generation        |
| `wall_renderer.py` | Tile rendering and collision         |
| `helpers.py`       | Math and collision helper functions  |
